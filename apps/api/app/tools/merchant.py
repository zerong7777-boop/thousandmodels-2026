from app.schemas import MerchantProfile


def select_night_merchants(merchants: list[MerchantProfile], limit: int = 6) -> list[MerchantProfile]:
    ranked = sorted(
        merchants,
        key=lambda item: (item.night_score, item.rainy_day_score, item.capacity_level),
        reverse=True,
    )
    return ranked[:limit]


def find_merchant(merchants: list[MerchantProfile], merchant_id: str) -> MerchantProfile | None:
    return next((merchant for merchant in merchants if merchant.merchant_id == merchant_id), None)
