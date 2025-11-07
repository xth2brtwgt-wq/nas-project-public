#!/bin/bash
# Insta360自動同期 - systemd自動マウント修正スクリプト

set -e

MOUNT_POINT="/mnt/mac-share"
MOUNT_SOURCE="//YOUR_MAC_IP_ADDRESS/Insta360"
MOUNT_OPTIONS="username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755"

# systemdでは、パスに基づいてユニット名を決定する必要がある
# /mnt/mac-share → mnt-mac-share (スラッシュをハイフンに変換)
UNIT_NAME="mnt-mac-share"

echo "=== systemd自動マウント設定を修正 ==="
echo ""

# 1. 既存のユニットファイルを削除
echo "既存のユニットファイルを削除中..."
sudo systemctl stop ${UNIT_NAME}.automount 2>/dev/null || true
sudo systemctl disable ${UNIT_NAME}.automount 2>/dev/null || true
sudo rm -f /etc/systemd/system/${UNIT_NAME}.automount
sudo rm -f /etc/systemd/system/${UNIT_NAME}.mount

# 2. systemd設定を再読み込み
sudo systemctl daemon-reload

# 3. マウントユニットファイルを作成
echo "マウントユニットファイルを作成中..."
sudo tee /etc/systemd/system/${UNIT_NAME}.mount > /dev/null << EOF
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

# 4. 自動マウントユニットファイルを作成
echo "自動マウントユニットファイルを作成中..."
sudo tee /etc/systemd/system/${UNIT_NAME}.automount > /dev/null << EOF
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

# 5. systemd設定を再読み込み
echo "systemd設定を再読み込み中..."
sudo systemctl daemon-reload

# 6. 自動マウントを有効化
echo "自動マウントを有効化中..."
sudo systemctl enable --now ${UNIT_NAME}.automount

# 7. 動作確認
echo ""
echo "=== 動作確認 ==="
sudo systemctl status ${UNIT_NAME}.automount --no-pager

echo ""
echo "=== マウントポイントにアクセスして自動マウントをテスト ==="
ls ${MOUNT_POINT} 2>/dev/null && echo "✅ マウント成功" || echo "⚠️  マウントされていません"

echo ""
echo "=== マウント状態を確認 ==="
mount | grep mac-share || echo "マウントされていません"

echo ""
echo "✅ 設定完了！"
echo ""
echo "使用方法:"
echo "  - マウントポイント ${MOUNT_POINT} にアクセスすると自動的にマウントされます"
echo "  - 状態確認: sudo systemctl status ${UNIT_NAME}.automount"
echo "  - 手動マウント: sudo systemctl start ${UNIT_NAME}.mount"
echo "  - 手動アンマウント: sudo systemctl stop ${UNIT_NAME}.mount"











