import os
import time
import yaml
import json
import requests
from config.logger import setup_logging
from typing import Dict, Any, Optional
from copy import deepcopy
from core.utils.util import get_project_dir
from core.utils import llm, tts
from core.utils.lock_manager import FileLockManager

TAG = __name__

class PrivateConfig:
    def __init__(self, device_id: str, default_config: Dict[str, Any], auth_code_gen=None):
        self.device_id = device_id
        self.default_config = default_config
        self.config_path = get_project_dir() + 'data/.private_config.yaml'
        self.logger = setup_logging()
        self.private_config = {}
        self.auth_code_gen = auth_code_gen
        self.lock_manager = FileLockManager()

    async def load_or_create(self):
        try:
            # 优先通过远程获取配置
            fetch_config_ = {}
            remote_config = self.default_config['remote_config']
            self.logger.bind(tag=TAG).info(f"remote config: {remote_config}")
            if remote_config and remote_config['enabled']:
                fetch_config_ = await self.fetch_config(remote_config['url'])

            self.logger.bind(tag=TAG).info(f"fetch_config: {fetch_config_}")
            await self.lock_manager.acquire_lock(self.config_path)
            try:
                if os.path.exists(self.config_path):
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        all_configs = yaml.safe_load(f) or {}
                else:
                    all_configs = {}

                if fetch_config_:
                    all_configs[self.device_id] = fetch_config_

                if self.device_id not in all_configs:
                    # Get selected module names
                    selected_modules = self.default_config['selected_module']
                    selected_tts = selected_modules['TTS']
                    selected_llm = selected_modules['LLM']
                    selected_asr = selected_modules['ASR']
                    selected_vad = selected_modules['VAD']

                    # 生成认证码
                    auth_code = None
                    if self.auth_code_gen:
                        auth_code = self.auth_code_gen.generate_code()

                    # Initialize device config with only necessary configurations
                    device_config = {
                        'selected_module': deepcopy(selected_modules),
                        'prompt': self.default_config['prompt'],
                        'LLM': {
                            selected_llm: deepcopy(self.default_config['LLM'][selected_llm])
                        },
                        'TTS': {
                            selected_tts: deepcopy(self.default_config['TTS'][selected_tts])
                        },
                        'ASR': {
                            selected_asr: deepcopy(self.default_config['ASR'][selected_asr])
                        },
                        'VAD': {
                            selected_vad: deepcopy(self.default_config['VAD'][selected_vad])
                        },
                        'auth_code': auth_code  # 添加认证码字段
                    }
                    
                    all_configs[self.device_id] = device_config
                    
                # Save updated configs
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(all_configs, f, allow_unicode=True)

                self.private_config = all_configs[self.device_id]

            finally:
                self.lock_manager.release_lock(self.config_path)

        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Error handling private config: {e}")
            self.private_config = {}

    async def update_config(self, selected_modules: Dict[str, str], prompt: str, nickname: str) -> bool:
        """更新设备配置
        Args:
            selected_modules: 选择的模块配置，格式如 {'LLM': 'AliLLM', 'TTS': 'EdgeTTS',...}
            prompt: 提示词配置
        Returns:
            bool: 更新是否成功
        """
        try:
            await self.lock_manager.acquire_lock(self.config_path)
            try:
                # Read main config to get full module configurations
                main_config = self.default_config

                # Create new device config
                device_config = {
                    'selected_module': selected_modules,
                    'prompt': prompt,
                    'nickname': nickname,
                }
                if self.private_config.get('last_chat_time'):
                    device_config['last_chat_time'] = self.private_config['last_chat_time']
                if self.private_config.get('owner'):
                    device_config['owner'] = self.private_config['owner']

                # Copy full module configurations from main config
                for module_type, selected_name in selected_modules.items():
                    if selected_name and selected_name in main_config.get(module_type, {}):
                        device_config[module_type] = {
                            selected_name: main_config[module_type][selected_name]
                        }

                # Read all configs
                if os.path.exists(self.config_path):
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        all_configs = yaml.safe_load(f) or {}
                else:
                    all_configs = {}

                # Update device config
                all_configs[self.device_id] = device_config
                self.private_config = device_config

                # Save back to file
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(all_configs, f, allow_unicode=True)

                return True
            finally:
                self.lock_manager.release_lock(self.config_path)

        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Error updating config: {e}")
            return False

    async def delete_config(self) -> bool:
        """删除设备配置
        Returns:
            bool: 删除是否成功
        """
        try:
            await self.lock_manager.acquire_lock(self.config_path)
            try:
                # 读取所有配置
                if os.path.exists(self.config_path):
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        all_configs = yaml.safe_load(f) or {}
                else:
                    return False

                # 删除设备配置
                if self.device_id in all_configs:
                    del all_configs[self.device_id]
                    
                    # 保存更新后的配置
                    with open(self.config_path, 'w', encoding='utf-8') as f:
                        yaml.dump(all_configs, f, allow_unicode=True)
                    
                    self.private_config = {}
                    return True
                
                return False
            finally:
                self.lock_manager.release_lock(self.config_path)

        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Error deleting config: {e}")
            return False

    def create_private_instances(self):
        #  判断存在私有配置，并且self.device_id在私有配置中
        if not self.private_config:
            self.logger.bind(tag=TAG).error("Private config not found for device_id: {}", self.device_id)
            return None, None
        
        """创建私有处理模块实例"""
        config = self.private_config
        selected_modules = config['selected_module']
        return (
            llm.create_instance(
                selected_modules["LLM"]
                if not 'type' in config["LLM"][selected_modules["LLM"]]
                else
                config["LLM"][selected_modules["LLM"]]['type'],
                config["LLM"][selected_modules["LLM"]],
            ),
            tts.create_instance(
                selected_modules["TTS"]
                if not 'type' in config["TTS"][selected_modules["TTS"]]
                else
                config["TTS"][selected_modules["TTS"]]["type"],
                config["TTS"][selected_modules["TTS"]],
                self.default_config.get("delete_audio", True)  # Using default_config for global settings
            )
        )

    async def update_last_chat_time(self, timestamp=None):
        """更新设备最近一次的聊天时间
        Args:
            timestamp: 指定的时间戳,不传则使用当前时间
        """
        if not self.private_config:
            self.logger.bind(tag=TAG).error("Private config not found")
            return False
            
        try:
            await self.lock_manager.acquire_lock(self.config_path)
            try:
                if timestamp is None:
                    timestamp = int(time.time())
                    
                self.private_config['last_chat_time'] = timestamp
                
                # 读取所有配置
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    all_configs = yaml.safe_load(f) or {}
                    
                # 更新当前设备配置    
                all_configs[self.device_id] = self.private_config
                
                # 保存回文件
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(all_configs, f, allow_unicode=True)
                    
                return True
            finally:
                self.lock_manager.release_lock(self.config_path)
                
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Error updating last chat time: {e}")
            return False

    def get_auth_code(self) -> str:
        """获取设备的认证码
        Returns:
            str: 认证码，如果没有返回空字符串
        """
        return self.private_config.get('auth_code', '')

    def get_owner(self) -> Optional[str]:
        """获取设备当前所有者"""
        return self.private_config.get('owner')

    async def fetch_config(self, fetch_url: str) -> Dict[str, Any]:
        """通过HTTP请求远程获取配置"""
        url = f"{fetch_url}{self.device_id}"
        headers = {
            'device_id': self.device_id
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 如果响应状态码不是200，会抛出异常
            # 检查响应内容类型是否为JSON
            if response.headers.get('Content-Type') != 'application/json':
                self.logger.bind(tag=TAG).error("Invalid content type: expected application/json")
                return {}

            # 解析JSON数据
            config_data = response.json()

            # 验证返回的数据结构
            if not isinstance(config_data, dict):
                self.logger.bind(tag=TAG).error("Invalid data format: expected a dictionary")
                return {}

            if config_data['code'] != 0:
                self.logger.bind(tag=TAG).error(f"Fetch config error: {config_data['msg']}")
                return {}
            
            config_data_ = config_data['data']
            if not isinstance(config_data_, dict):
                self.logger.bind(tag=TAG).error("Invalid config data format: expected a dictionary")
                return {}


            # 检查必要的字段是否存在
            required_fields = ['selected_module', 'prompt', 'LLM', 'TTS', 'ASR', 'VAD']
            for field in required_fields:
                if field not in config_data_:
                    self.logger.bind(tag=TAG).error(f"Missing required field: {field}")
                    return {}

            # 检查每个模块的配置是否正确
            for module in ['LLM', 'TTS', 'ASR', 'VAD']:
                if not isinstance(config_data_[module], dict):
                    self.logger.bind(tag=TAG).error(f"Invalid data format for {module}: expected a dictionary")
                    return {}

                selected_module = config_data_['selected_module'].get(module)
                if selected_module not in config_data_[module]:
                    self.logger.bind(tag=TAG).error(f"Selected {module} not found in config: {selected_module}")
                    return {}

            return config_data_

        except requests.exceptions.RequestException as e:
            self.logger.bind(tag=TAG).error(f"Error fetching config: {e}")
            return {}