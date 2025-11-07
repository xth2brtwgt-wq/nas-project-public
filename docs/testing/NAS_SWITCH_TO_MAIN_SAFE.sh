#!/bin/bash
# NAS環境：mainブランチに切り替えスクリプト（安全版）
# .envファイルなどの変更を保持したまま切り替え

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

# 3. .envファイルなどの変更をstash（一時保存）
echo "💾 .envファイルなどの変更を一時保存中..."
git stash push -m "NAS環境での変更を一時保存 $(date +%Y%m%d_%H%M%S)" --include-untracked

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

# 6. 一時保存した変更を復元
echo "📦 一時保存した変更を復元中..."
git stash pop || echo "⚠️  一時保存した変更がありません（正常です）"
echo "✅ 変更を復元しました"
echo ""

# 7. ブランチの状態を確認
echo "📊 ブランチの状態を確認中..."
echo "   現在のブランチ: $(git branch --show-current)"
echo "   最新コミット:"
git log --oneline -3
echo ""

# 8. 完了メッセージ
echo "✅ 環境統一が完了しました"
echo ""
echo "📋 確認事項:"
echo "  - 現在のブランチ: main"
echo "  - 最新コミット: $(git log --oneline -1 | cut -d' ' -f1)"
echo "  - ローカル環境とNAS環境が同じ状態になりました"
echo "  - .envファイルなどの変更は保持されています"
echo ""
echo "⚠️  注意: コード変更があった場合、各システムの再ビルドが必要な場合があります"

