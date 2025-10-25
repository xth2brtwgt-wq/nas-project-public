import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class EmailSender:
    """メール送信クラス"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_from = os.getenv('EMAIL_FROM', self.email_user)
        
    def send_sync_report(self, to_email: str, sync_result: Dict[str, Any]) -> bool:
        """同期結果レポートをメールで送信"""
        try:
            if not self.email_user or not self.email_password:
                raise Exception("メール設定が不完全です")
            
            # メールの作成
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = to_email
            
            # 件名の設定
            execution_date = sync_result.get('execution_date', datetime.now().strftime('%Y/%m/%d'))
            msg['Subject'] = f"[Insta360同期] 実行結果 - {execution_date}"
            
            # メール本文の作成
            body = self._create_sync_report_body(sync_result)
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # メール送信
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_from, to_email, text)
            server.quit()
            
            logger.info(f"同期レポートメール送信完了: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"同期レポートメール送信エラー: {str(e)}")
            raise Exception(f"メール送信に失敗しました: {str(e)}")
    
    def send_error_notification(self, to_email: str, error_message: str, error_details: str = "") -> bool:
        """エラー通知メールを送信"""
        try:
            if not self.email_user or not self.email_password:
                raise Exception("メール設定が不完全です")
            
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = to_email
            msg['Subject'] = f"[Insta360同期] エラー通知 - {datetime.now().strftime('%Y/%m/%d %H:%M')}"
            
            body = f"""
Insta360自動同期システムでエラーが発生しました。

【エラー情報】
発生時刻: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
エラーメッセージ: {error_message}

【詳細】
{error_details if error_details else '詳細情報なし'}

【対処方法】
1. ログファイルを確認してください: logs/insta360_sync.log
2. Mac側のSMB共有が有効か確認してください
3. ネットワーク接続を確認してください
4. 問題が解決しない場合は管理者に連絡してください

---
Insta360自動同期システム v1.0.0
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_from, to_email, text)
            server.quit()
            
            logger.info(f"エラー通知メール送信完了: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"エラー通知メール送信エラー: {str(e)}")
            raise Exception(f"エラー通知メール送信に失敗しました: {str(e)}")
    
    def _create_sync_report_body(self, sync_result: Dict[str, Any]) -> str:
        """同期レポートの本文を作成"""
        execution_date = sync_result.get('execution_date', '不明')
        execution_time = sync_result.get('execution_time', '不明')
        total_files = sync_result.get('total_files', 0)
        total_size = sync_result.get('total_size', 0)
        success_files = sync_result.get('success_files', 0)
        failed_files = sync_result.get('failed_files', 0)
        skipped_files = sync_result.get('skipped_files', 0)
        success_list = sync_result.get('success_list', [])
        failed_list = sync_result.get('failed_list', [])
        skipped_list = sync_result.get('skipped_list', [])
        
        # サイズを人間が読みやすい形式に変換
        size_mb = total_size / (1024 * 1024) if total_size > 0 else 0
        
        body = f"""
Insta360自動同期が完了しました。

【実行結果】
実行日時: {execution_date} {execution_time}
転送ファイル数: {total_files}件
総容量: {size_mb:.2f} MB
転送成功: {success_files}件
転送失敗: {failed_files}件
スキップ済み: {skipped_files}件

【詳細結果】
"""
        
        # 成功したファイルの詳細
        if success_list:
            body += "\n【転送成功ファイル】\n"
            for file_info in success_list:
                file_size_mb = file_info.get('size', 0) / (1024 * 1024)
                body += f"- {file_info.get('filename', '不明')} ({file_size_mb:.2f} MB) - 成功\n"
        
        # スキップされたファイルの詳細
        if skipped_list:
            body += "\n【スキップ済みファイル】\n"
            for file_info in skipped_list:
                file_size_mb = file_info.get('size', 0) / (1024 * 1024)
                body += f"- {file_info.get('filename', '不明')} ({file_size_mb:.2f} MB) - スキップ済み\n"
        
        # 失敗したファイルの詳細
        if failed_list:
            body += "\n【転送失敗ファイル】\n"
            for file_info in failed_list:
                file_size_mb = file_info.get('size', 0) / (1024 * 1024)
                error_msg = file_info.get('error', '不明なエラー')
                body += f"- {file_info.get('filename', '不明')} ({file_size_mb:.2f} MB) - 失敗: {error_msg}\n"
        
        # 転送対象ファイルがない場合
        if total_files == 0:
            body += "\n転送対象のInsta360ファイルは見つかりませんでした。\n"
        
        body += f"""
---
Insta360自動同期システム v1.0.0
        """
        
        return body
    
    def test_connection(self) -> bool:
        """メール接続テスト"""
        try:
            if not self.email_user or not self.email_password:
                logger.error("メール設定が不完全です")
                return False
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.quit()
            
            logger.info("メール接続テスト成功")
            return True
            
        except Exception as e:
            logger.error(f"メール接続テスト失敗: {str(e)}")
            return False