#!/bin/bash
# Amazon Purchase Analytics System - 初期セットアップスクリプト

set -e

# カラー定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Amazon Purchase Analytics - Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# .envの存在確認
if [ -f .env ]; then
    echo -e "${GREEN}✓ .envファイルが既に存在します${NC}"
else
    echo -e "${YELLOW}! .envファイルを作成します${NC}"
    
    if [ -f env.example ]; then
        cp env.example .env
        echo -e "${GREEN}✓ .envを作成しました${NC}"
        echo -e "${YELLOW}→ .envを編集してAPIキーを設定してください${NC}"
    else
        echo -e "${RED}エラー: env.exampleファイルが見つかりません${NC}"
        exit 1
    fi
fi

# Docker起動確認
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}エラー: Dockerが起動していません${NC}"
    echo -e "${YELLOW}Dockerを起動してから再度実行してください${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker起動確認完了${NC}"

# データディレクトリの確認
echo -e "${BLUE}データディレクトリを確認中...${NC}"
mkdir -p data/uploads data/processed data/exports data/cache data/db
echo -e "${GREEN}✓ データディレクトリ作成完了${NC}"

# Pythonテストスクリプト実行確認
echo ""
echo -e "${BLUE}セットアップテストを実行しますか？ (y/n)${NC}"
read -p "> " RUN_TEST

if [[ $RUN_TEST == "y" || $RUN_TEST == "Y" ]]; then
    echo -e "${BLUE}Dockerコンテナを起動します...${NC}"
    docker compose up -d db redis
    
    echo -e "${YELLOW}データベース起動を待機中...${NC}"
    sleep 10
    
    echo -e "${BLUE}セットアップテストを実行中...${NC}"
    python3 test_setup.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ セットアップテスト完了${NC}"
    else
        echo -e "${YELLOW}⚠ テストで警告がありました${NC}"
        echo -e "${YELLOW}Gemini APIキーを.envに設定してください${NC}"
    fi
fi

# .env.restoreの作成を推奨
if [ -f .env ] && [ ! -f .env.restore ]; then
    echo -e "${YELLOW}⚠ .env.restoreを作成することを推奨します（バックアップ用）${NC}"
    echo -e "${BLUE}cp .env .env.restore${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ セットアップ完了${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "次のステップ:"
echo -e "1. ${YELLOW}.env${NC}を編集してAPIキーを設定"
echo -e "   ${BLUE}nano .env${NC}"
echo ""
echo -e "2. ${YELLOW}.env.restore${NC}を作成（バックアップ用、推奨）"
echo -e "   ${BLUE}cp .env .env.restore${NC}"
echo ""
echo -e "3. アプリケーションを起動"
echo -e "   ${BLUE}./deploy.sh build${NC}"
echo ""
echo -e "4. ブラウザでアクセス"
echo -e "   ${BLUE}http://localhost:8000${NC}"
echo ""

