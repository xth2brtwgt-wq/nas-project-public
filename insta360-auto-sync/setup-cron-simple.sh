#!/bin/bash
# Insta360自動同期 - cronジョブ設定（シンプル版）

echo "=== cronジョブによる自動再マウント設定 ==="
echo ""

# 1. マウントチェックスクリプトが存在するか確認
if [ ! -f "/usr/local/bin/check-mac-share-mount.sh" ]; then
    echo "❌ マウントチェックスクリプトが見つかりません"
    echo "まず /usr/local/bin/check-mac-share-mount.sh を作成してください"
    exit 1
fi

# 2. 現在のcronジョブを表示
echo "現在のcronジョブ:"
crontab -l 2>/dev/null || echo "cronジョブが存在しません"

# 3. 既存のcheck-mac-share-mountエントリを削除して再追加
echo ""
echo "cronジョブを設定中..."
TEMP_CRON=$(mktemp)
crontab -l 2>/dev/null | grep -v "check-mac-share-mount" > "$TEMP_CRON" || true
echo "*/5 * * * * /usr/local/bin/check-mac-share-mount.sh" >> "$TEMP_CRON"
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

# 4. cronジョブを確認
echo ""
echo "=== 設定されたcronジョブ ==="
crontab -l | grep check-mac-share-mount

# 5. 手動でスクリプトを実行してテスト
echo ""
echo "=== 手動でスクリプトを実行してテスト ==="
sudo /usr/local/bin/check-mac-share-mount.sh

# 6. マウント状態を確認
echo ""
echo "=== マウント状態を確認 ==="
if mount | grep -q "/mnt/mac-share"; then
    echo "✅ マウントされています"
    mount | grep mac-share
else
    echo "❌ マウントされていません"
fi

echo ""
echo "✅ 設定完了！"
echo ""
echo "cronジョブは5分ごとに実行され、マウント状態をチェックして再マウントします。"











