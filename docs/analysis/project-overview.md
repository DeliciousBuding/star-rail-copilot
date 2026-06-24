# Project Overview — SRC Web Gateway Adapter

## Preliminary Direction
Add a clean HTTP client device method (`web_gateway.py`) to the SRC/ALAS framework, enabling cloud gaming via an external Go Gateway instead of Android emulator + ADB.

## Current Architecture

```
SRC Framework (Python, upstream: LmeSzinc/StarRailCopilot)
├── Device abstract layer (MRO: Device → Screenshot + Control + AppControl)
│   ├── adb.py              — Android ADB (upstream)
│   ├── scrcpy.py           — scrcpy video stream (upstream)
│   ├── nemu_ipc.py         — MuMu emulator IPC (upstream)
│   └── web_gateway.py      — HTTP client to Go Gateway (NEW)
└── Task engine, OCR, template matching (100% unchanged)
```

- **SRC**: Upstream fork at [DeliciousBuding/star-rail-copilot](https://github.com/DeliciousBuding/star-rail-copilot), branch `feat/web-gateway-device`
- **Gateway**: [DeliciousBuding/webdeck](https://github.com/DeliciousBuding/webdeck) — Go CDP Gateway
- **Protocol**: HTTP — SRC adapter calls Gateway's `/api/v1/*` endpoints

## Technology Stack

| Layer | Technology | Notes |
|:------|:-----------|:------|
| Core engine | Python 3.10 (SRC upstream) | Scheduler, OCR, template matching |
| Device method | `requests.Session` (stdlib) | HTTP client to Gateway |
| Gateway | Go + chromedp | Chrome CDP control |
| Deployment | Docker (Gateway) + Python (SRC) | Separate containers/image |

## Entry Points

The adapter (`web_gateway.py`) provides these methods to the SRC framework:

| Method | Gateway Endpoint | Returns |
|:-------|:-----------------|:--------|
| `screenshot_web_gateway()` | `GET /api/v1/device/screenshot` | `np.ndarray` BGR 1280×720 |
| `click_web_gateway(x, y)` | `POST /api/v1/input/tap` | None |
| `swipe_web_gateway(p1, p2)` | `POST /api/v1/input/swipe` | None |
| `long_click_web_gateway(x, y, duration)` | `POST /api/v1/input/swipe` | None |
| `app_start()` | `POST /api/v1/app/start` | None |
| `app_stop()` | `POST /api/v1/app/stop` | None |
| `app_is_running()` | `GET /api/v1/health` | `bool` |

## Integration Points (7 files, +42/-8 lines)

| File | Change | Lines |
|:-----|:-------|------:|
| `module/device/method/web_gateway.py` | **New** — HTTP adapter (~140 lines) | +140 |
| `module/config/argument/argument.yaml` | Add WebGateway to ScreenshotMethod/ControlMethod options | +3/-1 |
| `module/config/config_generated.py` | Add GatewayUrl default | +3/-1 |
| `module/device/connection_attr.py` | Add `is_web_gateway` guard, skip ADB init | +13/-2 |
| `module/device/connection.py` | Early return + release hook | +5 |
| `module/device/screenshot.py` | Import + register in `screenshot_methods` | +4/-1 |
| `module/device/control.py` | Import + dispatch in click/long_click/swipe | +10/-2 |
| `module/device/device.py` | `method_check` guard (WebGateway paired enforcement) | +10 |

## Build & Run

```bash
# SRC (this repo)
pip install -r requirements.txt
# Set config: Emulator_Serial = 'web_gateway'
# Set config: Emulator_ScreenshotMethod = 'WebGateway'
# Set config: Emulator_ControlMethod = 'WebGateway'
python src.py

# Gateway (separate repo)
cd webdeck
go build -o webdeck ./cmd/gateway/
./webdeck --auth cloud_auth.json
```

## Design Principles
- **Zero references** to `cdp`, `chrome`, `playwright`, `cloud_game`, `mjpeg`, `websocket` in SRC code
- **Same interface** as `adb.py` — SRC task logic unchanged
- **Pure mixin** — no `__init__`, uses `cached_property` for HTTP session
- **Gateway is Virtual Device Runtime** — not a Playwright wrapper

## External Integrations
- **Go Gateway**: HTTP/JSON over `/api/v1/*` endpoints
- **SRC Framework**: Mixin registered via `screenshot_methods` and `click_methods` dicts
