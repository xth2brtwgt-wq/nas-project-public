#!/bin/bash
# Git履歴から.envファイルを削除するスクリプト
# ⚠️ 警告: このスクリプトは破壊的な操作です。実行前に必ずバックアップを取ってください。

set -e  # エラーが発生したら処理を停止

echo "⚠️  警告: この操作はGit履歴を書き換えます"
echo "   - すべてのブランチの履歴が変更されます"
echo "   - リモートにpushするにはforce pushが必要です"
echo "   - チームで共有している場合は全員に通知が必要です"
echo ""
read -p "続行しますか？ (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy]([Ee][Ss])?$ ]]; then
    echo "❌ 処理を中止しました"
    exit 1
fi

echo "📦 バックアップを作成中..."
cd ~
if [ -d "nas-project-backup.git" ]; then
    echo "⚠️  既存のバックアップが見つかりました: nas-project-backup.git"
    read -p "上書きしますか？ (yes/no): " -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]([Ee][Ss])?$ ]]; then
        echo "❌ 処理を中止しました"
        exit 1
    fi
    rm -rf nas-project-backup.git
fi

git clone --mirror https://github.com/xth2brtwgt-wq/dpx2800-nas-system.git nas-project-backup.git
echo "✅ バックアップを作成しました: ~/nas-project-backup.git"
echo ""

cd ~/nas-project

echo "🔍 削除対象の.envファイルを確認中..."
git log --all --full-history --pretty=format: --name-only -- "*.env" | sort -u | grep -E "\.env$"
echo ""

echo "🗑️  Git履歴から.envファイルを削除中..."
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env \
                                      amazon-analytics/.env \
                                      document-automation/.env \
                                      nas-dashboard/.env \
                                      insta360-auto-sync/.env \
                                      notion-knowledge-summaries/.env \
                                      youtube-to-notion/.env \
                                      docker/fail2ban/.env \
                                      meeting-minutes-byc/.env" \
  --prune-empty --tag-name-filter cat -- --all

echo ""
echo "🧹 一時ファイルを削除中..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "✅ 確認中..."
ENV_FILES=$(git log --all --full-history --pretty=format: --name-only -- "*.env" | sort -u | grep -E "\.env$" || echo "")
if [ -z "$ENV_FILES" ]; then
    echo "✅ 成功: Git履歴から.envファイルが削除されました"
else
    echo "⚠️  警告: 以下のファイルが履歴に残っています:"
    echo "$ENV_FILES"
fi
echo ""
echo "📋 次のステップ:"
echo "  1. 履歴を確認: git log --all --oneline | head -10"
echo "  2. リモートに反映（force pushが必要）:"
echo "     git push origin --force --all"
echo "     git push origin --force --tags"
echo ""
echo "⚠️  重要: force pushはチームメンバーに通知してから実行してください"

