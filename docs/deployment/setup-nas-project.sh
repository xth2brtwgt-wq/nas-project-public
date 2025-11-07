#!/bin/bash
# NAS環境プロジェクトセットアップスクリプト

set -e

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== NAS環境プロジェクトセットアップ ===${NC}"
echo ""

# 引数チェック
if [ $# -ne 2 ]; then
    echo -e "${RED}❌ 使用方法: $0 <プロジェクト名> <ポート番号>${NC}"
    echo "例: $0 my-app 5003"
    exit 1
fi

PROJECT_NAME=$1
PORT=$2

echo -e "${YELLOW}📋 プロジェクト情報:${NC}"
echo "  プロジェクト名: $PROJECT_NAME"
echo "  ポート番号: $PORT"
echo ""

# プロジェクトディレクトリの作成
echo -e "${YELLOW}📁 プロジェクトディレクトリを作成中...${NC}"
mkdir -p /home/AdminUser/nas-project/$PROJECT_NAME
cd /home/AdminUser/nas-project/$PROJECT_NAME

# deploy-nas.shの作成
echo -e "${YELLOW}📝 deploy-nas.shを作成中...${NC}"
cat > deploy-nas.sh << EOF
#!/bin/bash
# $PROJECT_NAME - NAS環境デプロイスクリプト

set -e

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\${BLUE}=== $PROJECT_NAME NAS環境デプロイ ===\${NC}"
echo ""

# 現在のディレクトリを確認
if [ ! -f "app.py" ]; then
    echo -e "\${RED}❌ エラー: app.pyが見つかりません\${NC}"
    echo "このスクリプトは$PROJECT_NAMEディレクトリで実行してください"
    exit 1
fi

# 環境変数ファイルの確認
if [ ! -f "env.production" ]; then
    echo -e "\${YELLOW}⚠️  env.productionファイルが見つかりません\${NC}"
    echo "env.productionファイルを作成して環境変数を設定してください"
    echo "env.exampleを参考にしてください"
    exit 1
fi

# 必要なディレクトリを作成
echo -e "\${YELLOW}📁 必要なディレクトリを作成中...\${NC}"
mkdir -p /home/AdminUser/$PROJECT_NAME-data/uploads
mkdir -p /home/AdminUser/$PROJECT_NAME-data/transcripts
mkdir -p /home/AdminUser/$PROJECT_NAME-data/templates
mkdir -p /home/AdminUser/$PROJECT_NAME-data/logs

# 権限設定
echo -e "\${YELLOW}🔐 ディレクトリ権限を設定中...\${NC}"
chmod 755 /home/AdminUser/$PROJECT_NAME-data
chmod 755 /home/AdminUser/$PROJECT_NAME-data/uploads
chmod 755 /home/AdminUser/$PROJECT_NAME-data/transcripts
chmod 755 /home/AdminUser/$PROJECT_NAME-data/templates
chmod 755 /home/AdminUser/$PROJECT_NAME-data/logs

# Dockerネットワークを作成（存在しない場合）
echo -e "\${YELLOW}🌐 Dockerネットワークを作成中...\${NC}"
docker network create nas-network 2>/dev/null || echo "ネットワークは既に存在します"

# 既存のコンテナを停止・削除
echo -e "\${YELLOW}🛑 既存のコンテナを停止中...\${NC}"
docker compose down 2>/dev/null || echo "既存のコンテナはありません"

# 環境変数を読み込み
echo -e "\${YELLOW}📋 環境変数を読み込み中...\${NC}"
export \$(grep -v '^#' env.production | xargs)

# イメージをビルド
echo -e "\${YELLOW}🔨 Dockerイメージをビルド中...\${NC}"
docker compose build --no-cache

# コンテナを起動
echo -e "\${YELLOW}🚀 コンテナを起動中...\${NC}"
docker compose up -d

# 起動確認
echo -e "\${YELLOW}⏳ 起動確認中...\${NC}"
sleep 15

if docker ps | grep -q $PROJECT_NAME; then
    echo -e "\${GREEN}✅ $PROJECT_NAMEが正常に起動しました\${NC}"
    echo ""
    echo -e "\${BLUE}📊 アクセス情報:\${NC}"
    echo "  URL: http://192.168.68.110:$PORT"
    echo "  ヘルスチェック: http://192.168.68.110:$PORT/health"
    echo ""
    echo -e "\${BLUE}📁 データディレクトリ:\${NC}"
    echo "  アップロード: /home/AdminUser/$PROJECT_NAME-data/uploads"
    echo "  議事録: /home/AdminUser/$PROJECT_NAME-data/transcripts"
    echo "  テンプレート: /home/AdminUser/$PROJECT_NAME-data/templates"
    echo "  ログ: /home/AdminUser/$PROJECT_NAME-data/logs"
    echo ""
    echo -e "\${BLUE}🔧 管理コマンド:\${NC}"
    echo "  ログ確認: docker logs -f $PROJECT_NAME"
    echo "  停止: docker compose down"
    echo "  再起動: docker compose restart"
    echo "  状態確認: docker ps | grep $PROJECT_NAME"
    echo ""
    echo -e "\${GREEN}🎉 デプロイが完了しました！\${NC}"
else
    echo -e "\${RED}❌ コンテナの起動に失敗しました\${NC}"
    echo ""
    echo -e "\${YELLOW}🔍 トラブルシューティング:\${NC}"
    echo "1. ログを確認: docker logs $PROJECT_NAME"
    echo "2. 環境変数を確認: cat env.production"
    echo "3. ポートが使用中でないか確認: netstat -tlnp | grep $PORT"
    echo "4. Docker デーモンが起動しているか確認: systemctl status docker"
    exit 1
fi
EOF

chmod +x deploy-nas.sh

# docker-compose.ymlの作成
echo -e "${YELLOW}📝 docker-compose.ymlを作成中...${NC}"
cat > docker-compose.yml << EOF
version: '3.8'

services:
  $PROJECT_NAME:
    build: .
    image: $PROJECT_NAME:latest
    container_name: $PROJECT_NAME
    ports:
      - "$PORT:5000"
    volumes:
      # 永続化データディレクトリ（データのみ）
      - /home/AdminUser/$PROJECT_NAME-data/uploads:/app/uploads
      - /home/AdminUser/$PROJECT_NAME-data/transcripts:/app/transcripts
      # ログディレクトリ
      - /home/AdminUser/$PROJECT_NAME-data/logs:/app/logs
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
    labels:
      - "com.docker.compose.project=$PROJECT_NAME"
      - "com.docker.compose.service=$PROJECT_NAME"
      - "com.centurylinklabs.watchtower.enable=true"
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
EOF

# env.productionの作成
echo -e "${YELLOW}📝 env.productionを作成中...${NC}"
cat > env.production << EOF
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
APP_NAME=$PROJECT_NAME
VERSION=1.0.0
EOF

# env.exampleの作成
echo -e "${YELLOW}📝 env.exampleを作成中...${NC}"
cp env.production env.example

# README.mdの作成
echo -e "${YELLOW}📝 README.mdを作成中...${NC}"
cat > README.md << EOF
# $PROJECT_NAME

## 概要

$PROJECT_NAMEのNAS環境デプロイ用プロジェクトです。

## デプロイ方法

### 初回デプロイ

1. 環境変数の設定
   \`\`\`bash
   cp env.example env.production
   # env.productionを編集してAPIキーなどを設定
   \`\`\`

2. デプロイの実行
   \`\`\`bash
   ./deploy-nas.sh
   \`\`\`

### 日常的なデプロイ

\`\`\`bash
git pull origin main
./deploy-nas.sh
\`\`\`

## アクセス情報

- **URL**: http://192.168.68.110:$PORT
- **ヘルスチェック**: http://192.168.68.110:$PORT/health

## 管理コマンド

- ログ確認: \`docker logs -f $PROJECT_NAME\`
- 停止: \`docker compose down\`
- 再起動: \`docker compose restart\`
- 状態確認: \`docker ps | grep $PROJECT_NAME\`

## データディレクトリ

- アップロード: /home/AdminUser/$PROJECT_NAME-data/uploads
- 議事録: /home/AdminUser/$PROJECT_NAME-data/transcripts
- テンプレート: /home/AdminUser/$PROJECT_NAME-data/templates
- ログ: /home/AdminUser/$PROJECT_NAME-data/logs
EOF

echo -e "${GREEN}✅ プロジェクトセットアップが完了しました！${NC}"
echo ""
echo -e "${BLUE}📋 次のステップ:${NC}"
echo "1. アプリケーションコードを配置"
echo "2. env.productionを編集してAPIキーを設定"
echo "3. ./deploy-nas.sh を実行してデプロイ"
echo ""
echo -e "${BLUE}📁 プロジェクトディレクトリ:${NC}"
echo "  /home/AdminUser/nas-project/$PROJECT_NAME/"
echo ""
echo -e "${BLUE}📁 データディレクトリ:${NC}"
echo "  /home/AdminUser/$PROJECT_NAME-data/"
