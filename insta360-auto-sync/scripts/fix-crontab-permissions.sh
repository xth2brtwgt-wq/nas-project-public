#!/bin/bash
# Insta360自動同期 - crontabファイル権限修正スクリプト

set -e

CURRENT_USER=$(whoami)
CRONTAB_FILE="/var/spool/cron/crontabs/${CURRENT_USER}"

echo "=== crontabファイル権限修正 ==="
echo ""

echo "現在のユーザー: ${CURRENT_USER}"
echo "crontabファイル: ${CRONTAB_FILE}"
echo ""

# 1. crontabファイルの存在確認
if [ ! -f "${CRONTAB_FILE}" ]; then
    echo "⚠️  crontabファイルが存在しません"
    echo "空のcrontabファイルを作成します..."
    touch "${CRONTAB_FILE}"
fi

# 2. 現在の権限を確認
echo "=== 現在の権限 ==="
ls -la "${CRONTAB_FILE}"

# 3. 現在のユーザーのグループを確認
echo ""
echo "=== 現在のユーザーのグループ ==="
CURRENT_GROUP=$(id -gn ${CURRENT_USER})
echo "プライマリグループ: ${CURRENT_GROUP}"

# 4. 権限を修正
echo ""
echo "=== 権限を修正します ==="
sudo chmod 600 "${CRONTAB_FILE}"
sudo chown "${CURRENT_USER}:${CURRENT_GROUP}" "${CRONTAB_FILE}"

# 5. 修正後の権限を確認
echo ""
echo "=== 修正後の権限 ==="
ls -la "${CRONTAB_FILE}"

# 6. crontabの内容を確認
echo ""
echo "=== crontabの内容 ==="
crontab -l 2>/dev/null || echo "crontabが空です"

echo ""
echo "✅ 完了しました"











