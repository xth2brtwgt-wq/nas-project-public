#!/bin/bash
#
# Git hooks セットアップスクリプト
# プロジェクト内のhooksテンプレートを.git/hooksにコピーします
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
HOOKS_SOURCE_DIR="$PROJECT_DIR/hooks"
GIT_HOOKS_DIR="$PROJECT_DIR/.git/hooks"

echo "🔧 Git hooks をセットアップ中..."

# .gitディレクトリが存在するか確認
if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo "❌ .gitディレクトリが見つかりません。Gitリポジトリ内で実行してください。"
    exit 1
fi

# hooksテンプレートディレクトリが存在するか確認
if [ ! -d "$HOOKS_SOURCE_DIR" ]; then
    echo "⚠️  hooksテンプレートディレクトリが見つかりません: $HOOKS_SOURCE_DIR"
    exit 1
fi

# .git/hooksディレクトリが存在しない場合は作成
if [ ! -d "$GIT_HOOKS_DIR" ]; then
    mkdir -p "$GIT_HOOKS_DIR"
fi

# hooksテンプレートをコピー
for hook in "$HOOKS_SOURCE_DIR"/*; do
    if [ -f "$hook" ]; then
        hook_name=$(basename "$hook")
        target_hook="$GIT_HOOKS_DIR/$hook_name"
        
        echo "📝 $hook_name をインストール中..."
        cp "$hook" "$target_hook"
        chmod +x "$target_hook"
        echo "   ✅ $hook_name をインストールしました"
    fi
done

echo ""
echo "✅ Git hooks のセットアップが完了しました！"
echo ""
echo "📋 インストールされたhooks:"
ls -la "$GIT_HOOKS_DIR" | grep -E "^-.*x" | awk '{print "   - " $9}'
echo ""

