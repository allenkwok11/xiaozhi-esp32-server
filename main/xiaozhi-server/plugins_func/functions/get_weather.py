import requests
from bs4 import BeautifulSoup
from config.logger import setup_logging
from plugins_func.register import register_function, ToolType, ActionResponse, Action
import json

TAG = __name__
logger = setup_logging()

GET_WEATHER_FUNCTION_DESC = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "获取某个地点的天气，用户应提供一个位置，比如用户说杭州天气，参数为：杭州。"
            "如果用户说的是省份，默认用省会城市。如果用户说的不是省份或城市而是一个地名，"
            "默认用该地所在省份的省会城市。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "地点名，例如杭州。可选参数，如果不提供则不传"
                },
                "lang": {
                    "type": "string",
                    "description": "返回用户使用的语言code，例如zh_CN/zh_HK/en_US/ja_JP等，默认zh_CN"
                }
            },
            "required": ["lang"]
        }
    }
}

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    )
}


def fetch_city_info(location, api_key):
    url = f"https://geoapi.qweather.com/v2/city/lookup?key={api_key}&location={location}&lang=zh"
    logger.bind(tag=TAG).info(f"正在请求城市信息API，URL: {url}")
    try:
        response = requests.get(url, headers=HEADERS)
        logger.bind(tag=TAG).info(f"城市信息API响应状态码: {response.status_code}")
        json_data = response.json()
        logger.bind(tag=TAG).debug(f"城市信息API响应: {json.dumps(json_data, ensure_ascii=False)}")
        return json_data.get('location', [])[0] if json_data.get('location') else None
    except Exception as e:
        logger.bind(tag=TAG).error(f"获取城市信息失败: {str(e)}")
        return None


def fetch_weather_page(url):
    logger.bind(tag=TAG).info(f"正在请求天气页面，URL: {url}")
    try:
        response = requests.get(url, headers=HEADERS)
        logger.bind(tag=TAG).info(f"天气页面响应状态码: {response.status_code}")
        if not response.ok:
            logger.bind(tag=TAG).error(f"获取天气页面失败: {response.text[:200]}")
        return BeautifulSoup(response.text, "html.parser") if response.ok else None
    except Exception as e:
        logger.bind(tag=TAG).error(f"获取天气页面失败: {str(e)}")
        return None


def parse_weather_info(soup):
    try:
        city_name = soup.select_one("h1.c-submenu__location").get_text(strip=True)
        logger.bind(tag=TAG).info(f"解析到城市名称: {city_name}")

        current_abstract = soup.select_one(".c-city-weather-current .current-abstract")
        current_abstract = current_abstract.get_text(strip=True) if current_abstract else "未知"
        logger.bind(tag=TAG).info(f"当前天气概况: {current_abstract}")

        current_basic = {}
        for item in soup.select(".c-city-weather-current .current-basic .current-basic___item"):
            parts = item.get_text(strip=True, separator=" ").split(" ")
            if len(parts) == 2:
                key, value = parts[1], parts[0]
                current_basic[key] = value
        logger.bind(tag=TAG).info(f"当前天气详情: {json.dumps(current_basic, ensure_ascii=False)}")

        temps_list = []
        for row in soup.select(".city-forecast-tabs__row")[:7]:  # 取前7天的数据
            date = row.select_one(".date-bg .date").get_text(strip=True)
            temps = [span.get_text(strip=True) for span in row.select(".tmp-cont .temp")]
            high_temp, low_temp = (temps[0], temps[-1]) if len(temps) >= 2 else (None, None)
            temps_list.append((date, high_temp, low_temp))
        logger.bind(tag=TAG).info(f"获取到未来7天温度: {temps_list}")

        return city_name, current_abstract, current_basic, temps_list
    except Exception as e:
        logger.bind(tag=TAG).error(f"解析天气信息失败: {str(e)}")
        return "未知城市", "未知天气", {}, []


@register_function('get_weather', GET_WEATHER_FUNCTION_DESC, ToolType.SYSTEM_CTL)
def get_weather(conn, location: str = None, lang: str = "zh_CN"):
    logger.bind(tag=TAG).info(f"===== 天气查询函数开始执行 =====")
    logger.bind(tag=TAG).info(f"查询参数: location={location}, lang={lang}")
    
    try:
        api_key = conn.config["plugins"]["get_weather"]["api_key"]
        default_location = conn.config["plugins"]["get_weather"]["default_location"]
        
        # 位置参数处理逻辑优化
        # 1. 如果传入了明确的位置参数且不为None/空字符串，则使用该参数
        # 2. 否则，尝试使用客户端IP地址对应的城市信息
        # 3. 如果上述都无效，则使用配置文件中的默认位置
        if location and location.strip():
            final_location = location.strip()
            logger.bind(tag=TAG).info(f"使用用户明确指定的位置: {final_location}")
        elif conn.client_ip_info and "city" in conn.client_ip_info and conn.client_ip_info["city"]:
            final_location = conn.client_ip_info["city"]
            logger.bind(tag=TAG).info(f"使用IP地址解析的位置: {final_location}")
        else:
            final_location = default_location
            logger.bind(tag=TAG).info(f"使用配置文件中的默认位置: {final_location}")
            
        logger.bind(tag=TAG).info(f"最终使用的查询地点: {final_location}, API Key: {api_key}")

        city_info = fetch_city_info(final_location, api_key)
        if not city_info:
            error_msg = f"未找到相关的城市: {final_location}，请确认地点是否正确"
            logger.bind(tag=TAG).error(error_msg)
            # 构造一个直接回复
            direct_response = f"抱歉，我未能找到\"{final_location}\"的天气信息，请确认地点名称是否正确，或者尝试查询其他城市的天气。"
            return ActionResponse(Action.RESPONSE, None, direct_response)  # 使用RESPONSE动作直接返回

        logger.bind(tag=TAG).info(f"获取到城市信息: {json.dumps(city_info, ensure_ascii=False)}")
        logger.bind(tag=TAG).info(f"天气查询链接: {city_info['fxLink']}")
        
        soup = fetch_weather_page(city_info['fxLink'])
        if not soup:
            error_msg = "请求天气页面失败"
            logger.bind(tag=TAG).error(error_msg)
            direct_response = f"抱歉，在获取{final_location}的天气信息时遇到了问题，请稍后再试。"
            return ActionResponse(Action.RESPONSE, None, direct_response)  # 使用RESPONSE动作直接返回

        city_name, current_abstract, current_basic, temps_list = parse_weather_info(soup)
        
        # 构建天气报告（给LLM使用的详细数据）
        weather_report = f"根据下列数据，用{lang}回应用户的查询天气请求：\n{city_name}未来7天天气:\n"
        for i, (date, high, low) in enumerate(temps_list):
            if high and low:
                weather_report += f"{date}: {low}到{high}\n"
        weather_report += (
            f"当前天气: {current_abstract}\n"
            f"当前天气参数: {current_basic}\n"
            f"(确保只报告指定单日的气温范围，除非用户明确要求想要了解多日天气，如果未指定，默认报告今天的温度范围。"
            "参数为0的值不需要报告给用户，每次都报告体感温度，根据语境选择合适的参数内容告知用户，并对参数给出相应评价)"
        )
        
        # 同时构建一个直接可用的人性化天气回复
        # 这用作备用，防止LLM处理失败时能够直接回复用户
        today_temp = ""
        for date, high, low in temps_list:
            if "今天" in date or "今日" in date:
                today_temp = f"{low}到{high}"
                break
        if not today_temp and temps_list:
            today_temp = f"{temps_list[0][2]}到{temps_list[0][1]}"
        
        feel_temp = current_basic.get("体感温度", "")
        humidity = current_basic.get("相对湿度", "")
        
        direct_response = f"{city_name}今天{current_abstract}，温度{today_temp}。"
        if feel_temp:
            direct_response += f"体感温度{feel_temp}。"
        if humidity:
            direct_response += f"相对湿度{humidity}。"
            
        # 添加简单的建议
        if "雨" in current_abstract:
            direct_response += "外出请记得带伞。"
        elif temps_list and temps_list[0][1] and int(temps_list[0][1].replace("°", "")) > 30:
            direct_response += "天气炎热，注意防暑。"
        elif temps_list and temps_list[0][2] and int(temps_list[0][2].replace("°", "")) < 10:
            direct_response += "天气较冷，注意保暖。"
        
        logger.bind(tag=TAG).info(f"构建的天气报告: {weather_report}")
        logger.bind(tag=TAG).info(f"备用直接回复: {direct_response}")
        logger.bind(tag=TAG).info(f"===== 天气查询函数执行完毕，返回结果 =====")
        
        # 返回详细天气报告，但添加direct_response作为备用
        return ActionResponse(Action.REQLLM, weather_report, direct_response)
    except Exception as e:
        error_msg = f"查询天气时发生错误: {str(e)}"
        logger.bind(tag=TAG).error(error_msg)
        # 出错时也提供一个直接回复
        direct_response = f"抱歉，在获取天气信息时遇到了技术问题，请稍后再试。"
        return ActionResponse(Action.RESPONSE, None, direct_response)  # 使用RESPONSE动作直接返回
