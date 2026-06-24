"""
Web Gateway device method for SRC/ALAS framework.

HTTP client adapter to webdeck (Go Gateway). Replaces ADB with
browser-based cloud gaming via Gateway's v1 stable API.

SRC-native pattern:
  - Pure mixin (no __init__) — like Adb, Scrcpy, NemuIpc
  - Lazy init via cached_property — like scrcpy._scrcpy_server_stream
  - Browser lifecycle via del_cached_property — like nemu_ipc.nemu_ipc_release()

Usage:
  1. Set config: Emulator_Serial = 'web_gateway'
  2. Set config: Emulator_ScreenshotMethod = 'WebGateway'
  3. Set config: Emulator_ControlMethod = 'WebGateway'
  4. Gateway URL defaults to http://127.0.0.1:8090
     Override via config: Emulator_GatewayUrl = 'http://gateway:8090'
"""

import io

import numpy as np
from PIL import Image

from module.base.decorator import cached_property, del_cached_property
from module.base.timer import Timer
from module.exception import GameNotRunningError
from module.logger import logger


class WebGateway:
    """SRC Device method — HTTP client to webdeck. Same interface as adb.py.

    This is a MIXIN class. It must NOT have __init__.
    It relies on self.config being set by ConnectionAttr before any method is called.
    """

    # --- Gateway URL ---

    @cached_property
    def _gateway_url(self) -> str:
        return getattr(self.config, 'Emulator_GatewayUrl', 'http://127.0.0.1:8090')

    # --- HTTP session (lazy, cached) ---

    @cached_property
    def _gateway_session(self):
        import requests
        s = requests.Session()
        s.headers['User-Agent'] = 'SRC-WebGateway/1.0'
        self._verify_coordinates(s)
        return s

    def _verify_coordinates(self, session):
        """Verify Gateway reports 1280×720 before any screenshots are taken."""
        try:
            r = session.get(
                f"{self._gateway_url}/api/v1/device/info", timeout=10
            )
            r.raise_for_status()
            info = r.json()
            w, h = info.get('width'), info.get('height')
            if w != 1280 or h != 720:
                raise RuntimeError(
                    f"Gateway resolution mismatch: expected 1280×720, got {w}×{h}"
                )
            logger.info(f"Gateway coordinate contract verified: {w}×{h}")
        except Exception as e:
            logger.error(f"Coordinate verification failed: {e}")
            raise GameNotRunningError(
                f"Gateway coordinate contract failed: {e}"
            ) from e

    def _gateway_release(self):
        if '_gateway_session' in self.__dict__:
            self.__dict__['_gateway_session'].close()
            del self.__dict__['_gateway_session']

    # --- API helpers ---

    def _gw_get(self, path, **params):
        url = f"{self._gateway_url}{path}"
        try:
            r = self._gateway_session.get(url, params=params, timeout=10)
            r.raise_for_status()
            return r
        except Exception as e:
            logger.error(f"Gateway GET {path}: {e}")
            raise GameNotRunningError(f"Gateway unreachable: {e}") from e

    def _gw_post(self, path, data=None):
        url = f"{self._gateway_url}{path}"
        try:
            r = self._gateway_session.post(url, json=data, timeout=10)
            r.raise_for_status()
            return r
        except Exception as e:
            logger.error(f"Gateway POST {path}: {e}")
            raise GameNotRunningError(f"Gateway unreachable: {e}") from e

    def _gw_health(self):
        try:
            return self._gw_get('/api/v1/health').json()
        except Exception:
            return {"ok": False, "state": "UNREACHABLE"}

    # ------------------------------------------------------------------
    # Screenshot method (registered in Screenshot.screenshot_methods)
    # ------------------------------------------------------------------

    _web_gateway_screenshot_timer = Timer(0.1)

    def screenshot_web_gateway(self):
        """
        Take a screenshot via Gateway HTTP API.
        Returns: np.ndarray (H, W, 3) in BGR format (matching cv2 convention).
        """
        self._web_gateway_screenshot_timer.wait()
        self._web_gateway_screenshot_timer.reset()

        r = self._gw_get('/api/v1/device/screenshot', format='jpeg', quality=75)
        img = Image.open(io.BytesIO(r.content))
        img = img.convert('RGB')
        arr = np.array(img)
        # RGB → BGR (OpenCV convention)
        arr = arr[:, :, ::-1].copy()
        return arr

    # ------------------------------------------------------------------
    # Control methods (registered in Control.click_methods / swipe dispatch)
    # ------------------------------------------------------------------

    def click_web_gateway(self, x: int, y: int):
        """Tap at game coordinates (1280x720 logical)."""
        self._gw_post('/api/v1/input/tap', {'x': x, 'y': y})

    def swipe_web_gateway(self, p1: tuple, p2: tuple, duration: float = 0.3):
        """Swipe from p1 to p2."""
        x1, y1 = int(p1[0]), int(p1[1])
        x2, y2 = int(p2[0]), int(p2[1])
        duration_ms = int(duration * 1000)
        self._gw_post('/api/v1/input/swipe', {
            'x1': x1, 'y1': y1,
            'x2': x2, 'y2': y2,
            'duration_ms': duration_ms,
        })

    def long_click_web_gateway(self, x: int, y: int, duration: float = 1.0):
        """Long press via extended swipe at single point."""
        duration_ms = int(duration * 1000)
        self._gw_post('/api/v1/input/swipe', {
            'x1': x, 'y1': y,
            'x2': x, 'y2': y,
            'duration_ms': duration_ms,
        })

    # ------------------------------------------------------------------
    # App control
    # ------------------------------------------------------------------

    def app_start(self):
        """Navigate to cloud game and enter gameplay."""
        self._gw_post('/api/v1/app/start')

    def app_stop(self):
        """Stop game session."""
        try:
            self._gw_post('/api/v1/app/stop')
        except Exception as e:
            logger.warning(f"Gateway app_stop failed: {e}")

    def app_is_running(self) -> bool:
        """Check if Gateway reports healthy state."""
        h = self._gw_health()
        return h.get('ok', False) and h.get('state') == 'RUNNING'

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def web_gateway_release(self):
        """Release HTTP session. Called via release_resource()."""
        self._gateway_release()
        logger.info("WebGateway released")
