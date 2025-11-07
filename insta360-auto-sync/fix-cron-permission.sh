#!/bin/bash
# Insta360自動同期 - cronジョブ権限修正スクリプト

echo "=== cronジョブの権限を修正 ==="
echo ""

# 1. cronジョブの確認
echo "現在のcronジョブ:"
crontab -l 2>/dev/null | grep check-mac-share-mount || echo "cronジョブが見つかりません"

# 2. 既存のcronジョブから削除して再追加
echo ""
echo "cronジョブを設定中..."
(crontab -l 2>/dev/null | grep -v "check-mac-share-mount") | crontab - 2>/dev/null || true
echo "*/5 * * * * /usr/local/bin/check-mac-share-mount.sh" | crontab -

# 3. cronジョブを確認
echo ""
echo "=== 設定されたcronジョブ ==="
crontab -l | grep check-mac-share-mount || echo "cronジョブが見つかりません"

# 4. cronサービスの状態確認
echo ""
echo "=== cronサービスの状態 ==="
sudo systemctl status cron 2>/dev/null || sudo systemctl status crond 2>/dev/null || echo "cronサービスが見つかりません"

echo ""
echo "✅ 設定完了！"
echo ""
echo "cronジョブは5分ごとに実行され、マウント状態をチェックして再マウントします。"











