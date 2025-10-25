#!/bin/bash

# ドキュメント自動処理システム デプロイスクリプト
# 使用方法: ./deploy.sh

set -e

echo "========================================="
echo "ドキュメント自動処理システム デプロイ開始"
echo "========================================="

# 色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 環境変数チェック
check_env() {
    echo -e "\n${YELLOW}[1/7] 環境変数チェック${NC}"
    
    if [ ! -f .env ]; then
        echo -e "${RED}エラー: .env ファイルが見つかりません${NC}"
        echo "env.example をコピーして .env を作成してください："
        echo "  cp env.example .env"
        echo "  nano .env"
        exit 1
    fi
    
    # APIキーチェック
    if ! grep -q "GEMINI_API_KEY=your-gemini-api-key" .env; then
        echo -e "${GREEN}✓ Gemini APIキーが設定されています${NC}"
    else
        echo -e "${RED}警告: Gemini APIキーが設定されていません${NC}"
        echo "  .env ファイルで GEMINI_API_KEY を設定してください"
        read -p "続行しますか？ (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✓ 環境変数チェック完了${NC}"
}

# ディレクトリ作成
create_directories() {
    echo -e "\n${YELLOW}[2/7] データディレクトリ作成${NC}"
    
    # NAS上のディレクトリ
    if [ -d "/volume2" ]; then
        DATA_ROOT="/volume2/data/doc-automation"
    else
        DATA_ROOT="./data"
    fi
    
    echo "データディレクトリ: $DATA_ROOT"
    
    sudo mkdir -p "$DATA_ROOT"/{uploads,processed,exports,cache,db}
    sudo chown -R $USER:users "$DATA_ROOT" 2>/dev/null || sudo chown -R $USER:$USER "$DATA_ROOT"
    
    echo -e "${GREEN}✓ ディレクトリ作成完了${NC}"
}

# Dockerイメージのビルド
build_images() {
    echo -e "\n${YELLOW}[3/7] Dockerイメージビルド${NC}"
    
    echo "Webサービスをビルド中..."
    sudo docker compose build web
    
    echo "Workerサービスをビルド中..."
    sudo docker compose build worker
    
    echo -e "${GREEN}✓ イメージビルド完了${NC}"
}

# 既存コンテナの停止
stop_containers() {
    echo -e "\n${YELLOW}[4/7] 既存コンテナの停止${NC}"
    
    if sudo docker compose ps | grep -q "Up"; then
        echo "既存のコンテナを停止中..."
        sudo docker compose down
    else
        echo "実行中のコンテナはありません"
    fi
    
    echo -e "${GREEN}✓ コンテナ停止完了${NC}"
}

# コンテナの起動
start_containers() {
    echo -e "\n${YELLOW}[5/7] コンテナ起動${NC}"
    
    sudo docker compose up -d
    
    echo "起動待機中..."
    sleep 5
    
    echo -e "${GREEN}✓ コンテナ起動完了${NC}"
}

# ヘルスチェック
health_check() {
    echo -e "\n${YELLOW}[6/7] ヘルスチェック${NC}"
    
    echo "Webサービスの起動を待機中..."
    for i in {1..30}; do
        if curl -s http://localhost:8080/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Webサービス起動成功${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}エラー: Webサービスが起動しませんでした${NC}"
            echo "ログを確認してください: sudo docker compose logs web"
            exit 1
        fi
        sleep 2
    done
    
    # データベース接続確認
    echo "データベース接続確認中..."
    if sudo docker compose exec -T db pg_isready -U docuser > /dev/null 2>&1; then
        echo -e "${GREEN}✓ データベース接続成功${NC}"
    else
        echo -e "${RED}警告: データベース接続に失敗しました${NC}"
    fi
    
    # Redis接続確認
    echo "Redis接続確認中..."
    if sudo docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis接続成功${NC}"
    else
        echo -e "${RED}警告: Redis接続に失敗しました${NC}"
    fi
}

# デプロイ完了メッセージ
show_completion() {
    echo -e "\n${YELLOW}[7/7] デプロイ完了${NC}"
    echo "========================================="
    echo -e "${GREEN}✓ デプロイが正常に完了しました！${NC}"
    echo "========================================="
    echo ""
    echo "アクセス情報:"
    echo "  Web UI:          http://localhost:8080"
    echo "  API ドキュメント: http://localhost:8080/docs"
    echo "  ヘルスチェック:   http://localhost:8080/health"
    echo ""
    echo "コンテナ状態確認:"
    echo "  sudo docker compose ps"
    echo ""
    echo "ログ確認:"
    echo "  sudo docker compose logs -f"
    echo ""
    echo "コンテナ停止:"
    echo "  sudo docker compose down"
    echo ""
    echo "========================================="
}

# メイン処理
main() {
    check_env
    create_directories
    build_images
    stop_containers
    start_containers
    health_check
    show_completion
}

# スクリプト実行
main

