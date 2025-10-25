"""
AI分析サービス（月次レポート用）
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not available. AI features will be disabled.")


class AIAnalyzer:
    """AI分析サービス（Gemini API使用）"""
    
    def __init__(self):
        self.gemini_model = None
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.gemini_model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini AI初期化成功: {self.model_name}")
            except Exception as e:
                logger.error(f"Gemini AI初期化失敗: {e}")
                self.gemini_model = None
        else:
            logger.warning("Gemini API設定が不完全です。AI機能は無効になります。")
    
    def analyze_monthly_security_data(self, security_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        月次セキュリティデータのAI分析
        
        Args:
            security_data: セキュリティデータ
                {
                    'ban_history': [...],
                    'system_stats': {...},
                    'fail2ban_stats': {...},
                    'period': '2025-10'
                }
        
        Returns:
            {
                'summary': str,
                'insights': List[str],
                'recommendations': List[str],
                'risk_level': str,
                'trends': Dict[str, Any]
            }
        """
        if not self.gemini_model:
            return self._fallback_analysis(security_data)
        
        try:
            # データを整理
            ban_count = len(security_data.get('ban_history', []))
            system_stats = security_data.get('system_stats', {})
            fail2ban_stats = security_data.get('fail2ban_stats', {})
            period = security_data.get('period', '')
            
            # プロンプト作成
            prompt = f"""
あなたはセキュリティ分析の専門家です。以下の月次セキュリティデータを分析し、包括的なレポートを作成してください。

【分析期間】: {period}

【セキュリティ統計】
- BAN実行回数: {ban_count}回
- アクティブなJail数: {fail2ban_stats.get('active_jails', 0)}個
- 総BAN数: {fail2ban_stats.get('total_banned', 0)}件

【システム状況】
- CPU使用率: {system_stats.get('cpu_percent', 0):.1f}%
- メモリ使用率: {system_stats.get('memory_percent', 0):.1f}%
- ディスク使用率: {system_stats.get('disk_percent', 0):.1f}%

【BAN履歴詳細】
{self._format_ban_history(security_data.get('ban_history', []))}

以下の形式でJSONレスポンスを返してください：

{{
    "summary": "月次セキュリティ状況の要約（100-150文字）",
    "insights": [
        "重要な洞察1",
        "重要な洞察2",
        "重要な洞察3"
    ],
    "recommendations": [
        "推奨事項1",
        "推奨事項2",
        "推奨事項3"
    ],
    "risk_level": "LOW|MEDIUM|HIGH",
    "trends": {{
        "ban_trend": "増加|減少|安定",
        "attack_patterns": "攻撃パターンの分析",
        "system_health": "システム健全性の評価"
    }},
    "monthly_comparison": "前月との比較分析"
}}

必ずJSON形式のみで返答してください。説明文は不要です。
"""
            
            response = self.gemini_model.generate_content(prompt)
            result_text = response.text.strip()
            
            # JSON解析
            try:
                # JSON部分を抽出
                if '```json' in result_text:
                    json_start = result_text.find('```json') + 7
                    json_end = result_text.find('```', json_start)
                    json_text = result_text[json_start:json_end].strip()
                elif '{' in result_text and '}' in result_text:
                    json_start = result_text.find('{')
                    json_end = result_text.rfind('}') + 1
                    json_text = result_text[json_start:json_end]
                else:
                    json_text = result_text
                
                analysis_result = json.loads(json_text)
                logger.info("AI分析完了")
                return analysis_result
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析エラー: {e}")
                return self._fallback_analysis(security_data)
                
        except Exception as e:
            logger.error(f"AI分析エラー: {e}")
            return self._fallback_analysis(security_data)
    
    def _format_ban_history(self, ban_history: List[Dict]) -> str:
        """BAN履歴をフォーマット"""
        if not ban_history:
            return "BAN履歴なし"
        
        formatted = []
        for ban in ban_history[:10]:  # 最新10件のみ
            formatted.append(f"- {ban.get('ip', 'N/A')} | {ban.get('jail', 'N/A')} | {ban.get('timestamp', 'N/A')}")
        
        return "\n".join(formatted)
    
    def _fallback_analysis(self, security_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI利用不可時のフォールバック分析"""
        ban_count = len(security_data.get('ban_history', []))
        
        # 基本的な分析
        if ban_count == 0:
            risk_level = "LOW"
            summary = "今月はセキュリティインシデントが発生していません。システムは正常に稼働しています。"
        elif ban_count < 5:
            risk_level = "LOW"
            summary = f"今月は{ban_count}件のBANが実行されました。軽微な攻撃試行がありましたが、システムは正常に防御しています。"
        elif ban_count < 20:
            risk_level = "MEDIUM"
            summary = f"今月は{ban_count}件のBANが実行されました。中程度の攻撃活動が観測されています。"
        else:
            risk_level = "HIGH"
            summary = f"今月は{ban_count}件のBANが実行されました。高い攻撃活動が観測されています。"
        
        return {
            "summary": summary,
            "insights": [
                f"BAN実行回数: {ban_count}回",
                "システムは正常に稼働中",
                "Fail2banが適切に機能している"
            ],
            "recommendations": [
                "定期的なセキュリティアップデートの適用",
                "ログの定期的な監視",
                "必要に応じてセキュリティ設定の見直し"
            ],
            "risk_level": risk_level,
            "trends": {
                "ban_trend": "安定" if ban_count < 10 else "増加",
                "attack_patterns": "一般的な攻撃パターン",
                "system_health": "良好"
            },
            "monthly_comparison": "前月との比較データが不足しています"
        }
