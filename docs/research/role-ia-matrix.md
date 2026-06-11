# Role IA Matrix

Date: 2026-06-10

## Matrix

| Role | Primary goal | Default landing page | Navigation model | Core actions | Data objects | Visual density | Mobile priority | Must not show | Reference candidates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Organizer | Run and recover old-district events | /organizer/dashboard | Operations shell with event, exception, review navigation | seed, generate v1, approve v1, inspect trace, manage incidents, approve recovery, review metrics | EventSummary, PlanVersion, AgentTrace, Incident, RecoveryProposal, OperationalMetric | Medium-high | Desktop first | Merchant-only status form, tourist H5 shell | shadcn/ui primary; Ant Design Pro reference; Tremor metrics reference; PagerDuty/Datadog incident pattern |
| Merchant | Execute assigned event tasks and report runtime state | /merchant/dashboard | Lightweight task/status shell | view task, view preparation, report inventory, report queue, report availability, read organizer notices | MerchantTask, MerchantRuntimeState, PublicNotice | Medium | Tablet/mobile first | Organizer approvals, Agent trace, recovery proposal internals | shadcn/ui primary; Shopify POS/Square POS operation pattern; Flowbite mobile component reference |
| User/Tourist | Follow route, read stories, complete tasks, receive notices | /user/events/demo-night-tour | Mobile event route shell | view route, view point story, view task, view notice, understand route changes | PublicEventV2, RoutePoint, PublicNotice | Low-medium | Mobile first | PlanVersion, Incident, RecoveryProposal, internal merchant status | shadcn/ui primary; Luma event-page pattern; Wanderlog/Roadtrippers route pattern |

## Route Ownership

| Route | Owner Role | Login Required | Compatibility Status |
| --- | --- | --- | --- |
| /login | all | no | new |
| /organizer/dashboard | organizer | yes | new |
| /organizer | organizer | yes | compatibility alias |
| /organizer/events/demo-night-tour | organizer | yes | existing route retained |
| /organizer/events/demo-night-tour/exceptions | organizer | yes | existing route retained |
| /organizer/events/demo-night-tour/review | organizer | yes | new |
| /review/demo-night-tour | organizer | yes | compatibility alias |
| /merchant/dashboard | merchant | yes | new |
| /merchant/m001 | merchant | yes | compatibility alias |
| /merchant/events/demo-night-tour/tasks | merchant | yes | new |
| /merchant/events/demo-night-tour/status | merchant | yes | new |
| /merchant/notifications | merchant | yes | new |
| /user/events/demo-night-tour | tourist | yes | new |
| /user/events/demo-night-tour/route | tourist | yes | new |
| /user/events/demo-night-tour/points/rp001 | tourist | yes | new |
| /user/events/demo-night-tour/notices | tourist | yes | new |
| /public/events/demo-night-tour | public | no | existing public route retained |

## Non-Negotiable Separation Rules

- Organizer pages do not inline merchant status controls.
- Organizer pages do not inline tourist H5.
- Merchant pages do not show organizer approval navigation.
- Merchant pages do not show AgentTrace or recovery-proposal internals.
- User pages do not show backend terminology or organizer navigation.
- User pages can mention "route updated" but must not expose `PlanVersion`, `Incident`, or `RecoveryProposal` labels.
- Review center belongs to organizer, not a fourth independent product endpoint.
- Public H5 remains accessible without login, but it must still look like the user/tourist product surface, not an organizer preview card.

## Design Implications

| Role | Shell expectation | Layout implication | Component implication |
| --- | --- | --- | --- |
| Organizer | Command center | Desktop-first content grid, compact status rail, persistent event navigation | Approval queue, incident queue, version diff, trace timeline, metric panels |
| Merchant | Today-work console | Tablet/mobile-first stack, large status actions, minimal navigation | Merchant task cards, runtime status controls, notice feed |
| User/Tourist | Route H5 | Mobile-first route timeline, story cards, notice banners, local context | Route point cards, public notice banner, task prompt, route update indicator |

## Data Exposure Rules

| Object | Organizer | Merchant | User/Tourist |
| --- | --- | --- | --- |
| PlanVersion | Full version and diff | Hidden | Public route version only, rewritten as user language |
| AgentTrace | Full steps | Hidden | Hidden |
| Incident | Full queue and state | Only if tied to merchant report confirmation | Hidden |
| RecoveryProposal | Full proposal and approval | Hidden | Hidden |
| MerchantTask | Full list by merchant | Own tasks only | Related visitor task only |
| MerchantRuntimeState | Full operational visibility | Own state only | Hidden |
| PublicNotice | Draft/publish control | Read-only notice feed | Published notices only |
| OperationalMetric | Full review metrics | Hidden | Hidden |
