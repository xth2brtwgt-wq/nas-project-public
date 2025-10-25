#!/bin/bash
# Amazon Purchase Analytics System - デプロイスクリプト

set -e

# カラー定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Amazon Purchase Analytics - Deploy${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# .envの存在確認
if [ ! -f .env ]; then
    echo -e "${RED}エラー: .envファイルが見つかりません${NC}"
    echo -e "${YELLOW}env.exampleをコピーして.envを作成してください${NC}"
    exit 1
fi

# Gemini APIキーの確認
if ! grep -q "GEMINI_API_KEY=AIza" .env; then
    echo -e "${YELLOW}警告: Gemini APIキーが設定されていない可能性があります${NC}"
    echo -e "${YELLOW}.envを確認してください${NC}"
fi

# Docker起動確認
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}エラー: Dockerが起動していません${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 環境チェック完了${NC}"
echo ""

# デプロイタイプの選択
DEPLOY_TYPE=${1:-"restart"}

case $DEPLOY_TYPE in
    "build")
        echo -e "${BLUE}フルビルド＆デプロイを実行します...${NC}"
        docker compose down
        docker compose build --no-cache
        docker compose up -d
        ;;
    "rebuild")
        echo -e "${BLUE}リビルド＆デプロイを実行します...${NC}"
        docker compose down
        docker compose build
        docker compose up -d
        ;;
    "restart")
        echo -e "${BLUE}再起動を実行します...${NC}"
        docker compose restart
        ;;
    "stop")
        echo -e "${BLUE}停止を実行します...${NC}"
        docker compose down
        echo -e "${GREEN}✓ 停止完了${NC}"
        exit 0
        ;;
    "logs")
        echo -e "${BLUE}ログを表示します...${NC}"
        docker compose logs -f web
        exit 0
        ;;
    *)
        echo -e "${RED}エラー: 無効なオプション${NC}"
        echo "使用方法: ./deploy.sh [build|rebuild|restart|stop|logs]"
        exit 1
        ;;
esac

# 起動待機
echo -e "${YELLOW}コンテナの起動を待機中...${NC}"
sleep 5

# ヘルスチェック
echo -e "${BLUE}ヘルスチェック中...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ アプリケーション起動完了${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}✗ アプリケーションが起動しません${NC}"
        echo -e "${YELLOW}ログを確認してください: docker compose logs web${NC}"
        exit 1
    fi
    sleep 2
done

# バージョン情報取得
VERSION_INFO=$(curl -s http://localhost:8000/api/version 2>/dev/null || echo '{"version":"unknown"}')
VERSION=$(echo $VERSION_INFO | grep -o '"version":"[^"]*"' | cut -d'"' -f4)

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ デプロイ完了${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Version: ${YELLOW}${VERSION}${NC}"
echo -e "URL: ${BLUE}http://localhost:8000${NC}"
echo ""
echo -e "コマンド:"
echo -e "  ログ確認: ${YELLOW}docker compose logs -f web${NC}"
echo -e "  停止: ${YELLOW}./deploy.sh stop${NC}"
echo -e "  再起動: ${YELLOW}./deploy.sh restart${NC}"
echo ""

