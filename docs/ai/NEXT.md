# NEXT

## Recommended Next Step

Start a v1.3 live demo hardening phase.

v1.2 now has the event-page and merchant-edge loop in place: backend contracts, frontend exposure, mocked visual smoke, screenshots, and verification all pass. The next gap is not another UI feature; it is demo credibility under a real local run:

- Add a live FastAPI + Vite route smoke with real demo login, not only mocked Playwright API responses.
- Create a short operator demo script for the v1.2 loop: organizer publish -> merchant package -> sold-out update -> operation suggestion -> public Event Page -> review.
- Decide whether to keep regenerated historical screenshots or clean them before the next commit.
- Re-run the optional Qwen live smoke only through process environment credentials, then record whether it is success or blocked without storing any key.
- Convert the v1.2 loop into competition-facing material: architecture diagram, Agent capability evidence list, and slide-ready screenshots.

## Do Not Do Yet

- Do not make Qwen or DashScope required for the demo.
- Do not claim QwenPaw workflow orchestration until it is implemented and verified.
- Do not let model output approve plans, publish notices, mutate merchant state, create coupon/redemption authority, or create route versions.
- Do not expose raw model/backend terms on merchant, tourist, or public H5 pages.
- Do not use v1.1 live screenshot paths while the smoke outcome remains `blocked`.
- Do not start real merchant, hardware, POS, payment, map, weather, or traffic integrations.
- Do not run backend pytest in parallel against the default SQLite database; use serial runs or isolated database paths.
