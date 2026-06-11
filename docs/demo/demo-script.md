# 智引濠江 MVP Demo Script

## 3-5 Minute Demo

1. Open organizer backend at `http://127.0.0.1:5173`.
2. Click `生成活动方案`.
3. Show generated theme, route, schedule, merchants, budget, and risk plan.
4. Click `主办方确认方案`.
5. Show merchant execution packs.
6. Open `游客 H5` and refresh the tourist route page.
7. Trigger `库存不足`.
8. Show Recovery Agent recommendations.
9. Click `主办方确认调整`.
10. Refresh `游客 H5` and show updated temporary notice.
11. Trigger `强降雨` to show the second recovery path.
12. Generate review report and show lessons learned.

## Key Message

This is not a tourist chatbot. It is an old-district event orchestration Agent that connects organizers, merchants, visitor touchpoints, runtime recovery, approval boundaries, and post-event review.

## Fallback

If the external model environment is unavailable, keep `AGENT_BACKEND=deterministic`. The demo still runs without `DASHSCOPE_API_KEY`.
