#!/bin/bash
# Insta360自動同期 - systemdタイマー動作確認スクリプト

echo "=== systemdタイマーの動作確認 ==="
echo ""

# 1. タイマーの状態確認
echo "=== タイマーの状態 ==="
sudo systemctl status check-mac-share-mount.timer --no-pager -l

echo ""
echo "=== タイマーの一覧（該当のみ） ==="
sudo systemctl list-timers | grep check-mac-share-mount

echo ""
echo "=== サービスの状態 ==="
sudo systemctl status check-mac-share-mount.service --no-pager -l || echo "サービスはまだ実行されていません"

echo ""
echo "=== 手動でサービスを実行してテスト ==="
sudo systemctl start check-mac-share-mount.service

echo ""
echo "=== 実行後のログ確認 ==="
sudo journalctl -u check-mac-share-mount.service -n 10 --no-pager

echo ""
echo "=== マウント状態を確認 ==="
if mount | grep -q "/mnt/mac-share"; then
    echo "✅ マウントされています"
    mount | grep mac-share
else
    echo "❌ マウントされていません"
fi

echo ""
echo "✅ 確認完了！"
echo ""
echo "タイマーは5分ごとに実行され、マウント状態をチェックして再マウントします。"











