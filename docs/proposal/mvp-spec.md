# 智引濠江 MVP Spec

版本：v0.1  
日期：2026-06-07  
任务：`20260518-thousandmodels-ai-competition`  
项目根目录：`<PROJECT_ROOT>`  
状态：MVP 规格草案，供 implementation plan 使用

## 1. 项目定位

“智引濠江”不是面向游客的普通旅游推荐 App，也不是单次海报/文案生成器。MVP 定位为：

> 面向旧区文旅活动主办方的 AI 活动编排 Agent 原型。

系统要证明 AI Agent 能把一次澳门旧区文旅活动从“活动目标”推进到“可执行方案”，并在活动执行中根据商户和天气状态做动态调整，最后生成复盘报告。

MVP 的目标不是做完整城市级 SaaS，而是做一条可稳定演示、可解释、可验证的闭环。

## 2. 官方评分映射

本 MVP 必须显式服务官方五项评分：

| 官方维度 | MVP 对应设计 |
| --- | --- |
| 任务完成度 30% | 从活动创建到方案生成、商户执行包、游客 H5、异常恢复、复盘报告的完整闭环 |
| 智能体能力 20% | 多 Agent 分工、任务拆解、工具调用、结构化输出、多步执行、失败恢复 |
| 应用创新 20% | 不做泛旅游推荐，转向旧区活动组织与商户协同，贴合澳门旧区活化 |
| 实践文章 20% | 可写清楚问题定义、系统架构、Agent 工作流、MVP 案例、伦理边界 |
| 现场表现 10% | 3-5 分钟可演示核心链路，10 分钟路演可讲清方案限制和扩展 |

## 3. MVP 场景

### 3.1 固定片区

福隆新街 - 新马路 - 内港。

### 3.2 固定活动

周末旧区夜游。

### 3.3 活动主题

美食 + 文化故事 + 打卡互动。

### 3.4 模拟商户

8-12 个模拟商户，覆盖：

- 老字号糕点店
- 咖啡店
- 文创店
- 茶餐厅
- 手信店
- 小型展陈空间
- 室内备用休息点
- 可选打卡点

### 3.5 固定异常

MVP 只做两个异常：

- 商户库存不足
- 天气突变为强降雨

这两个异常必须能通过可控按钮或 mock API 触发，确保现场演示稳定。

## 4. 用户角色

### 4.1 主办方

政府部门、旅游机构、社区组织、商会或活动承办方。  
主办方负责创建活动、审核 AI 方案、确认动态调整、查看复盘报告。

### 4.2 商户

旧区小商户。  
商户负责确认参与活动、填写或更新商户状态、查看自己的活动执行包。

### 4.3 游客

活动参与者。  
游客通过二维码或 H5 页面查看路线、文化故事、商户优惠、打卡任务和临时通知。

## 5. 核心闭环

MVP 必须完整跑通以下链路：

1. 主办方创建“周末旧区夜游”活动。
2. 系统解析输入，生成结构化 `EventBrief`。
3. 总策划 Agent 调度子 Agent，生成 `EventPlan`。
4. 主办方查看并确认活动方案。
5. 系统为每个商户生成 `MerchantExecutionPack`。
6. 系统生成游客 H5 页面。
7. 活动运行中，主办方在 Dashboard 查看状态。
8. 触发“库存不足”或“天气突变”异常。
9. Recovery Agent 生成 `RecoveryAction`。
10. 主办方确认调整。
11. 游客 H5 和商户执行状态同步更新。
12. 活动结束后生成 `ReviewReport`。

## 6. MVP 非目标

以下内容不进入第一版 MVP：

- 不接真实商户生产系统。
- 不做真实 POS、CRM 或库存系统集成。
- 不做真实客流预测模型。
- 不做模型训练或微调。
- 不做 AI 眼镜、IoT、机器人或任何硬件。
- 不做完整游客 App。
- 不做多城市、多片区、多活动并发管理。
- 不要求真实地图 API；可用静态点位和规则距离。
- 不要求真实天气 API；可用 mock 天气工具。
- 不将实时状态写入长期 RAG 知识库。

## 7. 工程模块

### 7.1 活动创建模块

职责：让主办方输入活动目标，并转换为结构化任务。

输入：

- 活动区域
- 活动日期与时段
- 预算范围
- 目标客群
- 活动目标
- 偏好主题
- 限制条件

输出：

- `EventBrief`

页面：

- 主办方后台的活动创建表单

验收：

- 用户能用自然语言或表单创建活动。
- 系统能展示解析后的结构化字段。

### 7.2 Agent 编排模块

职责：总策划 Agent 接收 `EventBrief`，调度专业子 Agent，生成完整活动方案。

包含：

- 城市活动总策划 Agent
- 文化叙事 Agent
- 路线规划 Agent
- 商户匹配 Agent
- 营销内容 Agent
- 风险分析 Agent

输出：

- `EventPlan`
- Agent 调用记录
- 每个模块的结构化结果

验收：

- 能看到任务被拆解为多个 Agent 子任务。
- 每个 Agent 输出不是纯文本，而是结构化对象或可渲染模块。

### 7.3 商户数据模块

职责：管理 MVP 内的模拟商户档案和运行状态。

输入：

- 初始 mock 商户数据
- 商户端状态更新
- 异常触发状态

输出：

- `MerchantProfile`
- `MerchantRuntimeState`

验收：

- 至少有 8 个商户。
- 每个商户有类型、地址/点位、容量、营业时间、特色、参与限制、雨天适配度。
- 库存和排队状态可以被更新。

### 7.4 活动方案生成模块

职责：把 Agent 输出整理成主办方可审阅的活动策划方案。

输出内容：

- 活动主题
- 核心叙事
- 路线方案
- 时间表
- 推荐商户与角色分配
- 预算拆分
- 宣传文案
- 风险预案
- 执行清单

验收：

- 主办方可以在一个页面看到完整方案。
- 方案能被局部重生成或标记为已确认。

### 7.5 商户执行包模块

职责：为每个参与商户生成可执行任务。

输出：

- `MerchantExecutionPack`

内容：

- 商户在活动中的角色
- 推荐互动形式
- 导流时段
- 准备物料
- 宣传文案
- 优惠建议
- 异常处理提示

验收：

- 每个商户都有不同的执行包。
- 执行包能体现商户特色，而不是模板套话。

### 7.6 游客 H5 模块

职责：生成轻量游客入口，用于演示对外发布效果。

页面内容：

- 活动介绍
- 路线节点
- 站点文化故事
- 商户优惠
- 打卡任务
- 临时通知

验收：

- 游客端不要求登录。
- 能展示路线和站点。
- 动态调整后，游客端能看到更新通知。

### 7.7 实时状态 / Dashboard 模块

职责：展示活动运行状态和异常事件。

展示内容：

- 商户库存状态
- 商户排队状态
- 天气状态
- 路线风险
- 当前异常
- Agent 建议
- 主办方待确认动作

验收：

- 主办方能看到活动状态变化。
- 异常触发后能看到 Recovery Agent 的建议。

### 7.8 异常触发与动态恢复模块

职责：处理库存不足和天气突变。

输入：

- `MerchantRuntimeState`
- mock 天气状态
- 当前 `EventPlan`

输出：

- `RecoveryAction`

动作类型：

- 降低某商户导流权重
- 替换备用商户
- 切换雨天路线
- 更新游客通知
- 更新商户执行包
- 请求主办方确认

验收：

- 库存不足异常能触发替代商户和游客通知。
- 天气突变异常能触发雨天路线和室内点位。
- 对外发布前必须经过主办方确认。

### 7.9 复盘报告模块

职责：活动结束后生成复盘报告。

输入：

- `EventPlan`
- `AuditLog`
- 商户状态变化
- 异常处理记录
- 游客 H5 mock 访问/打卡数据

输出：

- `ReviewReport`

报告内容：

- 活动摘要
- 路线表现
- 商户表现
- 异常处理过程
- 预算执行概览
- 下次优化建议
- 可沉淀经验

验收：

- 复盘报告能从活动日志生成。
- 报告能说明哪些调整有效，哪些是下次风险。

### 7.10 审计与人工确认模块

职责：保留人机协同和责任边界。

记录内容：

- Agent 调用
- 工具调用
- 方案版本
- 人工修改
- 人工确认
- 异常触发
- 对外发布动作

验收：

- 任何游客端更新或导流调整都有确认记录。
- 实践文章中可以直接引用该模块说明 AI 伦理和责任边界。

## 8. 核心数据对象

### 8.1 EventBrief

字段建议：

- `event_id`
- `area`
- `date`
- `time_window`
- `budget_mop`
- `target_audience`
- `event_goal`
- `theme_preferences`
- `constraints`
- `priority_rules`

### 8.2 EventPlan

字段建议：

- `event_id`
- `theme`
- `narrative`
- `route`
- `schedule`
- `merchant_assignments`
- `budget_plan`
- `marketing_content`
- `risk_plan`
- `execution_checklist`
- `version`
- `approval_status`

### 8.3 MerchantProfile

字段建议：

- `merchant_id`
- `name`
- `type`
- `location`
- `opening_hours`
- `capacity_level`
- `signature_products`
- `story`
- `suitable_activity_types`
- `rainy_day_score`
- `night_score`
- `constraints`

### 8.4 MerchantRuntimeState

字段建议：

- `merchant_id`
- `inventory_status`
- `queue_status`
- `available_for_visitors`
- `temporary_note`
- `updated_at`

### 8.5 MerchantExecutionPack

字段建议：

- `merchant_id`
- `event_id`
- `role`
- `time_slot`
- `visitor_task`
- `preparation_items`
- `promo_text`
- `fallback_instruction`

### 8.6 RecoveryAction

字段建议：

- `action_id`
- `event_id`
- `trigger_type`
- `trigger_detail`
- `recommended_changes`
- `affected_merchants`
- `tourist_notification`
- `merchant_notification`
- `requires_approval`
- `approval_status`

### 8.7 ReviewReport

字段建议：

- `event_id`
- `summary`
- `route_result`
- `merchant_result`
- `incident_summary`
- `agent_actions`
- `human_approvals`
- `lessons_learned`
- `next_event_recommendations`

### 8.8 AuditLog

字段建议：

- `log_id`
- `event_id`
- `actor_type`
- `actor_id`
- `action_type`
- `input_ref`
- `output_ref`
- `timestamp`
- `note`

## 9. Agent 设计

### 9.1 城市活动总策划 Agent

职责：

- 理解 `EventBrief`
- 拆解活动策划任务
- 调度子 Agent
- 融合结果
- 输出 `EventPlan`

不可做：

- 不直接绕过子 Agent 生成全部内容。
- 不自动发布对外内容。

### 9.2 文化叙事 Agent

职责：

- 读取片区文化资料和商户故事。
- 生成活动主题、站点故事和游客端文化介绍。

输出：

- `theme`
- `narrative`
- `site_stories`

### 9.3 路线规划 Agent

职责：

- 根据静态点位、商户位置、活动时长和风险约束生成路线。

输出：

- 候选路线
- 预计时长
- 雨天备用路线
- 风险说明

### 9.4 商户匹配 Agent

职责：

- 从 `MerchantProfile` 中筛选适合当前活动的商户。
- 给每个商户分配活动角色。

输出：

- 推荐商户列表
- 角色分配
- 参与优先级

### 9.5 营销内容 Agent

职责：

- 生成活动宣传文案、游客端短文案、商户个性化文案。

输出：

- 主活动文案
- 商户文案
- 游客端文案

### 9.6 风险分析 Agent

职责：

- 分析天气、路线、商户容量、库存、居民影响和预算风险。

输出：

- 风险清单
- 触发条件
- 预案

### 9.7 失败恢复 Agent

职责：

- 在库存不足或天气突变时生成调整建议。

输出：

- `RecoveryAction`

要求：

- 必须说明触发原因。
- 必须说明影响范围。
- 必须给主办方确认选项。

### 9.8 复盘报告 Agent

职责：

- 读取活动日志、异常记录和商户状态，生成复盘报告。

输出：

- `ReviewReport`

## 10. 工具与 Mock

MVP 需要以下工具，不要求全部接真实 API：

| 工具 | MVP 实现方式 | 用途 |
| --- | --- | --- |
| 商户查询工具 | 读取本地 mock 数据 | 给商户匹配和路线规划使用 |
| 商户状态工具 | mock 状态表 + 手动按钮 | 触发库存不足 |
| 天气工具 | mock API 或固定按钮 | 触发强降雨 |
| 路线检查工具 | 静态点位 + 规则估算 | 判断路线时长和备用路线 |
| 预算计算工具 | 确定性函数 | 生成预算拆分 |
| 游客页面更新工具 | 写入当前活动状态 | 展示动态通知 |
| 报告导出工具 | Markdown/HTML/PDF 任选 | 生成复盘报告 |

## 11. 页面范围

### 11.1 主办方后台

必须包含：

- 活动创建
- AI 方案生成结果
- 商户执行包总览
- Dashboard
- 异常处理确认
- 复盘报告

### 11.2 商户端轻量页面

必须包含：

- 商户资料查看
- 活动执行包
- 库存/排队状态更新

### 11.3 游客 H5

必须包含：

- 活动介绍
- 路线节点
- 商户优惠或打卡任务
- 临时通知

## 12. 推荐 API 边界

后续实现可围绕这些接口设计：

- `POST /events`：创建活动，生成 `EventBrief`
- `POST /events/{event_id}/generate-plan`：生成 `EventPlan`
- `GET /events/{event_id}/plan`：读取活动方案
- `POST /events/{event_id}/approve-plan`：主办方确认方案
- `GET /events/{event_id}/merchant-packs`：读取商户执行包
- `POST /merchants/{merchant_id}/runtime-state`：更新商户状态
- `POST /events/{event_id}/trigger/weather`：触发天气异常
- `POST /events/{event_id}/trigger/inventory`：触发库存异常
- `GET /events/{event_id}/recovery-actions`：读取恢复建议
- `POST /recovery-actions/{action_id}/approve`：确认恢复动作
- `GET /public/events/{event_id}`：游客 H5 数据
- `POST /events/{event_id}/review-report`：生成复盘报告

## 13. 演示脚本

### 13.1 3-5 分钟短演示

1. 展示主办方创建活动：“周末旧区夜游，预算 MOP 50,000，目标亲子与年轻游客”。
2. 点击生成方案，展示活动主题、路线、商户、预算、风险预案。
3. 展示一个商户执行包。
4. 展示游客 H5。
5. 触发库存不足异常。
6. 展示 Recovery Agent 生成替代商户和游客通知。
7. 主办方确认调整，游客端更新。
8. 展示复盘报告摘要。

### 13.2 10 分钟路演重点

- 为什么不做普通旅游推荐，而做活动编排后台。
- 多 Agent 如何协作。
- 工具调用如何参与决策。
- 动态恢复如何体现 Agent 能力。
- 人工确认和审计如何控制责任边界。
- 后续如何扩展到真实商户和更多旧区。

## 14. 验收标准

MVP 完成必须满足：

- 能创建一场活动并生成结构化 `EventBrief`。
- 能生成完整 `EventPlan`。
- 至少 8 个模拟商户可参与匹配。
- 每个参与商户有执行包。
- 游客 H5 能显示活动路线和站点内容。
- Dashboard 能显示商户状态和异常。
- 库存不足异常能触发恢复建议。
- 天气突变异常能触发雨天路线建议。
- 恢复动作必须经过主办方确认。
- 确认后游客 H5 或活动状态可见更新。
- 能生成活动复盘报告。
- 能展示 Agent 调用、工具调用或审计记录。

## 15. 实施阶段建议

### Phase 1：静态数据与页面骨架

- 建立 mock 商户数据。
- 建立活动创建表单。
- 建立主办方后台基础页面。
- 建立游客 H5 静态展示。

### Phase 2：后端状态与数据对象

- 实现 EventBrief/EventPlan/MerchantProfile 等对象。
- 实现基础 API。
- 实现活动方案保存与读取。

### Phase 3：Agent 编排接入

- 接入 Qwen/QwenPaw。
- 实现总策划 Agent 和 3-4 个核心子 Agent。
- 先保证结构化输出稳定。

### Phase 4：异常恢复闭环

- 实现库存不足触发。
- 实现天气突变触发。
- 实现 RecoveryAction 与主办方确认。
- 实现游客端更新。

### Phase 5：复盘与演示打磨

- 实现 ReviewReport。
- 固定 demo 数据和演示脚本。
- 准备实践文章材料。

## 16. 主要风险

### 风险 1：范围膨胀

表现：做成完整 SaaS，无法按时完成。

控制：第一版只做一个片区、一场活动、两个异常。

### 风险 2：退化成文案生成器

表现：只生成主题和宣传文本，看不出 Agent 能力。

控制：必须展示任务拆解、工具调用、状态变化、恢复动作和审计记录。

### 风险 3：数据不真实

表现：评委质疑商户和路线都是编的。

控制：明确 MVP 使用模拟商户验证流程；文化点、片区背景尽量来自公开资料；后续说明可接真实商户试点。

### 风险 4：现场演示不稳定

表现：外部 API、模型响应或网络导致 demo 中断。

控制：异常用 mock 触发；关键 demo 数据可预置；保留降级输出。

### 风险 5：责任边界不清

表现：AI 自动导流或发布，影响商户和游客体验。

控制：所有对外更新都需主办方确认；保留审计日志。

## 17. 后续待决策

- 前端采用 React 还是 Vue。
- 后端采用 FastAPI 还是 Node。
- QwenPaw 是作为核心 Agent 编排框架，还是先用轻量封装再逐步迁移。
- 游客 H5 是否需要地图组件，还是第一版用静态路线卡片。
- 复盘报告导出为 Markdown、HTML 还是 PDF。

## 18. 当前结论

“智引濠江”应作为主选题推进，但第一版只能做可演示的旧区活动编排 Agent MVP。工程实现必须围绕一条闭环展开：

> 创建活动 -> 生成方案 -> 商户执行包 -> 游客 H5 -> 异常触发 -> 动态重规划 -> 主办方确认 -> 游客端更新 -> 复盘报告。

任何不服务这条闭环的功能，第一版都应推迟。
