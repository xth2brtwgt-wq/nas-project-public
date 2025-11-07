# NAS環境デプロイ仕様書

## 📋 概要

NAS環境でのDockerアプリケーションデプロイの共通仕様です。
全プロジェクトで統一されたデプロイ方法を提供します。

## 🏗️ ディレクトリ構造

### 標準的なディレクトリ構成

```
/home/AdminUser/
├── nas-project/                    # Gitリポジトリのルート（ソースコードのみ）
│   ├── amazon-analytics/          # Amazon購入分析プロジェクト
│   │   ├── app/                   # アプリケーションコード
│   │   ├── config/                # 設定ファイル
│   │   ├── docker-compose.yml     # Docker設定
│   │   ├── Dockerfile             # コンテナ定義
│   │   ├── .env                   # 実際の稼働設定（Git管理）
│   │   ├── .env.restore           # バックアップ（Git管理外）
│   │   ├── env.example            # 環境変数テンプレート
│   │   └── requirements.txt       # Python依存関係
│   ├── document-automation/       # ドキュメント自動化プロジェクト
│   ├── meeting-minutes-byc/       # 議事録作成プロジェクト
│   ├── nas-dashboard/             # NAS統合管理ダッシュボード
│   ├── youtube-to-notion/         # YouTube to Notionプロジェクト
│   └── insta360-auto-sync/        # Insta360自動同期プロジェクト
└── nas-project-data/              # 統合データディレクトリ（全データを一元管理）
    ├── amazon-analytics/          # Amazon分析データ
    │   ├── cache/                 # キャッシュデータ
    │   ├── db/                    # データベース
    │   ├── exports/               # エクスポートファイル
    │   ├── processed/             # 処理済みデータ
    │   └── uploads/               # アップロードファイル
    ├── document-automation/       # ドキュメント自動化データ
    │   ├── cache/                 # キャッシュデータ
    │   ├── db/                    # データベース
    │   ├── exports/               # エクスポートファイル
    │   ├── processed/             # 処理済みデータ
    │   ├── qdrant/                # ベクトルデータベース
    │   └── uploads/               # アップロードファイル
    ├── meeting-minutes-byc/       # 議事録データ
    │   ├── logs/                  # ログファイル
    │   ├── transcripts/           # 音声転写データ
    │   └── uploads/               # アップロードファイル
    ├── nas-dashboard/             # ダッシュボードデータ
    │   ├── backups/               # バックアップファイル
    │   └── reports/               # レポートファイル
    └── youtube-to-notion/         # YouTube to Notionデータ
        ├── cache/                 # キャッシュデータ
        ├── logs/                  # ログファイル
        ├── outputs/               # 出力ファイル
        └── uploads/               # アップロードファイル
```

### 重要なポイント

1. **アプリケーションコード**: `/home/AdminUser/nas-project/project-name/`（ソースコードのみ）
2. **永続化データ**: `/home/AdminUser/nas-project-data/project-name/`（統合データディレクトリ配下）
3. **templatesディレクトリ**: ボリュームマウントしない（アプリ更新時の問題回避）
4. **データディレクトリ管理**: すべてのプロジェクトデータは `/home/AdminUser/nas-project-data/` 配下で一元管理
5. **データ分離**: ソースコードとデータを完全に分離し、データは統合ディレクトリで管理
6. **バックアップ効率**: 統合データディレクトリの一括バックアップが可能

## 🔧 deploy-nas.sh 仕様

### 基本構造

```bash
#!/bin/bash
# Project Name - NAS環境デプロイスクリプト

set -e

# カラー出力設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Project Name NAS環境デプロイ ===${NC}"
```

### 必須チェック項目

1. **アプリケーションファイルの存在確認**
2. **環境変数ファイルの存在確認**
3. **必要なディレクトリの作成**
4. **権限設定**
5. **Dockerネットワークの作成**
6. **既存コンテナの停止・削除**
7. **環境変数の読み込み**
8. **Dockerイメージのビルド**
9. **コンテナの起動**
10. **起動確認**

### 標準的なディレクトリ作成

```bash
# 統合データディレクトリの作成
mkdir -p /home/AdminUser/nas-project-data/project-name/uploads
mkdir -p /home/AdminUser/nas-project-data/project-name/transcripts
mkdir -p /home/AdminUser/nas-project-data/project-name/logs
mkdir -p /home/AdminUser/nas-project-data/project-name/cache
mkdir -p /home/AdminUser/nas-project-data/project-name/processed
mkdir -p /home/AdminUser/nas-project-data/project-name/exports

# 権限設定
chmod 755 /home/AdminUser/nas-project-data
chmod 755 /home/AdminUser/nas-project-data/project-name
chmod 755 /home/AdminUser/nas-project-data/project-name/uploads
chmod 755 /home/AdminUser/nas-project-data/project-name/transcripts
chmod 755 /home/AdminUser/nas-project-data/project-name/logs
chmod 755 /home/AdminUser/nas-project-data/project-name/cache
chmod 755 /home/AdminUser/nas-project-data/project-name/processed
chmod 755 /home/AdminUser/nas-project-data/project-name/exports

# 所有者設定
chown -R AdminUser:admin /home/AdminUser/nas-project-data/project-name
```

## 🐳 docker-compose.yml 仕様

### 標準的な設定

```yaml
version: '3.8'

services:
  project-name:
    build: .
    image: project-name:latest
    container_name: project-name
    ports:
      - "PORT:5000"  # 外部ポート:内部ポート
    volumes:
      # 統合データディレクトリ（データのみ）
      - /home/AdminUser/nas-project-data/project-name/uploads:/app/uploads
      - /home/AdminUser/nas-project-data/project-name/transcripts:/app/transcripts
      - /home/AdminUser/nas-project-data/project-name/logs:/app/logs
      - /home/AdminUser/nas-project-data/project-name/cache:/app/cache
      - /home/AdminUser/nas-project-data/project-name/processed:/app/processed
      - /home/AdminUser/nas-project-data/project-name/exports:/app/exports
      # 注意: templatesはマウントしない（アプリケーション更新時に問題が発生するため）
    env_file:
      - .env
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
      - UPLOAD_DIR=/app/uploads
      - TRANSCRIPT_DIR=/app/transcripts
      - TEMPLATES_DIR=/app/templates
      - HOST=0.0.0.0
      - PORT=5000
      - TZ=Asia/Tokyo
    restart: unless-stopped
    networks:
      - nas-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  nas-network:
    external: true
```

## 📝 環境変数ファイル仕様

### env.production の標準構造

```bash
# API設定
GEMINI_API_KEY=your_gemini_api_key_here
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_database_id_here

# SMTP設定
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# アプリケーション設定
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
FLASK_DEBUG=False

# データベース設定
DATABASE_URL=sqlite:///app/data/database.db

# その他の設定
APP_NAME=Project Name
VERSION=1.0.0
```

## 🚀 デプロイ手順

### 初回デプロイ

1. **プロジェクトディレクトリに移動**
   ```bash
   cd /home/AdminUser/nas-project/project-name/
   ```

2. **環境変数ファイルの設定**
   ```bash
   cp env.example env.production
   # env.productionを編集してAPIキーなどを設定
   ```

3. **デプロイスクリプトの実行**
   ```bash
   ./deploy-nas.sh
   ```

### 日常的なデプロイ

1. **最新コードの取得**
   ```bash
   git pull origin main
   ```

2. **デプロイの実行**
   ```bash
   ./deploy-nas.sh
   ```

### 緊急時の再起動

```bash
docker compose restart
```

## 🔍 トラブルシューティング

### よくある問題

1. **環境変数ファイルの初期化**
   - 症状: APIキーが無効
   - 解決: `.env.restore`から`.env`にコピー

2. **ディレクトリ構造の混乱**
   - 症状: 間違ったディレクトリでデプロイ
   - 解決: 正しいディレクトリ（`/home/AdminUser/nas-project/project-name/`）で実行

3. **ボリュームマウントの問題**
   - 症状: 古いファイルが残る
   - 解決: データディレクトリの更新

### 確認コマンド

```bash
# コンテナの状態確認
docker ps | grep project-name

# ログの確認
docker logs project-name

# 環境変数の確認
docker exec project-name env | grep API_KEY

# ファイルの確認
ls -la /home/AdminUser/nas-project-data/project-name/
```

## 📋 チェックリスト

### デプロイ前

- [ ] 正しいディレクトリにいる
- [ ] `env.production`が設定されている
- [ ] 必要なAPIキーが設定されている
- [ ] ポートが使用されていない

### デプロイ後

- [ ] コンテナが正常に起動している
- [ ] ヘルスチェックが通る
- [ ] ログにエラーがない
- [ ] アプリケーションにアクセスできる

## 🎯 推奨事項

1. **定期的なバックアップ**
   - データディレクトリのバックアップ
   - 環境変数ファイルのバックアップ

2. **監視の設定**
   - ログの監視
   - リソース使用量の監視

3. **セキュリティ**
   - APIキーの適切な管理
   - 定期的なパスワード変更

---

**作成日**: 2025年10月23日
**対象**: 全NAS環境プロジェクト
**更新**: 必要に応じて更新
