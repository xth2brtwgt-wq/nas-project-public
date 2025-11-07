#!/bin/bash
# Insta360自動同期 - 自動再マウント設定スクリプト

set -e

# カラー出力設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Insta360自動同期 - 自動再マウント設定 ===${NC}"
echo ""

# マウントポイント
MOUNT_POINT="/mnt/mac-share"
MOUNT_SOURCE="//YOUR_MAC_IP_ADDRESS/Insta360"
MOUNT_OPTIONS="username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755"

echo -e "${YELLOW}現在のfstab設定を確認中...${NC}"
if grep -q "mac-share" /etc/fstab; then
    echo "✅ fstabに設定が存在します:"
    grep "mac-share" /etc/fstab
else
    echo "❌ fstabに設定が存在しません"
fi

echo ""
echo -e "${YELLOW}自動再マウントの設定方法:${NC}"
echo ""
echo "1. **fstab設定（推奨）**: システム起動時に自動マウント"
echo "2. **systemd自動マウント**: マウントポイントにアクセスしたときに自動マウント"
echo "3. **cronジョブ**: 定期的にマウント状態をチェックして再マウント"
echo ""

echo -e "${BLUE}=== 方法1: systemd自動マウント（推奨） ===${NC}"
echo "systemd自動マウントを使用すると、マウントポイントにアクセスしたときに自動的にマウントされます。"
echo ""

read -p "systemd自動マウントを設定しますか？ (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}systemd自動マウントユニットを作成中...${NC}"
    
    # systemd自動マウントユニットファイルを作成
    cat > /tmp/mnt-mac-share.automount << EOF
[Unit]
Description=Mac Share Auto Mount
After=network-online.target
Wants=network-online.target

[Automount]
Where=${MOUNT_POINT}
TimeoutIdleSec=0

[Install]
WantedBy=multi-user.target
EOF

    # systemdマウントユニットファイルを作成
    cat > /tmp/mnt-mac-share.mount << EOF
[Unit]
Description=Mac Share Mount
After=network-online.target
Wants=network-online.target

[Mount]
What=${MOUNT_SOURCE}
Where=${MOUNT_POINT}
Type=cifs
Options=${MOUNT_OPTIONS}

[Install]
WantedBy=multi-user.target
EOF

    echo "自動マウントユニットファイルを作成しました:"
    echo "  - /etc/systemd/system/mnt-mac-share.automount"
    echo "  - /etc/systemd/system/mnt-mac-share.mount"
    echo ""
    echo "以下のコマンドで設定を反映します:"
    echo "  sudo cp /tmp/mnt-mac-share.automount /etc/systemd/system/"
    echo "  sudo cp /tmp/mnt-mac-share.mount /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable --now mnt-mac-share.automount"
fi

echo ""
echo -e "${BLUE}=== 方法2: cronジョブ（シンプル） ===${NC}"
echo "cronジョブを使用して、定期的にマウント状態をチェックして再マウントします。"
echo ""

read -p "cronジョブを設定しますか？ (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}cronジョブスクリプトを作成中...${NC}"
    
    # cronジョブスクリプトを作成
    cat > /tmp/check-mac-share-mount.sh << 'EOF'
#!/bin/bash
# Mac Share マウント状態チェックスクリプト

MOUNT_POINT="/mnt/mac-share"
MOUNT_SOURCE="//YOUR_MAC_IP_ADDRESS/Insta360"
MOUNT_OPTIONS="username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755"

# マウント状態をチェック
if ! mount | grep -q "${MOUNT_POINT}"; then
    logger "Mac Share マウントが解除されています。再マウントを実行します。"
    mount -t cifs "${MOUNT_SOURCE}" "${MOUNT_POINT}" -o "${MOUNT_OPTIONS}"
    if [ $? -eq 0 ]; then
        logger "Mac Share マウントが成功しました。"
    else
        logger "Mac Share マウントに失敗しました。"
    fi
fi
EOF

    chmod +x /tmp/check-mac-share-mount.sh
    
    echo "cronジョブスクリプトを作成しました: /tmp/check-mac-share-mount.sh"
    echo ""
    echo "以下のコマンドで設定を反映します:"
    echo "  sudo cp /tmp/check-mac-share-mount.sh /usr/local/bin/"
    echo "  sudo chmod +x /usr/local/bin/check-mac-share-mount.sh"
    echo "  (crontab -l 2>/dev/null; echo '*/5 * * * * /usr/local/bin/check-mac-share-mount.sh') | crontab -"
    echo "  （5分ごとにマウント状態をチェック）"
fi

echo ""
echo -e "${GREEN}設定完了！${NC}"
echo ""
echo -e "${YELLOW}注意事項:${NC}"
echo "1. fstab設定はシステム起動時にのみ自動マウントされます"
echo "2. 実行中にマウントが解除された場合は、systemd自動マウントまたはcronジョブが必要です"
echo "3. systemd自動マウントは、マウントポイントへのアクセス時に自動的にマウントします"
echo "4. cronジョブは、定期的にマウント状態をチェックして再マウントします"











