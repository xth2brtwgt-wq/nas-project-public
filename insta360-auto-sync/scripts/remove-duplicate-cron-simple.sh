#!/bin/bash
# Insta360自動同期 - cronジョブ重複削除スクリプト（シンプル版）

set -e

echo "=== cronジョブ重複削除 ==="
echo ""

# 1. 現在のcrontabを取得
echo "現在のcrontabを取得しています..."
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt
crontab -l > /tmp/my_crontab

# 2. 重複を削除（最初の1つだけ残す）
echo "重複を削除しています..."
awk 'BEGIN {found=0} /sync-with-mount-check\.sh/ {if (found==0) {found=1; print} next} {print}' /tmp/my_crontab > /tmp/my_crontab.new

# 3. 新しいcrontabを設定
echo "新しいcrontabを設定しています..."
crontab /tmp/my_crontab.new

# 4. 設定後のcrontabを確認
echo ""
echo "=== 設定後のcrontab ==="
crontab -l

# 5. insta360関連のエントリを確認
echo ""
echo "=== insta360関連のエントリ（重複削除後） ==="
INSTA360_LINES=$(crontab -l | grep "sync-with-mount-check.sh" | wc -l)
echo "エントリ数: ${INSTA360_LINES}"
crontab -l | grep "sync-with-mount-check.sh" || echo "エントリが見つかりません"

if [ "${INSTA360_LINES}" -eq 1 ]; then
    echo ""
    echo "✅ 重複が削除されました（エントリ数: 1）"
else
    echo ""
    echo "⚠️  まだ重複がある可能性があります（エントリ数: ${INSTA360_LINES}）"
fi

# 6. 一時ファイルを削除
rm -f /tmp/my_crontab /tmp/my_crontab.new

echo ""
echo "✅ 完了しました"
echo "バックアップ: /tmp/crontab_backup_*.txt"











