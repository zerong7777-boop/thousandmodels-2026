def describe_weather(status: str) -> str:
    if status == "heavy_rain":
        return "强降雨"
    if status == "light_rain":
        return "小雨"
    return "正常"
