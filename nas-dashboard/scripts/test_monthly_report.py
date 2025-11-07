#!/usr/bin/env python3
"""
月次AI分析レポートのテスト実行スクリプト
ローカル環境で月次レポートをテスト実行します
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 環境変数を設定（.envから読み込む）
# 注意: .env.restoreは実行時には使用しない（バックアップ用のみ）
def load_env_file(file_path: Path):
    """環境変数ファイルを読み込む（dotenvなしで）"""
    if not file_path.exists():
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # 既に設定されていない場合のみ設定
                if key not in os.environ:
                    os.environ[key] = value

# .envを使用（.env.restoreは実行時には使用しない）
env_file = project_root / '.env'

if env_file.exists():
    load_env_file(env_file)

# NAS_MODEをfalseに設定（ローカル環境）
os.environ['NAS_MODE'] = 'false'

# テスト実行のインポート
from scripts.monthly_ai_report_scheduler import send_monthly_ai_report
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """メイン関数"""
    try:
        logger.info("=" * 60)
        logger.info("月次AI分析レポート テスト実行開始")
        logger.info("=" * 60)
        
        # 必要な環境変数の確認
        required_env_vars = ['EMAIL_USER', 'EMAIL_PASSWORD', 'EMAIL_TO', 'GEMINI_API_KEY']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"必要な環境変数が設定されていません: {', '.join(missing_vars)}")
            logger.info("\n以下の環境変数を設定してください:")
            for var in missing_vars:
                logger.info(f"  - {var}")
            return 1
        
        # 環境変数の確認表示
        logger.info("\n環境変数設定:")
        logger.info(f"  EMAIL_USER: {os.getenv('EMAIL_USER', '未設定')}")
        logger.info(f"  EMAIL_TO: {os.getenv('EMAIL_TO', '未設定')}")
        logger.info(f"  GEMINI_API_KEY: {'設定済み' if os.getenv('GEMINI_API_KEY') else '未設定'}")
        logger.info(f"  NAS_MODE: {os.getenv('NAS_MODE', 'false')}")
        logger.info("")
        
        # 月次レポートを生成・送信
        logger.info("月次AI分析レポートを生成・送信します...")
        success = send_monthly_ai_report()
        
        if success:
            logger.info("=" * 60)
            logger.info("✅ 月次AI分析レポートのテスト実行が完了しました")
            logger.info("=" * 60)
            return 0
        else:
            logger.error("=" * 60)
            logger.error("❌ 月次AI分析レポートのテスト実行が失敗しました")
            logger.error("=" * 60)
            return 1
            
    except KeyboardInterrupt:
        logger.info("\nテスト実行が中断されました")
        return 1
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())

