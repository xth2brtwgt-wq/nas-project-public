#!/bin/bash
# Insta360自動同期 - cronジョブによる自動再マウント設定

set -e

MOUNT_POINT="/mnt/mac-share"
MOUNT_SOURCE="${MOUNT_SOURCE:-//YOUR_MAC_IP_ADDRESS/Insta360}"
MOUNT_OPTIONS="${MOUNT_OPTIONS:-username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755}"

# 環境変数が設定されていない場合は警告
if [ "${MOUNT_SOURCE}" = "//YOUR_MAC_IP_ADDRESS/Insta360" ] || [ "${MOUNT_OPTIONS}" = "username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755" ]; then
    echo "⚠️  警告: 環境変数 MOUNT_SOURCE と MOUNT_OPTIONS を設定してください"
    echo "   例: export MOUNT_SOURCE='//192.168.1.100/Insta360'"
    echo "   例: export MOUNT_OPTIONS='username=your_user,password=your_pass,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755'"
    exit 1
fi

echo "=== cronジョブによる自動再マウント設定 ==="
echo ""

# 1. マウントチェックスクリプトを作成
echo "マウントチェックスクリプトを作成中..."
sudo tee /usr/local/bin/check-mac-share-mount.sh > /dev/null << EOF
#!/bin/bash
# Mac Share マウント状態チェックスクリプト

MOUNT_POINT="${MOUNT_POINT}"
MOUNT_SOURCE="${MOUNT_SOURCE}"
MOUNT_OPTIONS="${MOUNT_OPTIONS}"

# マウント状態をチェック
if ! mount | grep -q "\${MOUNT_POINT}"; then
    logger "Mac Share マウントが解除されています。再マウントを実行します。"
    mount -t cifs "\${MOUNT_SOURCE}" "\${MOUNT_POINT}" -o "\${MOUNT_OPTIONS}"
    if [ \$? -eq 0 ]; then
        logger "Mac Share マウントが成功しました。"
    else
        logger "Mac Share マウントに失敗しました。"
    fi
fi
EOF

# 2. 実行権限を付与
sudo chmod +x /usr/local/bin/check-mac-share-mount.sh

# 3. cronジョブを追加（5分ごとにチェック）
echo ""
echo "cronジョブを追加中..."
(crontab -l 2>/dev/null | grep -v "check-mac-share-mount"; echo "*/5 * * * * /usr/local/bin/check-mac-share-mount.sh") | crontab -

# 4. cronジョブを確認
echo ""
echo "=== 設定されたcronジョブ ==="
crontab -l | grep check-mac-share-mount || echo "cronジョブが見つかりません"

# 5. 手動でスクリプトを実行してテスト
echo ""
echo "=== 手動でスクリプトを実行してテスト ==="
sudo /usr/local/bin/check-mac-share-mount.sh

# 6. マウント状態を確認
echo ""
echo "=== マウント状態を確認 ==="
if mount | grep -q "${MOUNT_POINT}"; then
    echo "✅ マウントされています"
    mount | grep mac-share
else
    echo "❌ マウントされていません"
fi

echo ""
echo "✅ 設定完了！"
echo ""
echo "使用方法:"
echo "  - 5分ごとにマウント状態をチェックして、解除されていれば再マウントします"
echo "  - 手動で実行: sudo /usr/local/bin/check-mac-share-mount.sh"
echo "  - cronジョブの確認: crontab -l | grep check-mac-share-mount"
echo "  - ログの確認: journalctl -u cron | grep 'Mac Share' | tail -10"











