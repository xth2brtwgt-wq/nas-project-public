# セットアップガイド v1.0.0

ドキュメント自動処理システムの詳細なセットアップ手順です。

## 📌 バージョン情報

- **バージョン**: v1.0.0
- **リリース名**: 初期リリース版
- **リリース日**: 2025-10-19

## 📋 事前準備

### 1. Google Gemini APIキーの取得

#### Step 1: Google AI Studioにアクセス
1. https://makersuite.google.com/app/apikey にアクセス
2. Googleアカウントでログイン

#### Step 2: APIキーを作成
1. 「Create API Key」をクリック
2. プロジェクトを選択（または新規作成）
3. APIキーが表示されたらコピーして保存

#### Step 3: 無料枠の確認
- **無料枠**: 月60リクエスト/分（RPM）まで無料
- **料金**: https://ai.google.dev/pricing

### 2. Google Cloud Vision API の設定（オプション）

高精度なOCRが必要な場合のみ設定してください。

#### Step 1: Google Cloud Console
1. https://console.cloud.google.com/ にアクセス
2. プロジェクトを作成

#### Step 2: Vision APIを有効化
1. 「APIとサービス」→「ライブラリ」
2. 「Cloud Vision API」を検索
3. 「有効にする」をクリック

#### Step 3: サービスアカウントキーを作成
1. 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「サービスアカウント」
3. 名前を入力して作成
4. 「キー」タブ→「鍵を追加」→「JSON」
5. ダウンロードしたJSONファイルを保存

#### Step 4: 無料枠の確認
- **無料枠**: 月1,000ページまで無料
- **料金**: https://cloud.google.com/vision/pricing

## 🚀 インストール手順

### NAS環境での標準インストール

#### 1. プロジェクトの準備

```bash
# NASに接続
ssh -p 23456 YOUR_USERNAME@YOUR_IP_ADDRESS110

# プロジェクトディレクトリに移動
cd ~/nas-project/document-automation
```

#### 2. 環境変数の設定

```bash
# .envファイルを作成
cp env.example .env

# .envファイルを編集
nano .env
```

**最小構成（Geminiのみ）:**

```bash
# Gemini API キー（必須）
GEMINI_API_KEY=AIza...your-actual-key-here

# 処理モード
PROCESSING_MODE=hybrid
COST_MODE=balanced
OCR_ENGINE=local        # Tesseractを使用
AI_PROVIDER=gemini

# アプリケーション設定
MAX_FILE_SIZE=52428800
MAX_CONCURRENT_TASKS=3  # メモリ8GBの場合
```

**フル構成（Gemini + Cloud Vision）:**

```bash
# Gemini API キー
GEMINI_API_KEY=AIza...your-gemini-key

# Google Cloud
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/config/google-credentials.json

# 処理モード
PROCESSING_MODE=hybrid
COST_MODE=balanced
OCR_ENGINE=cloud        # Cloud Vision APIを使用
AI_PROVIDER=gemini

# アプリケーション設定
MAX_FILE_SIZE=52428800
MAX_CONCURRENT_TASKS=5  # クラウド処理なら余裕あり
```

#### 3. Google Cloud認証情報の配置（Cloud Vision使用時のみ）

```bash
# ダウンロードしたサービスアカウントキーをコピー
cp /path/to/downloaded-key.json ~/nas-project/document-automation/config/google-credentials.json

# 権限設定
chmod 600 ~/nas-project/document-automation/config/google-credentials.json
```

#### 4. デプロイスクリプトの実行

```bash
# スクリプトに実行権限を付与
chmod +x deploy.sh

# デプロイ実行
./deploy.sh
```

#### 5. 動作確認

```bash
# ヘルスチェック
curl http://localhost:8080/health

# Web UIにアクセス
# ブラウザで http://YOUR_IP_ADDRESS110:8080 を開く
```

## 🔧 カスタマイズ設定

### メモリ使用量の調整

**8GBメモリの場合:**

```yaml
# docker-compose.yml
services:
  worker:
    deploy:
      resources:
        limits:
          memory: 2G  # 2GBに制限
  
  db:
    deploy:
      resources:
        limits:
          memory: 1G  # 1GBに制限
```

**16GBメモリの場合:**

```yaml
services:
  worker:
    deploy:
      resources:
        limits:
          memory: 6G  # 6GBに拡張
```

### 同時処理数の調整

**.env:**

```bash
# 8GBメモリ
MAX_CONCURRENT_TASKS=3

# 16GBメモリ
MAX_CONCURRENT_TASKS=5
```

### コストモードの選択

```bash
# コスト重視（ローカル処理優先）
PROCESSING_MODE=local
COST_MODE=save
OCR_ENGINE=local
AI_PROVIDER=gemini  # 要約のみクラウド

# バランス型（推奨）
PROCESSING_MODE=hybrid
COST_MODE=balanced
OCR_ENGINE=cloud
AI_PROVIDER=gemini

# 性能重視（クラウド処理優先）
PROCESSING_MODE=cloud
COST_MODE=performance
OCR_ENGINE=cloud
AI_PROVIDER=gemini
```

## 🧪 テスト

### 1. システムヘルスチェック

```bash
# ヘルスチェックAPI
curl http://localhost:8080/health

# 期待される出力:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "mode": "hybrid",
#   "ocr_engine": "cloud",
#   "ai_provider": "gemini"
# }
```

### 2. ファイルアップロードテスト

```bash
# サンプルPDFでテスト
curl -X POST "http://localhost:8080/api/upload" \
  -F "file=@test.pdf"

# 期待される出力:
# {
#   "status": "success",
#   "message": "ファイルをアップロードしました",
#   "document_id": 1,
#   "filename": "test.pdf",
#   "file_size": 12345
# }
```

### 3. 処理状態の確認

```bash
# ドキュメント一覧取得
curl http://localhost:8080/api/documents

# 統計情報取得
curl http://localhost:8080/api/stats
```

## 📊 モニタリング

### ログの確認

```bash
# すべてのログ
sudo docker compose logs -f

# Webサービスのログのみ
sudo docker compose logs -f web

# Workerサービスのログのみ
sudo docker compose logs -f worker

# エラーログのみ
sudo docker compose logs | grep -i error
```

### リソース使用状況

```bash
# コンテナのリソース使用状況
sudo docker stats

# ディスク使用量
du -sh /volume2/data/doc-automation/*
```

### データベース確認

```bash
# データベースに接続
sudo docker exec -it doc-automation-db psql -U docuser -d document_automation

# ドキュメント数確認
# postgres=# SELECT status, COUNT(*) FROM documents GROUP BY status;

# 終了
# postgres=# \q
```

## 🔄 アップデート

### コードの更新

```bash
# 最新コードを取得（Gitを使用している場合）
git pull origin main

# コンテナを再ビルド・再起動
sudo docker compose down
sudo docker compose build
sudo docker compose up -d
```

### データベースのマイグレーション

```bash
# Alembicマイグレーション実行（将来的に）
sudo docker compose exec web alembic upgrade head
```

## 🗑️ アンインストール

### コンテナとイメージの削除

```bash
# コンテナ停止・削除
sudo docker compose down

# イメージ削除
sudo docker compose down --rmi all

# ボリューム削除（データも削除）
sudo docker compose down --volumes
```

### データの削除

```bash
# データディレクトリ削除（注意：復元不可）
sudo rm -rf /volume2/data/doc-automation
```

## 🆘 よくある質問

### Q1: Gemini APIのレート制限に達した場合

**A:** 無料枠は60 RPM（リクエスト/分）です。制限に達した場合：
1. 処理を一時停止
2. 有料プランへのアップグレードを検討
3. または、ローカル処理モードに切り替え

### Q2: メモリ不足エラーが出る場合

**A:** メモリ制限を調整：
- `MAX_CONCURRENT_TASKS`を減らす（.env）
- Docker Composeのメモリ制限を調整
- 他のサービスを停止

### Q3: OCRの精度が低い場合

**A:**
1. Cloud Vision APIを使用（高精度）
2. 画像の解像度を上げる（300dpi推奨）
3. PDFの品質を確認

### Q4: 処理が遅い場合

**A:**
1. Cloud処理モードに切り替え
2. 同時処理数を増やす
3. SSDをキャッシュとして活用

## 📞 サポート

問題が解決しない場合：
1. ログファイルを確認
2. README.mdのトラブルシューティングセクションを参照
3. GitHub Issuesで報告

---

**最終更新**: 2025年10月18日

