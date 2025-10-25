import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class EmailSender:
    """メール送信クラス"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_from = os.getenv('EMAIL_FROM', self.email_user)
        
    def send_weekly_report(self, to_email: str, report_content: str, report_data: Dict[str, Any]) -> bool:
        """週次レポートをメールで送信"""
        try:
            if not self.email_user or not self.email_password:
                raise Exception("メール設定が不完全です")
            
            # メールの作成
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = to_email
            
            # 件名の設定
            current_date = datetime.now().strftime('%Y/%m/%d')
            msg['Subject'] = f"[NAS管理] 週次セキュリティ・システムレポート - {current_date}"
            
            # メール本文の作成
            body = self._create_weekly_report_body(report_content, report_data)
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # メール送信
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_from, to_email, text)
            server.quit()
            
            logger.info(f"週次レポートメール送信完了: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"週次レポートメール送信エラー: {str(e)}")
            raise Exception(f"メール送信に失敗しました: {str(e)}")
    
    def send_error_notification(self, to_email: str, error_message: str, error_details: str = "") -> bool:
        """エラー通知メールを送信"""
        try:
            if not self.email_user or not self.email_password:
                raise Exception("メール設定が不完全です")
            
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = to_email
            msg['Subject'] = f"[NAS管理] エラー通知 - {datetime.now().strftime('%Y/%m/%d %H:%M')}"
            
            body = f"""
NAS統合管理システムでエラーが発生しました。

【エラー情報】
発生時刻: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
エラーメッセージ: {error_message}

【詳細】
{error_details if error_details else '詳細情報なし'}

【対処方法】
1. システムログを確認してください
2. 各サービスの状態を確認してください
3. 問題が解決しない場合は管理者に連絡してください

---
NAS統合管理システム
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
    
    def send_monthly_report(self, to_email: str, report_content: str, ai_analysis: Dict[str, Any]) -> bool:
        """月次AI分析レポートをメールで送信"""
        try:
            # メール内容を作成
            subject = f"NAS月次AI分析セキュリティレポート - {datetime.now().strftime('%Y年%m月')}"
            
            # AI分析結果を取得
            summary = ai_analysis.get('summary', '分析結果なし')
            risk_level = ai_analysis.get('risk_level', 'UNKNOWN')
            insights = ai_analysis.get('insights', [])
            recommendations = ai_analysis.get('recommendations', [])
            
            # HTMLメール本文を作成
            html_body = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .ai-summary {{ background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .risk-level {{ font-weight: bold; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                    .risk-low {{ background-color: #d4edda; color: #155724; }}
                    .risk-medium {{ background-color: #fff3cd; color: #856404; }}
                    .risk-high {{ background-color: #f8d7da; color: #721c24; }}
                    .insights {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .recommendations {{ background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>🤖 NAS月次AI分析セキュリティレポート</h2>
                    <p><strong>分析期間:</strong> {datetime.now().strftime('%Y年%m月')}</p>
                    <p><strong>生成日時:</strong> {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
                </div>
                
                <div class="ai-summary">
                    <h3>🧠 AI分析サマリー</h3>
                    <p>{summary}</p>
                </div>
                
                <div class="risk-level risk-{risk_level.lower()}">
                    <h3>⚠️ リスクレベル: {risk_level}</h3>
                </div>
                
                <div class="insights">
                    <h3>💡 重要な洞察</h3>
                    <ul>
                        {''.join([f'<li>{insight}</li>' for insight in insights])}
                    </ul>
                </div>
                
                <div class="recommendations">
                    <h3>📋 AI推奨事項</h3>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in recommendations])}
                    </ul>
                </div>
                
                <div style="margin-top: 30px;">
                    <h3>📊 詳細レポート</h3>
                    <pre style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; font-family: monospace; font-size: 12px;">{report_content}</pre>
                </div>
                
                <div class="footer">
                    <p>このレポートはAI分析により自動生成されました。</p>
                    <p>NAS統合管理システム - Gemini 2.0 Flash AI</p>
                </div>
            </body>
            </html>
            """
            
            # メール送信
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = to_email
            
            # HTML本文を追加
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # プレーンテキスト版も追加
            text_part = MIMEText(report_content, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # SMTPサーバーに接続して送信
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"月次AI分析レポートメール送信完了: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"月次AI分析レポートメール送信エラー: {e}")
            return False
    
    def _create_weekly_report_body(self, report_content: str, report_data: Dict[str, Any]) -> str:
        """週次レポートの本文を作成"""
        current_date = datetime.now().strftime('%Y年%m月%d日')
        
        # レポートデータから重要な情報を抽出
        fail2ban_data = report_data.get('fail2ban_data', {})
        system_data = report_data.get('system_data', {})
        docker_data = report_data.get('docker_data', {})
        
        # サマリー情報
        total_banned = fail2ban_data.get('total_banned', 0)
        active_jails = fail2ban_data.get('active_jails', 0)
        cpu_percent = system_data.get('cpu_percent', 0)
        memory_percent = system_data.get('memory_percent', 0)
        disk_percent = system_data.get('disk_percent', 0)
        running_containers = docker_data.get('running_containers', 0)
        total_containers = docker_data.get('total_containers', 0)
        
        body = f"""
NAS統合管理システム - 週次レポート
生成日時: {current_date}

【セキュリティ状況サマリー】
- 総BAN数: {total_banned}件
- アクティブなJail数: {active_jails}個

【システム状況サマリー】
- CPU使用率: {cpu_percent:.1f}%
- メモリ使用率: {memory_percent:.1f}%
- ディスク使用率: {disk_percent:.1f}%

【Dockerコンテナ状況サマリー】
- 稼働中コンテナ: {running_containers}/{total_containers}個

【詳細レポート】
{report_content}

---
このレポートは自動生成されました。
NAS統合管理システム
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
