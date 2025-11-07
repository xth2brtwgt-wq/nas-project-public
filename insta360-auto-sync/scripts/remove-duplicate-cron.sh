#!/bin/bash
# Insta360自動同期 - cronジョブ重複削除スクリプト

set -e

CURRENT_USER=$(whoami)
CRONTAB_FILE="/var/spool/cron/crontabs/${CURRENT_USER}"
SYNC_SCRIPT="~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh"

echo "=== cronジョブ重複削除 ==="
echo ""

# 1. 現在のcrontabを取得
echo "現在のcrontabを取得しています..."
CRON_CONTENT=$(crontab -l 2>/dev/null || echo "")

# 2. insta360関連のエントリを確認
echo ""
echo "=== insta360関連のエントリ ==="
echo "${CRON_CONTENT}" | grep "sync-with-mount-check.sh" || echo "エントリが見つかりません"

# 3. 重複を削除（最初の1つだけ残す）
echo ""
echo "重複を削除しています..."
NEW_CRON=$(echo "${CRON_CONTENT}" | awk '
BEGIN {
    found = 0
}
/sync-with-mount-check\.sh/ {
    if (found == 0) {
        found = 1
        print
    }
    next
}
{
    print
}
')

# 4. 新しいcrontabを設定
echo "新しいcrontabを設定しています..."
echo "${NEW_CRON}" | crontab -

# 5. 設定後のcrontabを確認
echo ""
echo "=== 設定後のcrontab ==="
crontab -l

# 6. insta360関連のエントリを確認
echo ""
echo "=== insta360関連のエントリ（重複削除後） ==="
INSTA360_COUNT=$(crontab -l | grep -c "sync-with-mount-check.sh" || echo "0")
echo "エントリ数: ${INSTA360_COUNT}"
crontab -l | grep "sync-with-mount-check.sh" || echo "エントリが見つかりません"

if [ "${INSTA360_COUNT}" -eq 1 ]; then
    echo ""
    echo "✅ 重複が削除されました"
else
    echo ""
    echo "⚠️  まだ重複がある可能性があります"
fi

echo ""
echo "✅ 完了しました"











