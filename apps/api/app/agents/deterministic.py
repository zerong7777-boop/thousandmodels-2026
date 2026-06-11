from app.schemas import EventBrief, MerchantProfile
from app.tools.budget import split_budget
from app.tools.merchant import select_night_merchants
from app.tools.route import build_static_route


class DeterministicAgentBackend:
    def plan_event(self, brief: EventBrief, merchants: list[MerchantProfile]) -> dict:
        selected = select_night_merchants(merchants, limit=6)
        assignments = []
        role_templates = [
            ("集合与开场试吃", "18:10-18:35"),
            ("文化问答与打卡", "18:35-19:00"),
            ("内港故事讲解", "19:00-19:30"),
            ("夜间补给", "19:30-20:00"),
            ("亲子互动备用点", "20:00-20:35"),
            ("路线收尾与手信优惠", "20:35-21:10"),
        ]
        for merchant, (role, slot) in zip(selected, role_templates, strict=False):
            assignments.append(
                {
                    "merchant_id": merchant.merchant_id,
                    "role": role,
                    "time_slot": slot,
                    "rationale": f"{merchant.name} 适合 {', '.join(merchant.suitable_activity_types[:2])}，夜间适配度 {merchant.night_score}/5。",
                }
            )

        return {
            "event_id": brief.event_id,
            "theme": "旧城夜光：福隆新街到内港的味觉与故事路线",
            "narrative": "以老字号美食、骑楼街景和内港记忆串联旧区夜游，把游客从单点消费引导为多点停留。",
            "route": build_static_route(rainy=False),
            "schedule": [
                "18:00 主办方与商户完成集合确认",
                "18:10 福隆新街开场与老字号试吃",
                "18:40 新马路文创打卡与街区问答",
                "19:10 内港故事点讲解",
                "19:45 茶餐厅补给与分流",
                "20:20 手作或社区客厅互动",
                "21:00 手信收尾与游客通知复核",
            ],
            "merchant_assignments": assignments,
            "budget_plan": split_budget(brief.budget_mop).model_dump(),
            "marketing_content": [
                "今晚从福隆新街出发，用一条夜游路线读懂澳门旧区。",
                "完成三处打卡任务，可在参与商户领取限定优惠。",
                "如遇天气或库存变化，请以游客 H5 的临时通知为准。",
            ],
            "risk_plan": [
                {
                    "risk_id": "r_inventory",
                    "level": "medium",
                    "description": "热门手信或试吃商品提前售罄。",
                    "trigger_condition": "商户库存状态变为 low 或 sold_out。",
                    "mitigation": "降低该商户导流权重，切换备用商户或改为故事打卡任务。",
                },
                {
                    "risk_id": "r_weather",
                    "level": "high",
                    "description": "强降雨影响户外停留点。",
                    "trigger_condition": "天气工具返回 heavy_rain。",
                    "mitigation": "切换内港咖啡室、小展馆和社区客厅组成的雨天路线。",
                },
                {
                    "risk_id": "r_queue",
                    "level": "medium",
                    "description": "单点排队过长影响路线节奏。",
                    "trigger_condition": "商户排队状态变为 overloaded。",
                    "mitigation": "分批到达，并推送下一个点位的文化任务。",
                },
            ],
            "execution_checklist": [
                "主办方确认路线和对外发布文案。",
                "商户确认执行包、库存和备用物料。",
                "游客 H5 发布前完成二维码和通知测试。",
                "异常恢复动作必须由主办方确认后同步游客端。",
            ],
            "version": 1,
            "approval_status": "draft",
        }
