#!/bin/bash
# PROJECT_NAME - NAS環境デプロイスクリプト

set -e

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== PROJECT_NAME NAS環境デプロイ ===${NC}"
echo ""

# 現在のディレクトリを確認
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ エラー: app.pyが見つかりません${NC}"
    echo "このスクリプトはPROJECT_NAMEディレクトリで実行してください"
    exit 1
fi

# 環境変数ファイルの確認
if [ ! -f "env.production" ]; then
    echo -e "${YELLOW}⚠️  env.productionファイルが見つかりません${NC}"
    echo "env.productionファイルを作成して環境変数を設定してください"
    echo "env.exampleを参考にしてください"
    exit 1
fi

# 必要なディレクトリを作成
echo -e "${YELLOW}📁 必要なディレクトリを作成中...${NC}"
mkdir -p /home/YOUR_USERNAME/PROJECT_NAME-data/uploads
mkdir -p /home/YOUR_USERNAME/PROJECT_NAME-data/transcripts
mkdir -p /home/YOUR_USERNAME/PROJECT_NAME-data/templates
mkdir -p /home/YOUR_USERNAME/PROJECT_NAME-data/logs

# 権限設定
echo -e "${YELLOW}🔐 ディレクトリ権限を設定中...${NC}"
chmod 755 /home/YOUR_USERNAME/PROJECT_NAME-data
chmod 755 /home/YOUR_USERNAME/PROJECT_NAME-data/uploads
chmod 755 /home/YOUR_USERNAME/PROJECT_NAME-data/transcripts
chmod 755 /home/YOUR_USERNAME/PROJECT_NAME-data/templates
chmod 755 /home/YOUR_USERNAME/PROJECT_NAME-data/logs

# Dockerネットワークを作成（存在しない場合）
echo -e "${YELLOW}🌐 Dockerネットワークを作成中...${NC}"
docker network create nas-network 2>/dev/null || echo "ネットワークは既に存在します"

# 既存のコンテナを停止・削除
echo -e "${YELLOW}🛑 既存のコンテナを停止中...${NC}"
docker compose down 2>/dev/null || echo "既存のコンテナはありません"

# 環境変数を読み込み
echo -e "${YELLOW}📋 環境変数を読み込み中...${NC}"
export $(grep -v '^#' env.production | xargs)

# イメージをビルド
echo -e "${YELLOW}🔨 Dockerイメージをビルド中...${NC}"
docker compose build --no-cache

# コンテナを起動
echo -e "${YELLOW}🚀 コンテナを起動中...${NC}"
docker compose up -d

# 起動確認
echo -e "${YELLOW}⏳ 起動確認中...${NC}"
sleep 15

if docker ps | grep -q PROJECT_NAME; then
    echo -e "${GREEN}✅ PROJECT_NAMEが正常に起動しました${NC}"
    echo ""
    echo -e "${BLUE}📊 アクセス情報:${NC}"
    echo "  URL: http://YOUR_NAS_IP:PORT"
    echo "  ヘルスチェック: http://YOUR_NAS_IP:PORT/health"
    echo ""
    echo -e "${BLUE}📁 データディレクトリ:${NC}"
    echo "  アップロード: /home/YOUR_USERNAME/PROJECT_NAME-data/uploads"
    echo "  議事録: /home/YOUR_USERNAME/PROJECT_NAME-data/transcripts"
    echo "  テンプレート: /home/YOUR_USERNAME/PROJECT_NAME-data/templates"
    echo "  ログ: /home/YOUR_USERNAME/PROJECT_NAME-data/logs"
    echo ""
    echo -e "${BLUE}🔧 管理コマンド:${NC}"
    echo "  ログ確認: docker logs -f PROJECT_NAME"
    echo "  停止: docker compose down"
    echo "  再起動: docker compose restart"
    echo "  状態確認: docker ps | grep PROJECT_NAME"
    echo ""
    echo -e "${BLUE}🛡️  セキュリティ設定:${NC}"
    echo "  環境変数ファイル: env.production"
    echo "  シークレットキー: 必ず変更してください"
    echo "  API キー: 適切に設定してください"
    echo ""
    echo -e "${GREEN}🎉 デプロイが完了しました！${NC}"
    echo ""
    echo -e "${YELLOW}📝 次のステップ:${NC}"
    echo "1. ブラウザで http://YOUR_NAS_IP:PORT にアクセス"
    echo "2. アプリケーション機能をテスト"
    echo "3. ログを確認してエラーがないかチェック"
    echo "4. 必要に応じて設定を調整"
else
    echo -e "${RED}❌ コンテナの起動に失敗しました${NC}"
    echo ""
    echo -e "${YELLOW}🔍 トラブルシューティング:${NC}"
    echo "1. ログを確認: docker logs PROJECT_NAME"
    echo "2. 環境変数を確認: cat env.production"
    echo "3. ポートが使用中でないか確認: netstat -tlnp | grep PORT"
    echo "4. Docker デーモンが起動しているか確認: systemctl status docker"
    exit 1
fi
