"""
AI要約・分類サービス（ハイブリッド対応）
"""
import google.generativeai as genai
from config.settings import settings
import logging
import json

logger = logging.getLogger(__name__)


class AIService:
    """AI要約・分類のハイブリッドサービス"""
    
    def __init__(self):
        self.provider = settings.ai_provider
        
        if self.provider == "gemini" and settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel(settings.gemini_model)
                logger.info(f"Gemini AI 初期化成功: {settings.gemini_model}")
            except Exception as e:
                logger.error(f"Gemini AI 初期化失敗: {e}")
                raise
    
    async def analyze_document(self, text: str, filename: str = "") -> dict:
        """
        ドキュメントのAI分析
        
        Args:
            text: OCR抽出テキスト
            filename: ファイル名（ヒント用）
        
        Returns:
            {
                "summary": str,
                "category": str,
                "keywords": list[str],
                "metadata": dict
            }
        """
        try:
            if self.provider == "gemini":
                return await self._gemini_analyze(text, filename)
            else:
                # フォールバック：基本的な分析
                return self._basic_analyze(text, filename)
                
        except Exception as e:
            logger.error(f"AI分析エラー: {e}")
            # エラー時もフォールバック
            return self._basic_analyze(text, filename)
    
    async def _gemini_analyze(self, text: str, filename: str) -> dict:
        """Gemini APIで分析"""
        try:
            prompt = f"""
あなたは文書分析の専門家です。以下の文書を分析してください。

【ファイル名】
{filename}

【文書内容】
{text[:5000]}  # 最初の5000文字

以下の情報をJSON形式で出力してください：

1. summary: 文書の要約（100-200文字）

2. category: カテゴリ
   まず、以下のよく使うカテゴリに該当するか確認してください：
   - 請求書・領収書
   - 契約書・同意書
   - 見積書・提案書
   - 会議資料・報告書
   - プレゼンテーション資料
   - 医療・健康記録
   - 税務・確定申告関連
   - 保険関連
   - 公的書類
   - メモ・手書きノート
   - 名刺
   - レシート
   
   上記に該当しない場合は、文書の内容から最も適切なカテゴリ名を生成してください。
   例：
   - 「家電 説明書」の文書 → 「製品マニュアル・説明書」
   - 「料理レシピ」の文書 → 「レシピ・料理」
   - 「旅行プラン」の文書 → 「旅行・観光」
   - 「研究論文」の文書 → 「学術・研究」
   
   カテゴリ名は2-4単語程度で、わかりやすく簡潔に命名してください。

3. keywords: 重要キーワード（5-10個のリスト）

4. metadata: 抽出したメタデータ（該当するものがあれば）
   {{
     "title": "文書タイトル",
     "date": "日付（YYYY-MM-DD形式）",
     "author": "作成者・発行者",
     "manufacturer": "メーカー名（製品の場合）",
     "model": "型番（製品の場合）",
     "amount": 金額（数値）,
     "company": "会社名",
     "custom": その他の情報
   }}

必ずJSON形式のみで返答してください。説明文は不要です。
"""
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # JSONパース
            # マークダウンのコードブロックを除去
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            result = json.loads(result_text.strip())
            
            logger.info(f"Gemini分析成功: カテゴリ={result.get('category')}")
            
            return {
                "summary": result.get("summary", ""),
                "category": result.get("category", "その他"),
                "keywords": result.get("keywords", []),
                "metadata": result.get("metadata", {})
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {e}, レスポンス: {result_text[:200]}")
            return self._basic_analyze(text, filename)
        except Exception as e:
            logger.error(f"Gemini分析エラー: {e}")
            return self._basic_analyze(text, filename)
    
    def _basic_analyze(self, text: str, filename: str) -> dict:
        """基本的な分析（フォールバック）"""
        try:
            # 簡単な要約（最初の200文字）
            summary = text[:200].replace("\n", " ").strip()
            if len(text) > 200:
                summary += "..."
            
            # ファイル名からカテゴリ推測
            category = self._guess_category_from_filename(filename)
            
            # キーワード抽出（頻出単語）
            keywords = self._extract_keywords(text)
            
            return {
                "summary": summary,
                "category": category,
                "keywords": keywords,
                "metadata": {}
            }
            
        except Exception as e:
            logger.error(f"基本分析エラー: {e}")
            return {
                "summary": "分析に失敗しました",
                "category": "その他",
                "keywords": [],
                "metadata": {}
            }
    
    def _guess_category_from_filename(self, filename: str) -> str:
        """ファイル名からカテゴリを推測"""
        filename_lower = filename.lower()
        
        if any(word in filename_lower for word in ["請求", "invoice", "bill"]):
            return "請求書・領収書"
        elif any(word in filename_lower for word in ["契約", "contract", "agreement"]):
            return "契約書・同意書"
        elif any(word in filename_lower for word in ["見積", "estimate", "quote"]):
            return "見積書・提案書"
        elif any(word in filename_lower for word in ["会議", "meeting", "議事録"]):
            return "会議資料・報告書"
        elif any(word in filename_lower for word in ["名刺", "card"]):
            return "名刺"
        elif any(word in filename_lower for word in ["レシート", "receipt"]):
            return "レシート"
        else:
            return "その他"
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> list[str]:
        """簡単なキーワード抽出"""
        # 簡易的な実装（本来はTF-IDFやMeCabを使うべき）
        import re
        from collections import Counter
        
        # 日本語と英数字を抽出
        words = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\w]+', text)
        
        # 長さが2文字以上の単語のみ
        words = [w for w in words if len(w) >= 2]
        
        # 頻出単語
        counter = Counter(words)
        keywords = [word for word, count in counter.most_common(max_keywords)]
        
        return keywords
    
    async def generate_combined_summary(self, documents_data: list[dict], title: str) -> str:
        """
        複数文書の統合要約
        
        Args:
            documents_data: [{"filename": str, "summary": str, "category": str}, ...]
            title: タイトル
        
        Returns:
            統合要約のマークダウンテキスト
        """
        try:
            if self.provider == "gemini":
                return await self._gemini_combined_summary(documents_data, title)
            else:
                return self._basic_combined_summary(documents_data, title)
                
        except Exception as e:
            logger.error(f"統合要約エラー: {e}")
            return self._basic_combined_summary(documents_data, title)
    
    async def _gemini_combined_summary(self, documents_data: list[dict], title: str) -> str:
        """Geminiで統合要約"""
        try:
            # ファイル名リストを作成
            file_list = "\n".join([
                f"{i+1}. {doc['filename']} ({doc['category']})"
                for i, doc in enumerate(documents_data)
            ])
            
            docs_text = "\n\n".join([
                f"### 文書{i+1}: {doc['filename']}\n"
                f"カテゴリ: {doc['category']}\n"
                f"要約: {doc['summary']}"
                for i, doc in enumerate(documents_data)
            ])
            
            prompt = f"""
以下の複数の文書をまとめた統合レポートを作成してください。

【タイトル】
{title}

【対象文書一覧】
{file_list}

【各文書の詳細】
{docs_text}

以下の形式でマークダウンで出力してください。
**必ず「対象文書一覧」セクションを最初に含めて、元ファイル名を明記してください。**

# {title}

## 対象文書一覧
{file_list}

## 概要
全体的な要約を200-300文字で記載

## 主要なポイント
- ポイント1
- ポイント2
- ポイント3

## カテゴリ別サマリー
各カテゴリごとにまとめる。各カテゴリの説明で該当するファイル名を明記すること。

## 重要事項
特に注目すべき点

## 推奨アクション
必要に応じて推奨される次のアクションを記載
"""
            
            response = self.model.generate_content(prompt)
            summary_text = response.text.strip()
            
            logger.info(f"統合要約生成成功: {len(summary_text)}文字")
            
            return summary_text
            
        except Exception as e:
            logger.error(f"Gemini統合要約エラー: {e}")
            return self._basic_combined_summary(documents_data, title)
    
    def _basic_combined_summary(self, documents_data: list[dict], title: str) -> str:
        """基本的な統合要約"""
        from datetime import datetime
        
        lines = [
            f"# {title}",
            "",
            f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"文書数: {len(documents_data)}",
            "",
            "## 文書一覧",
            ""
        ]
        
        # カテゴリ別に分類
        by_category = {}
        for doc in documents_data:
            category = doc.get("category", "その他")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(doc)
        
        for category, docs in by_category.items():
            lines.append(f"### {category} ({len(docs)}件)")
            lines.append("")
            for doc in docs:
                lines.append(f"- **{doc['filename']}**")
                if doc.get("summary"):
                    lines.append(f"  - {doc['summary'][:200]}")
            lines.append("")
        
        return "\n".join(lines)


# シングルトンインスタンス
ai_service = AIService()

