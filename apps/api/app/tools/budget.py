from app.schemas import BudgetPlan


def split_budget(total_mop: int) -> BudgetPlan:
    marketing = int(total_mop * 0.28)
    merchant_support = int(total_mop * 0.34)
    staffing = int(total_mop * 0.23)
    contingency = total_mop - marketing - merchant_support - staffing
    return BudgetPlan(
        total_mop=total_mop,
        marketing_mop=marketing,
        merchant_support_mop=merchant_support,
        staffing_mop=staffing,
        contingency_mop=contingency,
    )
