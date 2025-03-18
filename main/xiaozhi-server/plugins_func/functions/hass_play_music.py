from plugins_func.register import register_function,ToolType, ActionResponse, Action
from config.logger import setup_logging
import asyncio
import requests

TAG = __name__
logger = setup_logging()

HASS_CACHE = {}

hass_play_music_function_desc = {
            "type": "function",
            "function": {
                "name": "hass_play_music",
                "description": "用户想听音乐、有声书的时候使用，在房间的媒体播放器（media_player）里播放对应音频",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "media_content_id": {
                                "type": "string",
                                "description": "可以是音乐或有声书的专辑名称、歌曲名、演唱者,如果未指定就填random"
                            },
                            "entity_id": {
                            "type": "string",
                            "description": "需要操作的音箱的设备id,homeassistant里的entity_id,media_player开头"
                            }
                        },
                        "required": ["media_content_id", "entity_id"]
                    }
                }
            }


@register_function('hass_play_music', hass_play_music_function_desc, ToolType.SYSTEM_CTL)

def hass_play_music(conn, entity_id='', media_content_id='random'):
    try:
        #logger.bind(tag=TAG).error(f"arguments: {arguments}")
        
        #entity_id = arguments["entity_id"]
        #media_content_id = arguments["media_content_id"]
        
        #logger.bind(tag=TAG).error(f"entity_id: {entity_id}")


        # 执行音乐播放命令
        future = asyncio.run_coroutine_threadsafe(
            handle_hass_play_music(conn, entity_id, media_content_id),
            conn.loop
        )
        ha_response = future.result()
        return ActionResponse(action=Action.RESPONSE, result="退出意图已处理", response=ha_response)
    except Exception as e:
        logger.bind(tag=TAG).error(f"处理音乐意图错误: {e}")

def initialize_hass_handler(conn):
    config = conn.config
    global HASS_CACHE
    if HASS_CACHE == {}:
        logger.bind(tag=TAG).info(f"实例化HASS:")
        if "HomeAssistant" in config["LLM"]:
            HASS_CACHE['base_url'] = config["LLM"]['HomeAssistant']['base_url']
            HASS_CACHE['api_key'] = config["LLM"]['HomeAssistant']['api_key']
        else:
            logger.bind(tag=TAG).error(f"使用前请在config文件中配置: LLM.HomeAssistant.base_url LLM.HomeAssistant.api_key")

async def handle_hass_play_music( conn, entity_id, media_content_id):
    initialize_hass_handler(conn)
    global HASS_CACHE
    api_key = HASS_CACHE['api_key']
    base_url = HASS_CACHE['base_url']
    url = f"{base_url}/api/services/music_assistant/play_media"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "entity_id": entity_id,
        "media_id": media_content_id
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return f"正在播放{media_content_id}的音乐"
    else:
        return f"音乐播放失败，错误码: {response.status_code}"
