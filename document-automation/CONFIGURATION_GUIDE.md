# 設定ガイド v1.0.0

リリースに必要な設定項目の詳細ガイドです。

## 📌 バージョン情報

- **バージョン**: v1.0.0
- **リリース名**: 初期リリース版
- **リリース日**: 2025-10-19

## 🚀 クイック設定（5分で完了）

### Step 1: 設定ファイル作成

```bash
cd /Users/Yoshi/nas-project/document-automation
cp .env.template .env
```

### Step 2: 必須項目の設定

```bash
nano .env
```

最低限、以下の項目を設定してください：

```bash
# 1. Gemini APIキー（必須）
GEMINI_API_KEY=あなたのAPIキーをここに貼り付け

# 2. セキュリティキー（必須）
SECRET_KEY=ここにランダム文字列

# 3. 同時処理数（メモリに応じて）
MAX_CONCURRENT_TASKS=3  # 8GBの場合
```

### Step 3: 完了！

これだけで動作します。デプロイ可能です！

---

## 📋 詳細設定ガイド

### 1. Gemini API キー 🔴 必須

**目的**: AI要約・分類機能に使用

**取得方法**:
1. https://makersuite.google.com/app/apikey にアクセス
2. Googleアカウントでログイン
3. 「Create API Key」をクリック
4. 表示されたキー（`AIza...`で始まる）をコピー

**設定例**:
```bash
GEMINI_API_KEY=AIzaSyDc1234567890abcdefghijklmnopqrstu
```

**料金**:
- 無料枠: 月60リクエスト/分
- 有料: $0.075-0.30 / 1M tokens

**確認方法**:
```bash
# 正しく設定されているか確認
echo $GEMINI_API_KEY
```

---

### 2. 処理モード設定 🟡 推奨

#### PROCESSING_MODE

**選択肢**:
- `hybrid` （推奨）: ローカルとクラウドを使い分け
- `cloud`: すべてクラウド処理（高速・高精度）
- `local`: すべてローカル処理（完全無料）

**推奨値**: `hybrid`

#### COST_MODE

**選択肢**:
- `save`: コスト重視（ローカル優先）
- `balanced` （推奨）: バランス型
- `performance`: 性能重視（クラウド優先）

**推奨値**: `balanced`

---

### 3. OCRエンジン設定 🟡 推奨

#### OCR_ENGINE

**選択肢**:
- `local`: Tesseract OCR（無料、精度70-85%）
- `cloud`: Google Cloud Vision API（有料、精度95%+）

**設定ガイド**:

| 使用ケース | 推奨設定 | 理由 |
|-----------|---------|------|
| Geminiのみ使用 | `local` | コスト節約 |
| 高精度が必要 | `cloud` | 最高精度 |
| 手書き文字が多い | `cloud` | 手書き認識向上 |

**設定例（パターン別）**:

```bash
# パターンA: 最小コスト構成
OCR_ENGINE=local
GEMINI_API_KEY=your-key

# パターンB: 高精度構成
OCR_ENGINE=cloud
GOOGLE_CLOUD_PROJECT_ID=your-project
GEMINI_API_KEY=your-key
```

---

### 4. 同時処理数 🟡 推奨

#### MAX_CONCURRENT_TASKS

**メモリ別推奨値**:

| メモリ | 推奨値 | 理由 |
|-------|--------|------|
| 8GB | `3` | 安定動作 |
| 16GB | `5` | 高速処理 |
| 32GB+ | `10` | 最大性能 |

**設定例**:
```bash
# 8GBメモリの場合
MAX_CONCURRENT_TASKS=3

# 16GBメモリの場合
MAX_CONCURRENT_TASKS=5
```

**調整方法**:
- メモリ不足エラーが出る → 値を減らす
- 余裕がある → 値を増やす

---

### 5. セキュリティ設定 🟡 推奨

#### SECRET_KEY

**目的**: セッション暗号化、CSRF保護

**生成方法**:
```bash
# macOS/Linux
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 出力例:
# kJ8n3Lp9mQ2rS5tV7wX0yZ1aC3dE6fG8hI

# Dockerコンテナ内で生成
docker run --rm python:3.11-slim python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**設定例**:
```bash
SECRET_KEY=kJ8n3Lp9mQ2rS5tV7wX0yZ1aC3dE6fG8hI
```

#### API_KEY（オプション）

**目的**: API認証（外部アクセス制御）

**設定方法**:
```bash
# 同じく生成
API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
```

**使用例**:
```bash
# API呼び出し時にヘッダーに含める
curl -H "X-API-Key: your-api-key" http://localhost:8080/api/documents
```

---

### 6. Google Cloud Vision API 🟢 オプション

**必要な場合のみ設定**:
- 高精度OCRが必要
- 手書き文字認識
- 複雑なレイアウトのPDF

#### Step 1: Google Cloudプロジェクト作成

1. https://console.cloud.google.com/ にアクセス
2. プロジェクトを作成
3. Vision APIを有効化

#### Step 2: サービスアカウントキー取得

1. 「APIとサービス」→「認証情報」
2. 「サービスアカウント」を作成
3. JSONキーをダウンロード

#### Step 3: キーを配置

```bash
# ダウンロードしたキーを配置
cp ~/Downloads/your-key.json /Users/Yoshi/nas-project/document-automation/config/google-credentials.json

# 権限設定
chmod 600 /Users/Yoshi/nas-project/document-automation/config/google-credentials.json
```

#### Step 4: 環境変数設定

```bash
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/config/google-credentials.json
OCR_ENGINE=cloud
```

---

### 7. その他の設定 🟢 オプション

#### ファイルサイズ制限

```bash
# デフォルト: 50MB
MAX_FILE_SIZE=52428800

# 100MBに変更する場合
MAX_FILE_SIZE=104857600
```

#### 対応ファイル形式

```bash
# デフォルト
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png

# TIFFを追加する場合
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png,tiff
```

#### 対応言語

```bash
# デフォルト: 日本語・英語
OCR_LANGUAGE=ja,en

# 中国語・韓国語を追加
OCR_LANGUAGE=ja,en,zh,ko
```

#### ログレベル

```bash
# デバッグ情報を出力
LOG_LEVEL=DEBUG

# 本番環境
LOG_LEVEL=INFO
```

---

## 🎯 推奨構成パターン

### パターンA: 最小コスト構成（推奨）

```bash
# 必須
GEMINI_API_KEY=your-key
SECRET_KEY=your-random-string

# 処理設定
PROCESSING_MODE=hybrid
COST_MODE=save
OCR_ENGINE=local
MAX_CONCURRENT_TASKS=3

# コスト: 月$1-3程度
```

### パターンB: バランス構成（推奨）

```bash
# 必須
GEMINI_API_KEY=your-key
SECRET_KEY=your-random-string

# 処理設定
PROCESSING_MODE=hybrid
COST_MODE=balanced
OCR_ENGINE=local
MAX_CONCURRENT_TASKS=3

# コスト: 月$3-10程度
```

### パターンC: 高性能構成

```bash
# 必須
GEMINI_API_KEY=your-key
GOOGLE_CLOUD_PROJECT_ID=your-project
SECRET_KEY=your-random-string

# 処理設定
PROCESSING_MODE=cloud
COST_MODE=performance
OCR_ENGINE=cloud
MAX_CONCURRENT_TASKS=5

# コスト: 月$10-30程度
```

---

## ✅ 設定チェックリスト

デプロイ前に以下を確認してください：

### 必須項目
- [ ] `GEMINI_API_KEY` が設定されている
- [ ] `SECRET_KEY` が設定されている（ランダム文字列）
- [ ] `MAX_CONCURRENT_TASKS` がメモリに適した値

### 推奨項目
- [ ] `PROCESSING_MODE` が選択されている
- [ ] `OCR_ENGINE` が選択されている
- [ ] `API_KEY` が設定されている（外部公開時）

### オプション項目
- [ ] Google Cloud Vision API（高精度OCR）
- [ ] ログレベルが適切
- [ ] ファイルサイズ制限が適切

---

## 🧪 設定の確認方法

### 1. 環境変数の確認

```bash
# .envファイルの内容確認
cat .env | grep -v "^#" | grep -v "^$"

# 必須項目チェック
grep "GEMINI_API_KEY" .env
grep "SECRET_KEY" .env
```

### 2. デプロイ後の確認

```bash
# ヘルスチェック
curl http://localhost:8080/health

# 期待される出力:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "mode": "hybrid",
#   "ocr_engine": "local",
#   "ai_provider": "gemini"
# }
```

### 3. コンテナ内の環境変数確認

```bash
# Webコンテナ
sudo docker exec doc-automation-web env | grep GEMINI

# Workerコンテナ
sudo docker exec doc-automation-worker env | grep -E "(GEMINI|OCR|PROCESSING)"
```

---

## 🚨 よくあるエラーと対処法

### エラー1: Gemini API認証エラー

**症状**:
```
Error: Invalid API key
```

**対処法**:
1. APIキーが正しいか確認
2. APIキーが有効化されているか確認
3. 請求先アカウントが設定されているか確認（無料枠内でも必要）

### エラー2: メモリ不足

**症状**:
```
MemoryError: Unable to allocate memory
```

**対処法**:
```bash
# MAX_CONCURRENT_TASKSを減らす
MAX_CONCURRENT_TASKS=2  # 3から2に変更
```

### エラー3: OCRエンジンエラー

**症状**:
```
Error: Cloud Vision API not configured
```

**対処法**:
```bash
# ローカルモードに変更
OCR_ENGINE=local
```

---

## 📞 サポート

設定で困ったら：
1. このガイドの「よくあるエラー」を確認
2. README.mdのトラブルシューティングを参照
3. ログを確認: `sudo docker compose logs`

---

**最終更新**: 2025年10月18日

