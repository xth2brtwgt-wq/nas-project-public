# Gemini API 代替案（既存APIキー流用）

既存システムで使用しているGemini APIキーを流用する方法です。

## メリット
- ✅ 既存のAPIキーが使える
- ✅ コストが安い（OpenAIより低価格）
- ✅ 日本語に強い

## 実装手順

### 1. 依存関係を追加

requirements.txtに追加：
```
google-generativeai==0.8.3
```

### 2. AI Analyzerを修正

`app/services/ai_analyzer.py`を修正してGemini対応：

```python
import google.generativeai as genai
from config.settings import settings

class AIAnalyzer:
    def __init__(self, db: Session):
        self.db = db
        self.use_gemini = False
        
        # Geminiを優先して使用
        if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.use_gemini = True
        elif settings.OPENAI_API_KEY:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.use_gemini = False
        else:
            self.client = None
            
    def classify_product_category(self, product_name: str) -> Optional[str]:
        if self.use_gemini:
            # Gemini版
            prompt = f"以下の商品を適切なカテゴリに分類してください。\\n\\n商品名: {product_name}\\n\\nカテゴリ: 食品・飲料、日用品・消耗品、家電・PC関連、本・メディア、ファッション、ホビー・趣味、健康・美容、ペット用品、その他\\n\\n最も適切なカテゴリ名を1つだけ返してください。"
            response = self.model.generate_content(prompt)
            return response.text.strip()
        else:
            # OpenAI版（既存コード）
            ...
```

### 3. 設定ファイルを更新

`config/settings.py`に追加：
```python
class Settings(BaseSettings):
    # ... 既存の設定 ...
    
    # AI Provider (gemini or openai)
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
```

### 4. 環境変数を設定

`.env`ファイル：
```env
# Gemini API (既存のキーを流用)
GEMINI_API_KEY=your_existing_gemini_key

# OpenAI (オプション)
# OPENAI_API_KEY=
```

## どちらを選ぶべきか？

| 項目 | OpenAI | Gemini |
|-----|--------|--------|
| コスト | 💰💰 | 💰 |
| 日本語精度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 実装済み | ✅ | 要修正 |
| 既存キー流用 | ❌ | ✅ |

## 推奨

1. **今すぐ使いたい** → OpenAI API取得（実装済み）
2. **コスト重視** → Gemini API実装（上記手順で対応）
3. **両方使いたい** → 両方設定して切り替え可能に

