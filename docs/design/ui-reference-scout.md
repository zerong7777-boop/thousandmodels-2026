# UI Reference Scout: 智引濠江 MVP

版本：v0.1  
日期：2026-06-07  
任务：`20260518-thousandmodels-ai-competition`  
项目根目录：`<PROJECT_ROOT>`

## Baseline Path

当前 MVP 已锁定为旧区文旅活动编排 Agent，而不是游客向的普通推荐 App。前端展示需要服务现场演示：

- 主办方后台：活动创建、方案审阅、商户执行包、异常恢复、审计记录、复盘报告。
- 商户端：查看执行包，更新库存和排队状态。
- 游客 H5：查看路线、商户优惠、打卡任务和临时通知。

现有 `docs/proposal/implementation-plan.md` 已选择 React + Vite + TypeScript，但 Task 6 仍偏向手写 CSS 和基础页面。这个方向可运行，但展示质感和组件一致性不足。

## Candidate Insertion Points

- `docs/proposal/implementation-plan.md`
  - 顶部 `Tech Stack` 增加 `antd`。
  - `Decisions Locked By This Plan` 明确前端使用 Ant Design 组件库，而不是整套 Ant Design Pro 脚手架。
  - Task 1 的 `apps/web/package.json` 依赖加入 `antd`。
  - Task 6 替换为 Ant Design 版前端实施任务。
- `apps/web/src/`
  - 后续实现时使用 `ConfigProvider`、`Layout`、`Menu`、`Steps`、`Form`、`Table`、`Timeline`、`Card`、`Tag`、`Alert`、`Modal`、`Descriptions`、`Statistic` 等组件。
  - 保留 `lucide-react`，用于按钮和工具类图标。

## Recommended Plan

推荐路线：React + Vite + TypeScript + Ant Design 组件库。

原因：

- 与“主办方后台 / Dashboard / 审批流 / 表格 / 状态标签 / 时间线”的产品形态匹配。
- 组件覆盖度高，能快速做出专业、稳定、可扫描的后台界面。
- 不需要引入 Umi、复杂路由、权限系统或整套模板结构，能控制 MVP 范围。
- 与现有 FastAPI 后端计划兼容，前端只通过 `/api` 调接口。

视觉方向：

- 主办方后台应是安静、密集但清晰的运营工具，不做营销落地页。
- 第一屏直接展示“活动编排 Agent 工作台”，不要 hero 页面。
- 信息组织优先级：活动状态 -> Agent 方案 -> 商户执行包 -> 异常恢复 -> 审计与复盘。
- 使用澳门旧区主题色做轻量 token，而不是大面积单色背景。建议：深墨绿/石板灰作为导航，胭脂红或金色作为状态强调，页面主体保持浅灰白。
- 卡片只用于独立信息块，不做卡片套卡片。
- 所有对外更新和导流调整必须有“主办方确认”按钮或状态。

## Rejected Options

### 1. 直接克隆 Ant Design Pro

Ant Design Pro 是成熟的企业应用脚手架，包含 dashboard、form、list、profile、exception、account、AI assistant 等模板，并基于 Umi/Ant Design 生态。它适合作参考布局和页面类型，但对本 MVP 过重。

不直接采用的原因：

- 会引入 Umi、模板路由、权限、账户等非 MVP 需求。
- 容易把时间消耗在删减模板，而不是完成活动编排闭环。
- 评委更关心 Agent 流程和可演示能力，不需要完整企业后台骨架。

### 2. 直接采用 shadcn-admin

shadcn-admin 的视觉更现代，且基于 Vite + TypeScript，但它通常伴随 Tailwind、Radix、TanStack Router/Query、Zod、React Hook Form 等配置。

不作为主路线的原因：

- 对当前 MVP 来说配置面更大。
- 后台表格、时间线、审批流等常用企业组件需要更多拼装。
- 如果后续要做高定制视觉，可在 Ant Design MVP 稳定后再局部借鉴。

### 3. 把 design-spells 当成主 UI 框架

`design-spells` 主要是微交互和设计细节清单，适合在功能稳定后做按钮动效、hover 状态、加载反馈等 polish。

不作为主路线的原因：

- 它不是组件库，也不是 dashboard 模板。
- 第一阶段需要稳定、清楚、可演示的后台体验，不能让微交互干扰审批流和状态流。

## Risks / Unknowns

- Ant Design 组件能快速提质，但仍需要定制信息层级，否则会变成普通后台模板。
- 如果后续强行加入地图、账号权限、真实商户系统，会超过 MVP 范围。
- 若接入 Qwen/QwenPaw 后响应不稳定，前端必须能展示 deterministic fallback 结果。
- 游客 H5 不应照搬后台组件密度，应单独做移动端可读布局。

## Implementation Handoff

后续实现时按以下原则执行：

1. 不克隆整套模板。
2. 安装 `antd`，保留 `lucide-react`。
3. 用 Ant Design 的 `ConfigProvider` 定义项目 token。
4. 主办方页使用 `Layout + Steps + Form + Table + Timeline + Alert + Modal` 完成闭环。
5. 商户端和游客端做轻量页面，不增加登录和真实权限系统。
6. 页面必须支持 3-5 分钟演示路径：生成方案 -> 确认 -> 查看执行包 -> 触发异常 -> 确认恢复 -> 游客端更新 -> 复盘。
7. 完成前用桌面和窄屏视口做截图或手动 UI 检查，避免文字溢出和状态重叠。

## Sources

- Ant Design: https://github.com/ant-design/ant-design
- Ant Design components overview: https://ant.design/components/overview
- Ant Design Pro: https://github.com/ant-design/ant-design-pro
- shadcn/ui: https://github.com/shadcn-ui/ui
- shadcn-admin: https://github.com/rohitsoni007/shadcn-admin
- design-spells: https://github.com/sickn33/antigravity-awesome-skills/tree/main/skills/design-spells
