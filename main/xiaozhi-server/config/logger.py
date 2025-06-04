import os
import sys
from loguru import logger
from config.config_loader import load_config
from config.settings import check_config_file
from datetime import datetime

SERVER_VERSION = "0.5.2"
_logger_initialized = False
_current_log_file = None
_current_log_size = 0
_max_log_size = 10 * 1024 * 1024  # 10MB

def get_module_abbreviation(module_name, module_dict):
    """获取模块名称的缩写，如果为空则返回00"""
    module_value = module_dict.get(module_name, "")
    if not module_value:
        return "00"
    if "_" in module_value:
        parts = module_value.split("_")
        return parts[-1][:2] if parts[-1] else "00"
    return module_value[:2]

def build_module_string(selected_module):
    """构建模块字符串"""
    return (
        get_module_abbreviation("VAD", selected_module)
        + get_module_abbreviation("ASR", selected_module)
        + get_module_abbreviation("LLM", selected_module)
        + get_module_abbreviation("TTS", selected_module)
        + get_module_abbreviation("Memory", selected_module)
        + get_module_abbreviation("Intent", selected_module)
    )

def formatter(record):
    """为没有 tag 的日志添加默认值"""
    record["extra"].setdefault("tag", record["name"])
    return record["message"]

def get_log_filename(log_dir, base_name):
    """生成按日期和大小分割的日志文件名"""
    global _current_log_file, _current_log_size
    
    now = datetime.now()
    date_part = f"{now.month}.{now.day}"
    
    # 检查是否需要创建新文件
    if _current_log_file is None or not os.path.exists(_current_log_file):
        file_index = 1
        while True:
            new_filename = os.path.join(log_dir, f"{base_name}.{date_part}.{file_index}")
            if not os.path.exists(new_filename):
                _current_log_file = new_filename
                _current_log_size = 0
                return new_filename
            # 如果文件已存在，增加索引
            file_index += 1
    else:
        # 检查文件大小
        if _current_log_size > _max_log_size:
            # 文件过大，创建新文件
            base_path = os.path.splitext(_current_log_file)[0]
            parts = base_path.split('.') 
            if len(parts) >= 3:
                try: 
                    file_index = int(parts[-1]) + 1
                except ValueError:
                    file_index = 1
            else:
                file_index = 1
                
            new_filename = f"{base_path.rsplit('.', 1)[0]}.{file_index}" 
            _current_log_file = new_filename
            _current_log_size = 0
            return new_filename
        else:
            return _current_log_file

def update_log_size(message):
    """更新当前日志文件大小"""
    global _current_log_size
    # 如果当前日志文件存在，获取其大小
    if _current_log_file and os.path.exists(_current_log_file):
        _current_log_size = os.path.getsize(_current_log_file)
    else:
        # 如果当前日志文件不存在，重置大小
        _current_log_size = len(message.encode('utf-8'))

def setup_logging():
    check_config_file()
    """从配置文件中读取日志配置，并设置日志输出格式和级别"""
    config = load_config()
    log_config = config["log"]
    global _logger_initialized

    # 第一次初始化时配置日志
    if not _logger_initialized:
        logger.configure(
            extra={
                "selected_module": log_config.get("selected_module", "00000000000000")
            }
        )
        log_format = log_config.get(
            "log_format",
            "<green>{time:YYMMDD HH:mm:ss}</green>[{version}_{extra[selected_module]}][<light-blue>{extra[tag]}</light-blue>]-<level>{level}</level>-<light-green>{message}</light-green>",
        )
        log_format_file = log_config.get(
            "log_format_file",
            "{time:YYYY-MM-DD HH:mm:ss} - {version_{extra[selected_module]}} - {name} - {level} - {extra[tag]} - {message}",
        )
        selected_module_str = logger._core.extra["selected_module"]

        log_format = log_format.replace("{version}", SERVER_VERSION)
        log_format = log_format.replace("{selected_module}", selected_module_str)
        log_format_file = log_format_file.replace("{version}", SERVER_VERSION)
        log_format_file = log_format_file.replace(
            "{selected_module}", selected_module_str
        )

        log_level = log_config.get("log_level", "INFO")
        log_dir = log_config.get("log_dir", "tmp")
        log_file = log_config.get("log_file", "server")
        data_dir = log_config.get("data_dir", "data")

        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)

        # 配置日志输出
        logger.remove()

        # 输出到控制台
        logger.add(sys.stdout, format=log_format, level=log_level, filter=formatter)

        # 输出到文件，使用自定义的日志文件名生成器
        def sink(message):
            filename = get_log_filename(log_dir, log_file)
            with open(filename, "a", encoding="utf-8") as f:
                f.write(message + "\n")
            update_log_size(message)

        logger.add(
            sink,
            format=log_format_file,
            level=log_level,
            filter=formatter,
        )
        _logger_initialized = True

    return logger

def update_module_string(selected_module_str):
    """更新模块字符串并重新配置日志处理器"""
    logger.debug(f"更新日志配置组件")
    current_module = logger._core.extra["selected_module"]

    if current_module == selected_module_str:
        return

    try:
        logger.configure(extra={"selected_module": selected_module_str})

        config = load_config()
        log_config = config["log"]

        log_format = log_config.get(
            "log_format",
            "<green>{time:YYMMDD HH:mm:ss}</green>[{version}_{extra[selected_module]}][<light-blue>{extra[tag]}</light-blue>]-<level>{level}</level>-<light-green>{message}</light-green>",
        )
        log_format_file = log_config.get(
            "log_format_file",
            "{time:YYYY-MM-DD HH:mm:ss} - {version_{extra[selected_module]}} - {name} - {level} - {extra[tag]} - {message}",
        )

        log_format = log_format.replace("{version}", SERVER_VERSION)
        log_format = log_format.replace("{selected_module}", selected_module_str)
        log_format_file = log_format_file.replace("{version}", SERVER_VERSION)
        log_format_file = log_format_file.replace(
            "{selected_module}", selected_module_str
        )

        log_dir = log_config.get("log_dir", "tmp")
        log_file = log_config.get("log_file", "server")

        logger.remove()
        logger.add(
            sys.stdout,
            format=log_format,
            level=log_config.get("log_level", "INFO"),
            filter=formatter,
        )

        def sink(message):
            filename = get_log_filename(log_dir, log_file)
            with open(filename, "a", encoding="utf-8") as f:
                f.write(message + "\n")
            update_log_size(message)

        logger.add(
            sink,
            format=log_format_file,
            level=log_config.get("log_level", "INFO"),
            filter=formatter,
        )

    except Exception as e:
        logger.error(f"日志配置更新失败: {str(e)}")
        raise
