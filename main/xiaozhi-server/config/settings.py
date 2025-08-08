import os
from config.config_loader import read_config, get_project_dir, load_config


default_config_file = "config.yaml"
config_file_valid = False


def check_config_file():
    global config_file_valid
    if config_file_valid:
        return
    """
    简化的配置检查，仅提示用户配置文件的使用情况
    """
    custom_config_file = get_project_dir() + "data/." + default_config_file
    if not os.path.exists(custom_config_file):
        raise FileNotFoundError(
            "Cannot find data/.config.yaml file, please verify its existence according to the tutorial"
        )

    # 检查是否从API读取配置
    config = load_config()
    if config.get("read_config_from_api", False):
        print("read config from api")
        old_config_origin = read_config(custom_config_file)
        if old_config_origin.get("selected_module") is not None:
            error_msg = "Your configuration file appears to contain both console configuration and local configuration:\n"
            error_msg += "\nRecommendations:\n"
            error_msg += "1、Copy the config_from_api.yaml file from root directory to data folder and rename it to .config.yaml.\n"
            error_msg += "2、Configure the API endpoint and keys according to the tutorial.\n"
            raise ValueError(error_msg)
    config_file_valid = True
