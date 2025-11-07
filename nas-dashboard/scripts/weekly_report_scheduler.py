#!/usr/bin/env python3
"""
週次レポート自動送信スケジューラー
毎週指定された曜日・時刻に週次レポートを自動生成・送信
"""

import os
import sys
import schedule
import time
import logging
from datetime import datetime
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import get_system_status_data, get_fail2ban_status_data, get_docker_status_data, generate_report_content
from utils.email_sender import EmailSender

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/weekly_report.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def send_weekly_report():
    """週次レポートを生成・送信"""
    try:
        logger.info("週次レポート生成開始")
        
        # システムデータを取得
        system_data = get_system_status_data()
        fail2ban_data = get_fail2ban_status_data()
        docker_data = get_docker_status_data()
        
        # レポート内容を生成
        report_content = generate_report_content(system_data, fail2ban_data, docker_data)
        
        # レポートファイルを保存
        # NAS環境では統合データディレクトリを使用、ローカル環境では相対パスを使用
        if os.getenv('NAS_MODE') == 'true' and os.path.exists('/app/reports'):
            report_dir = Path('/app/reports')
        else:
            report_dir = Path('/Users/Yoshi/nas-project/data/reports')
        
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f"weekly_report_{timestamp}.txt"
        report_file.write_text(report_content, encoding='utf-8')
        
        logger.info(f"レポートファイル保存完了: {report_file}")
        
        # メール送信
        email_to = os.getenv('EMAIL_TO')
        if not email_to:
            logger.error("EMAIL_TO環境変数が設定されていません")
            return False
        
        email_sender = EmailSender()
        
        # レポートデータを準備
        report_data = {
            'system_data': system_data,
            'fail2ban_data': fail2ban_data,
            'docker_data': docker_data
        }
        
        # メール送信
        success = email_sender.send_weekly_report(email_to, report_content, report_data)
        
        if success:
            logger.info("週次レポートメール送信完了")
            return True
        else:
            logger.error("週次レポートメール送信失敗")
            return False
            
    except Exception as e:
        logger.error(f"週次レポート生成・送信エラー: {e}", exc_info=True)
        
        # エラー通知メールを送信
        try:
            email_to = os.getenv('EMAIL_TO')
            if email_to:
                email_sender = EmailSender()
                email_sender.send_error_notification(
                    email_to,
                    "週次レポート生成・送信エラー",
                    str(e)
                )
        except Exception as email_error:
            logger.error(f"エラー通知メール送信失敗: {email_error}")
        
        return False

def main():
    """メイン関数"""
    try:
        # 環境変数の確認
        required_env_vars = ['EMAIL_USER', 'EMAIL_PASSWORD', 'EMAIL_TO']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"必要な環境変数が設定されていません: {', '.join(missing_vars)}")
            return 1
        
        # 週次レポート設定
        report_enabled = os.getenv('WEEKLY_REPORT_ENABLED', 'true').lower() == 'true'
        if not report_enabled:
            logger.info("週次レポートが無効化されています")
            return 0
        
        # 毎週月曜日朝9時に固定
        report_day = int(os.getenv('WEEKLY_REPORT_DAY', '0'))  # 0=月曜日
        report_time = os.getenv('WEEKLY_REPORT_TIME', '09:00')
        
        # 曜日の設定（月曜日に固定）
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        target_day = days[report_day]  # 0=月曜日
        
        logger.info("============================================================")
        logger.info("週次レポート自動送信システムを起動しました")
        logger.info(f"スケジュール設定: 毎週{target_day} {report_time}")
        logger.info(f"送信先: {os.getenv('EMAIL_TO')}")
        logger.info("============================================================")
        
        # スケジュール設定
        getattr(schedule.every(), target_day).at(report_time).do(send_weekly_report)
        
        # 初回テスト実行（オプション）
        if os.getenv('WEEKLY_REPORT_TEST', 'false').lower() == 'true':
            logger.info("テスト実行を開始します...")
            send_weekly_report()
        
        # スケジューラーを実行
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1分ごとにチェック
            
    except KeyboardInterrupt:
        logger.info("スケジューラーを停止しました")
        return 0
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
