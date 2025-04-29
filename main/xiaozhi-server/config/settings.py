import os
from collections.abc import Mapping
from config import logger
from config.config_loader import read_config, get_project_dir, load_config

TAG = __name__
logger = logger.setup_logging()

default_config_file = "config.yaml"


def find_missing_keys(new_config, old_config, parent_key=""):
    """
    递归查找缺失的配置项
    返回格式：[缺失配置路径]
    """
    missing_keys = []

    if not isinstance(new_config, Mapping):
        return missing_keys

    for key, value in new_config.items():
        # 构建当前配置路径
        full_path = f"{parent_key}.{key}" if parent_key else key

        # 检查键是否存在
        if key not in old_config:
            missing_keys.append(full_path)
            continue

        # 递归检查嵌套字典
        if isinstance(value, Mapping):
            sub_missing = find_missing_keys(
                value, old_config[key], parent_key=full_path
            )
            missing_keys.extend(sub_missing)
    return missing_keys


def check_config_file():
    """
    简化的配置检查，仅提示用户配置文件的使用情况
    """
    custom_config_file = get_project_dir() + "data/." + default_config_file
    if not os.path.exists(custom_config_file):
        logger.bind(tag=TAG).info("提示: 使用默认配置文件。如需自定义配置，请创建 data/.config.yaml 文件")
    else:
        logger.bind(tag=TAG).info(f"提示: 使用自定义配置文件 data/.config.yaml，配置将覆盖默认值")
    
    # 检查是否从API读取配置
    config = load_config()
    if config.get("read_config_from_api", False):
        logger.bind(tag=TAG).info("提示: 从API获取配置")
