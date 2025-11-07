#!/usr/bin/env python3
"""
月次AI分析レポート自動送信スケジューラー
毎月1日に月次AI分析レポートを自動生成・送信
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

from app import get_system_status_data, get_fail2ban_status_data, get_docker_status_data
from utils.email_sender import EmailSender

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monthly_ai_report.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def send_monthly_ai_report():
    """月次AI分析レポートを生成・送信"""
    try:
        logger.info("月次AI分析レポート生成開始")
        
        # システムデータを取得
        system_data = get_system_status_data()
        fail2ban_data = get_fail2ban_status_data()
        docker_data = get_docker_status_data()
        
        # AI分析レポート内容を生成
        from app import generate_monthly_ai_report_data
        report_data = generate_monthly_ai_report_data(system_data, fail2ban_data, docker_data)
        
        # レポートファイル用の完全なレポート内容を生成
        ai_analysis = report_data.get('ai_analysis', {})
        ban_history = report_data.get('ban_history', [])
        
        # BAN履歴の詳細リストを生成
        ban_history_list = ""
        if ban_history:
            ban_history_list = "\n".join([
                f"- {ban.get('timestamp', 'N/A')} | {ban.get('ip', 'N/A')} | {ban.get('jail', 'N/A')}"
                for ban in ban_history[:100]  # 最新100件まで
            ])
            if len(ban_history) > 100:
                ban_history_list += f"\n... 他 {len(ban_history) - 100}件"
        else:
            ban_history_list = "なし"
        
        full_report_content = f"""
月次AI分析レポート
==================

期間: {report_data.get('period', '不明')}

【システム状況】
- CPU使用率: {report_data.get('system_metrics', {}).get('cpu_usage', 0):.1f}%
- メモリ使用率: {report_data.get('system_metrics', {}).get('memory_usage', 0):.1f}%
- ディスク使用率: {report_data.get('system_metrics', {}).get('disk_usage', 0):.1f}%

【セキュリティ状況】
- 総BAN数: {report_data.get('security_metrics', {}).get('total_bans', 0)}件
- アクティブなJail数: {report_data.get('security_metrics', {}).get('active_jails', 0)}個

【コンテナ状況】
- 稼働中コンテナ: {report_data.get('container_metrics', {}).get('running_containers', 0)}/{report_data.get('container_metrics', {}).get('total_containers', 0)}個

【AI分析結果】
サマリー: {ai_analysis.get('summary', 'AI分析結果なし')}
リスクレベル: {ai_analysis.get('risk_level', 'UNKNOWN')}

重要な洞察:
{chr(10).join([f'- {i}' for i in ai_analysis.get('insights', [])])}

推奨事項:
{chr(10).join([f'- {r}' for r in ai_analysis.get('recommendations', [])])}

【過去30日間のBAN履歴詳細】
総件数: {len(ban_history)}件

{ban_history_list}
"""
        
        # レポートファイルを保存（完全版）
        # NAS環境では統合データディレクトリを使用、ローカル環境では相対パスを使用
        if os.getenv('NAS_MODE') == 'true' and os.path.exists('/app/reports'):
            report_dir = Path('/app/reports')
        else:
            report_dir = Path('/Users/Yoshi/nas-project/data/reports')
        
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f"monthly_ai_report_{timestamp}.txt"
        report_file.write_text(full_report_content, encoding='utf-8')
        
        logger.info(f"月次AI分析レポートファイル保存完了: {report_file}")
        
        # メール送信
        email_to = os.getenv('EMAIL_TO')
        if not email_to:
            logger.error("EMAIL_TO環境変数が設定されていません")
            return False
        
        email_sender = EmailSender()
        
        # メール送信（report_dataは既にgenerate_monthly_ai_report_dataの返り値）
        # report_dataにはai_analysis、system_metrics、security_metrics、container_metricsが含まれている
        # report_contentは空文字列（メール本文には既に全ての情報が含まれているため）
        success = email_sender.send_monthly_ai_report(email_to, "", report_data)
        
        if success:
            logger.info("月次AI分析レポートメール送信完了")
            return True
        else:
            logger.error("月次AI分析レポートメール送信失敗")
            return False
            
    except Exception as e:
        logger.error(f"月次AI分析レポート生成・送信エラー: {e}", exc_info=True)
        
        # エラー通知メールを送信
        try:
            email_to = os.getenv('EMAIL_TO')
            if email_to:
                email_sender = EmailSender()
                email_sender.send_error_notification(
                    email_to,
                    "月次AI分析レポート生成・送信エラー",
                    str(e)
                )
        except Exception as email_error:
            logger.error(f"エラー通知メール送信失敗: {email_error}")
        
        return False

def check_and_send_monthly_report():
    """毎日チェックして、1日の場合に月次レポートを送信"""
    try:
        today = datetime.now()
        if today.day == 1:  # 毎月1日の場合
            logger.info(f"今日は{today.month}月1日です。月次AI分析レポートを送信します。")
            return send_monthly_ai_report()
        else:
            logger.debug(f"今日は{today.day}日です。月次レポートの送信日ではありません。")
            return True
    except Exception as e:
        logger.error(f"月次レポートチェックエラー: {e}")
        return False

def main():
    """メイン関数"""
    try:
        # 環境変数の確認
        required_env_vars = ['EMAIL_USER', 'EMAIL_PASSWORD', 'EMAIL_TO', 'GEMINI_API_KEY']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"必要な環境変数が設定されていません: {', '.join(missing_vars)}")
            return 1
        
        # 月次AI分析レポート設定
        report_enabled = os.getenv('MONTHLY_AI_REPORT_ENABLED', 'true').lower() == 'true'
        if not report_enabled:
            logger.info("月次AI分析レポートが無効化されています")
            return 0
        
        # 毎月1日朝10時に固定
        report_time = os.getenv('MONTHLY_AI_REPORT_TIME', '10:00')
        
        logger.info("============================================================")
        logger.info("月次AI分析レポート自動送信システムを起動しました")
        logger.info(f"スケジュール設定: 毎月1日 {report_time}")
        logger.info(f"送信先: {os.getenv('EMAIL_TO')}")
        logger.info("============================================================")
        
        # スケジュール設定（毎月1日）
        # scheduleライブラリにはmonth属性がないため、毎日チェックして1日の場合に実行
        schedule.every().day.at(report_time).do(check_and_send_monthly_report)
        
        # 初回テスト実行（オプション）
        if os.getenv('MONTHLY_AI_REPORT_TEST', 'false').lower() == 'true':
            logger.info("テスト実行を開始します...")
            send_monthly_ai_report()
        
        # 強制テスト実行（デバッグ用）
        if os.getenv('FORCE_MONTHLY_TEST', 'false').lower() == 'true':
            logger.info("強制テスト実行を開始します...")
            send_monthly_ai_report()
        
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
