#!/bin/bash
# Insta360自動同期 - 更新状態確認スクリプト

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../" && pwd)"

echo "=== Insta360自動同期システム - 更新状態確認 ==="
echo ""

cd "${PROJECT_DIR}"

# 1. 現在のブランチとコミットを確認
echo "=== Git状態 ==="
echo "現在のブランチ: $(git branch --show-current)"
echo "最新のコミット: $(git log -1 --oneline)"
echo ""

# 2. リモートとの差分を確認
echo "=== リモートとの差分 ==="
git fetch origin 2>/dev/null || echo "リモートの取得に失敗しました"

LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/$(git branch --show-current) 2>/dev/null || echo "")

if [ -z "${REMOTE_COMMIT}" ]; then
    echo "⚠️  リモートブランチが見つかりません"
elif [ "${LOCAL_COMMIT}" = "${REMOTE_COMMIT}" ]; then
    echo "✅ ローカルとリモートは同期されています"
else
    echo "⚠️  ローカルとリモートに差分があります"
    echo "ローカル: ${LOCAL_COMMIT:0:7}"
    echo "リモート: ${REMOTE_COMMIT:0:7}"
    echo ""
    echo "更新するには: git pull"
fi
echo ""

# 3. 重要なファイルの存在確認
echo "=== 重要なファイルの存在確認 ==="
FILES=(
    "scripts/sync-with-mount-check.sh"
    "scripts/setup-cron-sync.sh"
    "scripts/remove-duplicate-cron.sh"
    "utils/mount_utils.py"
    "SYNC_WITH_MOUNT_CHECK.md"
    "SETUP_GUIDE.md"
    "CRON_SETUP_MANUAL.md"
    "CRON_TROUBLESHOOTING.md"
)

for file in "${FILES[@]}"; do
    if [ -f "${file}" ]; then
        echo "✅ ${file}"
    else
        echo "❌ ${file} (見つかりません)"
    fi
done
echo ""

# 4. スクリプトの実行権限確認
echo "=== スクリプトの実行権限確認 ==="
SCRIPTS=(
    "scripts/sync-with-mount-check.sh"
    "scripts/setup-cron-sync.sh"
    "scripts/remove-duplicate-cron.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "${script}" ]; then
        if [ -x "${script}" ]; then
            echo "✅ ${script} (実行権限あり)"
        else
            echo "⚠️  ${script} (実行権限なし - chmod +x ${script} を実行してください)"
        fi
    fi
done
echo ""

# 5. 環境変数ファイルの確認
echo "=== 環境変数ファイルの確認 ==="
if [ -f ".env" ]; then
    echo "✅ .env (存在します - 実際の稼働設定)"
else
    echo "⚠️  .env (存在しません - env.exampleからコピーして作成してください)"
fi

if [ -f ".env.restore" ]; then
    echo "✅ .env.restore (存在します - バックアップ用)"
else
    echo "⚠️  .env.restore (存在しません - .envからバックアップを作成することを推奨: cp .env .env.restore)"
fi

if [ -f "env.example" ]; then
    echo "✅ env.example (存在します - テンプレート)"
else
    echo "❌ env.example (見つかりません)"
fi
echo ""

# 6. cronジョブの確認
echo "=== cronジョブの確認 ==="
if crontab -l 2>/dev/null | grep -q "sync-with-mount-check.sh"; then
    echo "✅ cronジョブが設定されています"
    crontab -l | grep "sync-with-mount-check.sh"
else
    echo "⚠️  cronジョブが設定されていません"
    echo "設定するには: ./scripts/setup-cron-sync.sh または crontab -e"
fi
echo ""

# 7. Dockerコンテナの確認
echo "=== Dockerコンテナの確認 ==="
if docker ps | grep -q "insta360-auto-sync"; then
    echo "✅ コンテナが実行中です"
    docker ps | grep "insta360-auto-sync"
else
    echo "⚠️  コンテナが実行されていません"
    echo "起動するには: ./deploy.sh"
fi
echo ""

# 8. マウント状態の確認
echo "=== マウント状態の確認 ==="
if mount | grep -q "/mnt/mac-share"; then
    echo "✅ マウントされています"
    mount | grep "/mnt/mac-share"
else
    echo "⚠️  マウントされていません（同期処理実行時に自動的にマウントされます）"
fi
echo ""

echo "=== 確認完了 ==="
echo ""
echo "更新が必要な場合:"
echo "  1. git pull"
echo "  2. chmod +x scripts/*.sh"
echo "  3. ./scripts/setup-cron-sync.sh (cronジョブが設定されていない場合)"

