#!/bin/bash
#
# バージョンアップスクリプト
# 使い方:
#   ./scripts/version_bump.sh [patch|minor|major]
#
# 引数なしの場合は自動判定でパッチバージョンをインクリメント

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# カラー出力
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 自動バージョンアップ開始${NC}"
echo ""

# バージョンアップタイプ（引数から取得、なければ自動判定）
BUMP_TYPE="${1:-auto}"

# Pythonスクリプトを実行
if [ "$BUMP_TYPE" = "auto" ]; then
    python3 "$SCRIPT_DIR/auto_version.py"
else
    python3 "$SCRIPT_DIR/auto_version.py" "$BUMP_TYPE"
fi

echo ""
echo -e "${GREEN}✅ バージョンアップ完了${NC}"
echo ""
echo -e "${YELLOW}📌 次のステップ:${NC}"
echo "   1. git add version.py"
echo "   2. git commit -m '自動バージョンアップ to vX.X.X'"
echo "   3. git push"
echo ""

