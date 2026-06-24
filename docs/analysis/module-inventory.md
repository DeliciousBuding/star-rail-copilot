# Module Inventory — SRC Web Gateway Adapter

## Summary

| Module | Responsibility | Dependencies | Files | Lines | Complexity | S.U.P.E.R Score |
|:-------|:---------------|:-------------|------:|------:|:-----------|:----------------|
| `web_gateway.py` | HTTP client to Go Gateway | requests, PIL, numpy | 1 | ~140 | Low | S🟢 U🟢 P🟢 E🟢 R🟢 |
| Integration points | Register adapter in SRC framework | web_gateway | 7 | +42 | Low | S🟢 U🟢 P🟢 E🟢 R🟢 |

## Module Details

### module/device/method/web_gateway.py
- **Path**: `module/device/method/web_gateway.py`
- **Responsibility**: HTTP client adapter to Go Gateway. Implements SRC device method interface — same signatures as `adb.py`.
- **Public API**: `WebGateway` mixin class with:
  - `screenshot_web_gateway()` → `np.ndarray` (BGR, 1280×720)
  - `click_web_gateway(x, y)` → None
  - `swipe_web_gateway(p1, p2, duration)` → None
  - `long_click_web_gateway(x, y, duration)` → None
  - `app_start()` → None
  - `app_stop()` → None
  - `app_is_running()` → `bool`
  - `web_gateway_release()` → None (cleanup)
- **Internal Dependencies**: None (pure mixin, no SRC module imports beyond base framework)
- **External Dependencies**: `requests`, `PIL`, `numpy`
- **Complexity Rating**: Low
- **S.U.P.E.R Assessment**:
  - **S**: ✅ Single purpose — HTTP client to Gateway
  - **U**: ✅ Unidirectional: SRC calls → HTTP → Gateway response
  - **P**: ✅ Contract: Gateway v1 API (JSON in, JPEG out)
  - **E**: ✅ Gateway URL from config (`Emulator_GatewayUrl`), no hardcoded paths
  - **R**: ✅ Replaceable: swap Gateway with any backend implementing same v1 API

### Integration Points (7 modified files)

| File | Change | Lines | Purpose |
|:-----|:-------|------:|:--------|
| `config/argument/argument.yaml` | Options | +3/-1 | Add WebGateway to ScreenshotMethod and ControlMethod enums |
| `config/config_generated.py` | Defaults | +3/-1 | Add `Emulator_GatewayUrl` config key |
| `connection_attr.py` | Guard | +13/-2 | `is_web_gateway` property; skip ADB init when serial is `'web_gateway'` |
| `connection.py` | Lifecycle | +5 | Early return in `__init__`; release hook |
| `screenshot.py` | Registration | +4/-1 | Import WebGateway; register `screenshot_web_gateway` in dict |
| `control.py` | Dispatch | +10/-2 | Import WebGateway; dispatch in click/long_click/swipe |
| `device.py` | Validation | +10 | `method_check` guard: paired screenshot/control enforcement |

All changes follow existing SRC patterns (same as `nemu_ipc`, `scrcpy`, `MaaTouch` registrations).

### Design Compliance
- **Forbidden terms absent**: No `cdp`, `chrome`, `playwright`, `cloud_game`, `mjpeg`, `websocket` in SRC code
- **Mixin pattern**: No `__init__`, uses `cached_property` for lazy HTTP session
- **Error semantics**: All HTTP errors wrapped as `GameNotRunningError` (same as ADB errors)
- **Coordinate contract**: Screenshot returns 1280×720 BGR; coordinates in screenshot pixel space
