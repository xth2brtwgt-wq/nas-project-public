#!/bin/bash
# Insta360自動同期 - cronジョブ追加スクリプト（権限エラー対策版）

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../" && pwd)"
SYNC_SCRIPT="${PROJECT_DIR}/scripts/sync-with-mount-check.sh"
LOG_FILE="${PROJECT_DIR}/../nas-project-data/insta360-auto-sync/logs/cron.log"
CRON_ENTRY="0 0 * * * ${SYNC_SCRIPT} >> ${LOG_FILE} 2>&1"

echo "=== Insta360自動同期 - cronジョブ追加 ==="
echo ""

# 現在のユーザーを確認
CURRENT_USER=$(whoami)
echo "現在のユーザー: ${CURRENT_USER}"

# crontabファイルの場所を確認
CRONTAB_FILE="/var/spool/cron/crontabs/${CURRENT_USER}"
echo "crontabファイル: ${CRONTAB_FILE}"

# 1. crontabファイルの権限を確認
if [ -f "${CRONTAB_FILE}" ]; then
    echo "既存のcrontabファイルが見つかりました"
    ls -la "${CRONTAB_FILE}"
else
    echo "crontabファイルが存在しません（新規作成）"
fi

# 2. 既存のcrontabを取得
echo ""
echo "既存のcrontabを取得しています..."
EXISTING_CRON=$(crontab -l 2>/dev/null || echo "")

# 3. 既にエントリが存在するか確認
if echo "${EXISTING_CRON}" | grep -q "sync-with-mount-check.sh"; then
    echo "⚠️  既にエントリが存在します"
    echo "${EXISTING_CRON}" | grep "sync-with-mount-check.sh"
    echo ""
    read -p "既存のエントリを削除して追加しますか？ (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 既存のエントリを削除
        EXISTING_CRON=$(echo "${EXISTING_CRON}" | grep -v "insta360-auto-sync" | grep -v "sync-with-mount-check.sh" | grep -v "sync.py")
    else
        echo "キャンセルしました"
        exit 0
    fi
fi

# 4. 新しいエントリを追加
echo ""
echo "新しいエントリを追加しています..."
NEW_CRON="${EXISTING_CRON}"
if [ -n "${EXISTING_CRON}" ]; then
    NEW_CRON="${EXISTING_CRON}"$'\n'"${CRON_ENTRY}"
else
    NEW_CRON="${CRON_ENTRY}"
fi

# 5. 一時ファイルに書き込み（/tmpではなく、ホームディレクトリを使用）
TEMP_CRON="${HOME}/.crontab.tmp"
echo "${NEW_CRON}" > "${TEMP_CRON}"

# 6. crontabファイルを設定
echo "crontabファイルを設定しています..."
if crontab "${TEMP_CRON}" 2>&1; then
    echo "✅ cronジョブの設定が完了しました"
    
    # 一時ファイルを削除
    rm -f "${TEMP_CRON}"
    
    # 設定を確認
    echo ""
    echo "=== 設定されたcronジョブ ==="
    crontab -l | grep -E "insta360|sync" || echo "cronジョブが見つかりません"
    echo ""
    echo "すべてのcronジョブ:"
    crontab -l
else
    echo "❌ cronジョブの設定に失敗しました"
    echo ""
    echo "代替方法を試してください:"
    echo "1. sudo crontab -e -u ${CURRENT_USER}"
    echo "2. または、crontabファイルを直接編集:"
    echo "   sudo vi ${CRONTAB_FILE}"
    
    # 一時ファイルを削除
    rm -f "${TEMP_CRON}"
    exit 1
fi

echo ""
echo "✅ 完了しました"











