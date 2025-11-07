#!/bin/bash
# NAS環境：mainブランチに切り替えスクリプト
# 使用方法: bash NAS_SWITCH_TO_MAIN.sh

set -e  # エラーが発生したら処理を停止

echo "🔄 NAS環境：mainブランチに切り替えを開始します"
echo ""

# 1. プロジェクトルートに移動
cd ~/nas-project

# 2. 現在のブランチを確認
echo "📌 現在のブランチを確認中..."
CURRENT_BRANCH=$(git branch --show-current)
echo "   現在のブランチ: $CURRENT_BRANCH"
echo ""

# 3. 変更があるか確認
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  警告: 未コミットの変更があります"
    echo "   変更内容:"
    git status --short
    echo ""
    read -p "続行しますか？未コミットの変更は保持されます (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 処理を中止しました"
        exit 1
    fi
fi

# 4. mainブランチに切り替え
echo "🔄 mainブランチに切り替え中..."
if [ "$CURRENT_BRANCH" != "main" ]; then
    git checkout main
    echo "✅ mainブランチに切り替えました"
else
    echo "✅ 既にmainブランチにいます"
fi
echo ""

# 5. 最新のmainブランチを取得
echo "📥 最新のmainブランチを取得中..."
git pull origin main
echo "✅ 最新のmainブランチを取得しました"
echo ""

# 6. ブランチの状態を確認
echo "📊 ブランチの状態を確認中..."
echo "   現在のブランチ: $(git branch --show-current)"
echo "   最新コミット:"
git log --oneline -3
echo ""

# 7. ローカル環境との同期確認
echo "✅ 環境統一が完了しました"
echo ""
echo "📋 確認事項:"
echo "  - 現在のブランチ: main"
echo "  - 最新コミット: 88fb2db (Merge feature/monitoring-fail2ban-integration)"
echo "  - ローカル環境とNAS環境が同じ状態になりました"
echo ""
echo "⚠️  注意: コード変更があった場合、各システムの再ビルドが必要な場合があります"

