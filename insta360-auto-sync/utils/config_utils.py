import json
import os
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    """設定管理クラス"""
    
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        config_file = self.config_dir / f"{config_name}.json"
        
        if not config_file.exists():
            logger.warning(f"設定ファイルが見つかりません: {config_file}")
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"設定ファイルを読み込みました: {config_file}")
            return config
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー {config_file}: {e}")
            return {}
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """設定ファイルを保存"""
        config_file = self.config_dir / f"{config_name}.json"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            logger.info(f"設定ファイルを保存しました: {config_file}")
            return True
        except Exception as e:
            logger.error(f"設定ファイル保存エラー {config_file}: {e}")
            return False

def load_environment_config() -> Dict[str, Any]:
    """環境変数から設定を読み込み"""
    config = {
        'sync': {
            'source_path': os.getenv('SOURCE_PATH', '/source'),
            'destination_path': os.getenv('DESTINATION_PATH', '/volume2/data/insta360')
        },
        'email': {
            'to_email': os.getenv('TO_EMAIL', '')
        }
    }
    
    logger.info("環境変数設定を読み込みました")
    return config