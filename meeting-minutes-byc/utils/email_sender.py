#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メール送付機能
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# アプリケーション情報
from config.version import APP_NAME, APP_VERSION

class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_from = os.getenv('EMAIL_FROM', self.email_user)
        
    def send_meeting_minutes(self, to_email, meeting_data, transcript_file_path=None, meeting_file_path=None):
        """議事録をメールで送信"""
        try:
            if not self.email_user or not self.email_password:
                raise Exception("メール設定が不完全です")
            
            # メールの作成
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = to_email
            # メール件名の設定（日時フォーマットを修正）
            meeting_date_for_subject = self._format_datetime_for_email(meeting_data.get('meeting_date', '会議'))
            msg['Subject'] = f"議事録 - {meeting_date_for_subject}"
            
            # 処理結果の確認
            notion_sent = meeting_data.get('notion_sent', False)
            notion_error = meeting_data.get('notion_error', '')
            
            # 日時形式を変換
            formatted_meeting_date = self._format_datetime_for_email(meeting_data.get('meeting_date', '未設定'))
            
            # ファイル名から拡張子を除去
            filename = meeting_data.get('filename', 'unknown')
            filename_without_ext = os.path.splitext(filename)[0]
            
            # メール本文の作成
            body = f"""
議事録が生成されました。

【基本情報】
会議日時: {formatted_meeting_date}
ファイル名: {filename}
処理日時: {self._format_datetime_for_email(meeting_data.get('timestamp', '不明'))}
ファイルサイズ: {meeting_data.get('file_size', 0) / 1024 / 1024:.2f} MB

【処理結果】
✅ 音声ファイルアップロード: 完了
✅ 音声文字起こし: 完了
✅ 議事録生成: 完了
✅ Markdownファイル生成: 完了
{'✅ Notion登録: 完了' if notion_sent else f'❌ Notion登録: エラー ({notion_error})' if notion_error else '⚠️ Notion登録: 未設定'}

【添付ファイル】
- 文字起こしファイル: transcript_{filename_without_ext}.txt
- 議事録ファイル: meeting_minutes_{filename_without_ext}.md

---
{APP_NAME} v{APP_VERSION} で生成されました。
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 文字起こしファイルの添付
            if transcript_file_path and os.path.exists(transcript_file_path):
                with open(transcript_file_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= transcript_{filename_without_ext}.txt'
                    )
                    msg.attach(part)
            
            # 議事録ファイルの添付
            if meeting_file_path and os.path.exists(meeting_file_path):
                with open(meeting_file_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= meeting_minutes_{filename_without_ext}.md'
                    )
                    msg.attach(part)
            
            # メール送信
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_from, to_email, text)
            server.quit()
            
            logger.info(f"メール送信完了: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"メール送信エラー: {str(e)}")
            raise Exception(f"メール送信に失敗しました: {str(e)}")
    
    def _format_datetime_for_email(self, datetime_str):
        """日時文字列をメール用の形式に変換"""
        if not datetime_str or datetime_str == '未設定':
            return '未設定'
        
        try:
            # ISO形式の日時をパース
            if 'T' in datetime_str:
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            else:
                # その他の形式を試行
                dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            
            # YYYY/MM/DD HH24:Mi形式に変換
            return dt.strftime('%Y/%m/%d %H:%M')
        except ValueError:
            # パースできない場合は元の文字列を返す
            return datetime_str
    
    def send_notification(self, to_email, subject, message):
        """通知メールを送信"""
        try:
            if not self.email_user or not self.email_password:
                raise Exception("メール設定が不完全です")
            
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_from, to_email, text)
            server.quit()
            
            logger.info(f"通知メール送信完了: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"通知メール送信エラー: {str(e)}")
            raise Exception(f"通知メール送信に失敗しました: {str(e)}")
