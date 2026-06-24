# Risk Assessment — SRC Web Gateway Adapter

## S.U.P.E.R Architecture Health Summary

| Principle | Status | Key Findings | Priority |
|:----------|:-------|:-------------|:---------|
| **S** Single Purpose | 🟢 | web_gateway.py does one thing: HTTP client to Gateway. Integration points follow existing dispatch patterns. | — |
| **U** Unidirectional Flow | 🟢 | SRC → web_gateway → HTTP → Gateway. No reverse dependencies. | — |
| **P** Ports over Implementation | 🟢 | Gateway v1 API is the contract. Adapter never touches CDP/Chrome. | — |
| **E** Environment-Agnostic | 🟢 | Gateway URL from config. Same code works with local or remote Gateway. | — |
| **R** Replaceable Parts | 🟢 | Swap Gateway backend without touching SRC. Swap SRC device method without touching Gateway. | — |

**Overall Health**: _5/5 principles healthy_ — Clean architecture

## Risk Matrix

| Risk | Impact | Likelihood | Severity | Mitigation |
|:-----|:-------|:-----------|:---------|:-----------|
| Gateway unreachable | High | Medium | High | All HTTP errors wrapped as `GameNotRunningError`; SRC framework handles this gracefully |
| Coordinate mismatch | High | Low | Medium | Fixed 1280×720 contract; should verify via `/api/v1/device/info` at startup (deferred) |
| Cookie expiration | High | Low | Medium | Gateway handles session; SRC adapter is stateless |
| Network latency impacts FPS | Medium | Medium | Medium | SRC screenshot timer enforces min interval; Gateway streams at configurable FPS |
| `requests` not in requirements | Low | Low | Low | `requests` already a transitive dependency of SRC (via adbutils) |

## Technical Debt
- Coordinate contract not verified at startup (should call `/api/v1/device/info`)
- Screenshot query params (`format`, `quality`) sent but Gateway currently ignores them (uses server-level config)
- No end-to-end test of SRC → Gateway → Chrome pipeline

## Testing Risks
- No automated tests for the adapter
- No CI pipeline
- End-to-end validation requires running Gateway + Chrome + cloud game auth
- Manual verification: `python -c "import ast; ast.parse(...)"` for syntax check

## Project Governance Risks
- No AGENTS.md or CLAUDE.md in this repo
- Upstream PR strategy not yet defined (current branch: `feat/web-gateway-device`)
- `tmp/` directory contains debug screenshots (not committed, gitignored)
