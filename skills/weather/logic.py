
import requests

def get_weather(city: str):
    """
    查询指定城市的天气信息。
    参数:
    - city: 城市名称，如 '北京'、'上海'、'广州'
    返回: 天气信息，包括温度、天气状况、湿度等
    """
    try:
        # 使用免费的天气 API (Open-Meteo)
        # 首先需要通过城市名获取经纬度
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=zh&format=json"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return f"未找到城市: {city}"

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        city_name = geo_data["results"][0]["name"]

        # 获取天气信息
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=auto"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        current = weather_data["current"]
        temp = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        wind_speed = current["wind_speed_10m"]
        weather_code = current["weather_code"]

        # 天气代码映射
        weather_map = {
            0: "晴朗",
            1: "大部晴朗",
            2: "多云",
            3: "阴天",
            45: "雾",
            48: "雾凇",
            51: "毛毛雨",
            53: "中度毛毛雨",
            55: "密毛毛雨",
            61: "小雨",
            63: "中雨",
            65: "大雨",
            71: "小雪",
            73: "中雪",
            75: "大雪",
            80: "阵雨",
            81: "强阵雨",
            82: "暴雨",
            95: "雷雨",
            96: "雷暴伴冰雹",
            99: "强雷暴伴冰雹"
        }

        weather_desc = weather_map.get(weather_code, "未知")

        result = f"""
📍 {city_name} 天气信息:
━━━━━━━━━━━━━━━━
🌡️ 温度: {temp}°C
💧 湿度: {humidity}%
💨 风速: {wind_speed} km/h
☁️ 天气: {weather_desc}
━━━━━━━━━━━━━━━━
"""
        return result.strip()
    except Exception as e:
        return f"查询天气失败: {str(e)}"

def get_skills():
    """插件注册入口"""
    return {
        "get_weather": get_weather
    }
