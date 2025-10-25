#!/bin/bash
# 既存プロジェクトのNAS環境デプロイ仕様への更新スクリプト

set -e

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== 既存プロジェクトのNAS環境デプロイ仕様更新 ===${NC}"
echo ""

# プロジェクトリスト
PROJECTS=(
    "amazon-analytics:5001"
    "document-automation:5003"
    "insta360-auto-sync:5004"
    "nas-dashboard:5005"
)

for project_info in "${PROJECTS[@]}"; do
    IFS=':' read -r project_name port <<< "$project_info"
    
    echo -e "${YELLOW}📁 $project_name を更新中...${NC}"
    
    # プロジェクトディレクトリの確認
    if [ -d "/home/YOUR_USERNAME/nas-project/$project_name" ]; then
        cd "/home/YOUR_USERNAME/nas-project/$project_name"
        
        # 既存のdeploy-nas.shをバックアップ
        if [ -f "deploy-nas.sh" ]; then
            cp deploy-nas.sh deploy-nas.sh.backup.$(date +%Y%m%d_%H%M%S)
            echo "  ✅ deploy-nas.sh をバックアップしました"
        fi
        
        # 新しいdeploy-nas.shを作成
        cat > deploy-nas.sh << EOF
#!/bin/bash
# $project_name - NAS環境デプロイスクリプト

set -e

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\${BLUE}=== $project_name NAS環境デプロイ ===\${NC}"
echo ""

# 現在のディレクトリを確認
if [ ! -f "app.py" ]; then
    echo -e "\${RED}❌ エラー: app.pyが見つかりません\${NC}"
    echo "このスクリプトは$project_nameディレクトリで実行してください"
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
mkdir -p /home/YOUR_USERNAME/$project_name-data/uploads
mkdir -p /home/YOUR_USERNAME/$project_name-data/transcripts
mkdir -p /home/YOUR_USERNAME/$project_name-data/templates
mkdir -p /home/YOUR_USERNAME/$project_name-data/logs

# 権限設定
echo -e "\${YELLOW}🔐 ディレクトリ権限を設定中...\${NC}"
chmod 755 /home/YOUR_USERNAME/$project_name-data
chmod 755 /home/YOUR_USERNAME/$project_name-data/uploads
chmod 755 /home/YOUR_USERNAME/$project_name-data/transcripts
chmod 755 /home/YOUR_USERNAME/$project_name-data/templates
chmod 755 /home/YOUR_USERNAME/$project_name-data/logs

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

if docker ps | grep -q $project_name; then
    echo -e "\${GREEN}✅ $project_nameが正常に起動しました\${NC}"
    echo ""
    echo -e "\${BLUE}📊 アクセス情報:\${NC}"
    echo "  URL: http://YOUR_NAS_IP:$port"
    echo "  ヘルスチェック: http://YOUR_NAS_IP:$port/health"
    echo ""
    echo -e "\${BLUE}📁 データディレクトリ:\${NC}"
    echo "  アップロード: /home/YOUR_USERNAME/$project_name-data/uploads"
    echo "  議事録: /home/YOUR_USERNAME/$project_name-data/transcripts"
    echo "  テンプレート: /home/YOUR_USERNAME/$project_name-data/templates"
    echo "  ログ: /home/YOUR_USERNAME/$project_name-data/logs"
    echo ""
    echo -e "\${BLUE}🔧 管理コマンド:\${NC}"
    echo "  ログ確認: docker logs -f $project_name"
    echo "  停止: docker compose down"
    echo "  再起動: docker compose restart"
    echo "  状態確認: docker ps | grep $project_name"
    echo ""
    echo -e "\${GREEN}🎉 デプロイが完了しました！\${NC}"
else
    echo -e "\${RED}❌ コンテナの起動に失敗しました\${NC}"
    echo ""
    echo -e "\${YELLOW}🔍 トラブルシューティング:\${NC}"
    echo "1. ログを確認: docker logs $project_name"
    echo "2. 環境変数を確認: cat env.production"
    echo "3. ポートが使用中でないか確認: netstat -tlnp | grep $port"
    echo "4. Docker デーモンが起動しているか確認: systemctl status docker"
    exit 1
fi
EOF
        
        chmod +x deploy-nas.sh
        echo "  ✅ deploy-nas.sh を更新しました"
        
        # docker-compose.ymlの更新（必要に応じて）
        if [ -f "docker-compose.yml" ]; then
            # 既存のdocker-compose.ymlをバックアップ
            cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
            echo "  ✅ docker-compose.yml をバックアップしました"
        fi
        
        echo "  ✅ $project_name の更新が完了しました"
    else
        echo "  ⚠️  $project_name のディレクトリが見つかりません"
    fi
    
    echo ""
done

echo -e "${GREEN}🎉 全プロジェクトの更新が完了しました！${NC}"
echo ""
echo -e "${BLUE}📋 更新内容:${NC}"
echo "  - deploy-nas.sh の標準化"
echo "  - データディレクトリの統一"
echo "  - ポート番号の整理"
echo ""
echo -e "${BLUE}📁 データディレクトリ:${NC}"
for project_info in "${PROJECTS[@]}"; do
    IFS=':' read -r project_name port <<< "$project_info"
    echo "  /home/YOUR_USERNAME/$project_name-data/"
done
