#!/bin/bash

# ドキュメント自動処理システム - 権限修正スクリプト
# 使用方法: ./fix-permissions.sh

set -e

echo "========================================="
echo "ドキュメント自動処理システム 権限修正"
echo "========================================="

# 色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# NAS上のデータディレクトリ
DATA_DIR="~/nas-project-data/document-automation"

echo -e "\n${YELLOW}データディレクトリ: ${DATA_DIR}${NC}"

# ディレクトリが存在しない場合は作成
if [ ! -d "$DATA_DIR" ]; then
    echo -e "${YELLOW}ディレクトリが存在しません。作成します...${NC}"
    sudo mkdir -p "$DATA_DIR"/{uploads,processed,exports,cache,db,qdrant}
fi

# 権限を修正
echo -e "\n${YELLOW}権限を修正中...${NC}"

# すべてのディレクトリに読み書き権限を付与
sudo chmod -R 755 "$DATA_DIR"
sudo chmod -R 777 "$DATA_DIR"/uploads
sudo chmod -R 777 "$DATA_DIR"/processed
sudo chmod -R 777 "$DATA_DIR"/exports
sudo chmod -R 777 "$DATA_DIR"/cache

# 所有権を確認（YOUR_USERNAMEが存在する場合）
if id "YOUR_USERNAME" &>/dev/null; then
    echo -e "${YELLOW}YOUR_USERNAMEの所有権に設定中...${NC}"
    sudo chown -R YOUR_USERNAME:users "$DATA_DIR" 2>/dev/null || \
    sudo chown -R YOUR_USERNAME:YOUR_USERNAME "$DATA_DIR" 2>/dev/null || \
    echo -e "${YELLOW}警告: YOUR_USERNAMEが見つかりません。現在のユーザーで設定します。${NC}"
fi

# 現在のユーザーでも所有権を設定（フォールバック）
CURRENT_USER=$(whoami)
sudo chown -R "$CURRENT_USER:$CURRENT_USER" "$DATA_DIR" 2>/dev/null || \
sudo chown -R "$CURRENT_USER:users" "$DATA_DIR" 2>/dev/null || \
echo -e "${YELLOW}警告: 所有権の設定に失敗しました。${NC}"

# 権限確認
echo -e "\n${GREEN}権限確認:${NC}"
ls -la "$DATA_DIR" | head -10

echo -e "\n${GREEN}✓ 権限修正完了${NC}"
echo "========================================="
echo ""
echo "次のコマンドでコンテナを再起動してください:"
echo "  cd ~/nas-project/document-automation"
echo "  sudo docker compose restart web worker"
echo ""
