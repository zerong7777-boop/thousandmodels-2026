RAINY_ROUTE = ["内港咖啡室", "内港小展馆", "旧区社区客厅", "十月初五茶餐厅"]
DEFAULT_ROUTE = ["福隆新街集合", "福隆老饼家", "新马路文创铺", "内港小展馆", "十月初五茶餐厅", "新街手信铺"]


def build_static_route(rainy: bool = False) -> list[str]:
    return list(RAINY_ROUTE if rainy else DEFAULT_ROUTE)
