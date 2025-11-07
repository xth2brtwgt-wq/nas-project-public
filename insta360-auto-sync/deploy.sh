#!/bin/bash
# Insta360自動同期システム - NAS環境デプロイスクリプト

set -e

# カラー出力設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Insta360自動同期システム NAS環境デプロイ ===${NC}"
echo ""

# 現在のディレクトリを確認
if [ ! -f "scripts/sync.py" ]; then
    echo -e "${RED}❌ エラー: scripts/sync.pyが見つかりません${NC}"
    echo "このスクリプトはinsta360-auto-syncディレクトリで実行してください"
    exit 1
fi

# 環境変数ファイルの確認
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .envファイルが見つかりません${NC}"
    echo ".envファイルを作成して環境変数を設定してください"
    echo "env.exampleを参考にしてください"
    exit 1
fi

# 必要なディレクトリを作成
echo -e "${YELLOW}📁 必要なディレクトリを作成中...${NC}"
mkdir -p ~/nas-project-data/insta360-auto-sync/insta360
mkdir -p ~/nas-project-data/insta360-auto-sync/source
mkdir -p ~/nas-project-data/insta360-auto-sync/logs

# 権限設定
echo -e "${YELLOW}🔐 権限を設定中...${NC}"
chmod -R 755 ~/nas-project-data/insta360-auto-sync/
# 注意: 実際のユーザー名とグループ名に置き換えてください
# chown -R YOUR_USERNAME:YOUR_GROUP ~/nas-project-data/insta360-auto-sync/
if [ -n "${NAS_USER:-}" ] && [ -n "${NAS_GROUP:-}" ]; then
    chown -R "${NAS_USER}:${NAS_GROUP}" ~/nas-project-data/insta360-auto-sync/
else
    echo -e "${YELLOW}⚠️  環境変数 NAS_USER と NAS_GROUP が設定されていません${NC}"
    echo "   権限設定をスキップします。必要に応じて手動で設定してください"
fi

# Dockerネットワークの作成
echo -e "${YELLOW}🌐 Dockerネットワークを作成中...${NC}"
docker network create nas-network 2>/dev/null || echo "ネットワーク 'nas-network' は既に存在します"

# 既存コンテナの停止・削除
echo -e "${YELLOW}🛑 既存コンテナを停止中...${NC}"
docker compose down 2>/dev/null || echo "既存のコンテナはありません"

# 古いイメージの削除
echo -e "${YELLOW}🗑️  古いDockerイメージを削除中...${NC}"
docker image prune -f

# Dockerイメージのビルド
echo -e "${YELLOW}🔨 Dockerイメージをビルド中...${NC}"
docker compose build --no-cache

# コンテナの起動
echo -e "${YELLOW}🚀 コンテナを起動中...${NC}"
docker compose up -d

# 起動確認
echo -e "${YELLOW}⏳ コンテナの起動を待機中...${NC}"
sleep 10

# ヘルスチェック
echo -e "${YELLOW}🔍 ヘルスチェックを実行中...${NC}"
if docker compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Insta360自動同期システムが正常に起動しました${NC}"
    echo ""
    echo -e "${BLUE}📊 システム情報:${NC}"
    echo "  - コンテナ名: insta360-auto-sync"
    echo "  - スケジュール: 毎日 00:00 に実行"
    echo "  - ソースパス: /source"
    echo "  - 転送先パス: /volume2/data/insta360"
    echo "  - ログファイル: ~/insta360-auto-sync-data/logs/"
    echo ""
    echo -e "${GREEN}🎉 デプロイが完了しました！${NC}"
else
    echo -e "${RED}❌ コンテナの起動に失敗しました${NC}"
    echo "ログを確認してください:"
    echo "docker compose logs"
    exit 1
fi

# ログの表示
echo -e "${BLUE}📋 最新のログ:${NC}"
docker compose logs --tail=20
