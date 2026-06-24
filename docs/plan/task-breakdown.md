# Task Breakdown — SRC Web Gateway Adapter

## Overview
- **Total Phases**: 2
- **Total Tasks**: 7
- **Estimated Total Effort**: S
- **Status**: Phase 1 ✅ | Phase 2 ✅

## S.U.P.E.R Design Constraints

- **S**: web_gateway.py does exactly one thing — HTTP client to Gateway
- **U**: Data flows: SRC framework → adapter → HTTP → Gateway; no reverse dependencies
- **P**: Gateway v1 API is the contract; adapter never touches CDP/Chrome/Playwright
- **E**: Gateway URL from config (`Emulator_GatewayUrl`); same code for local/remote Gateway
- **R**: Swappable: replace Gateway with any v1 API backend; replace adapter with any HTTP client

## Testing and Governance Constraints

- Current test exemption: adapter is ~140 lines of HTTP glue — manual validation via syntax check
- Future: integration test with running Gateway instance

## Phase 1: Clean Reset & Adapter ✅
**Goal**: Reset SRC repo to upstream, create clean feature branch, write web_gateway.py adapter
**S.U.P.E.R Focus**: P — define the contract before implementation; R — same interface as adb.py

| # | Task | Priority | Effort | Depends | Status |
|:--|:-----|:---------|:-------|:--------|:-------|
| S1 | Reset to upstream/master, create `feat/web-gateway-device` branch | P0 | S | — | ✅ |
| S2 | Write `module/device/method/web_gateway.py` (~140 lines HTTP client) | P0 | S | S1 | ✅ |
| S3 | Integrate into SRC: 7 files, +42/-8 lines (config, connection, screenshot, control, device) | P0 | S | S2 | ✅ |
| S4 | Commit with clean message, push branch | P0 | S | S3 | ✅ |

## Phase 2: Review & Quality Fixes ✅
**Goal**: Fix review findings, enforce design constraints
**S.U.P.E.R Focus**: E — remove any hardcoded references; P — consistent error semantics

| # | Task | Priority | Effort | Depends | Status |
|:--|:-----|:---------|:-------|:--------|:-------|
| S5 | Fix _gw_post error wrapping (was raw re-raise, now GameNotRunningError) | P1 | S | — | ✅ |
| S6 | Fix _gw_health to reuse _gw_get (was duplicating HTTP logic) | P2 | S | — | ✅ |
| S7 | Remove unused `import time`, fix app_stop logging, add tmp/ to gitignore | P1 | S | — | ✅ |
| S8 | Delete old `feat/playwright` branch, remove `config/playwright.json` | P2 | S | — | ✅ |
| S9 | Remove "CDP" from module docstring | P2 | S | — | ✅ |
