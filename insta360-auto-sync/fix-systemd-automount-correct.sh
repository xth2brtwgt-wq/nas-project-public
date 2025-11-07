#!/bin/bash
# Insta360自動同期 - systemd自動マウント修正スクリプト（正しい方法）

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

# systemdでは、マウントポイントのパスからユニット名を決定
# /mnt/mac-share → mnt-mac-share (スラッシュをハイフンに変換)
UNIT_NAME="mnt-mac-share"

echo "=== systemd自動マウント設定を修正 ==="
echo "マウントポイント: ${MOUNT_POINT}"
echo "ユニット名: ${UNIT_NAME}"
echo ""

# 1. 既存のユニットファイルを完全に削除
echo "既存のユニットファイルを削除中..."
sudo systemctl stop ${UNIT_NAME}.automount 2>/dev/null || true
sudo systemctl stop ${UNIT_NAME}.mount 2>/dev/null || true
sudo systemctl disable ${UNIT_NAME}.automount 2>/dev/null || true
sudo systemctl disable ${UNIT_NAME}.mount 2>/dev/null || true
sudo rm -f /etc/systemd/system/${UNIT_NAME}.automount
sudo rm -f /etc/systemd/system/${UNIT_NAME}.mount
sudo systemctl daemon-reload

# 2. マウントポイントがマウントされている場合は解除
if mount | grep -q "${MOUNT_POINT}"; then
    echo "既存のマウントを解除中..."
    sudo umount "${MOUNT_POINT}" 2>/dev/null || true
fi

# 3. マウントユニットファイルを作成（先に作成する必要がある）
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

# 5. ファイルの内容を確認
echo ""
echo "=== 作成されたユニットファイルの内容確認 ==="
echo "--- ${UNIT_NAME}.mount ---"
cat /etc/systemd/system/${UNIT_NAME}.mount
echo ""
echo "--- ${UNIT_NAME}.automount ---"
cat /etc/systemd/system/${UNIT_NAME}.automount

# 6. systemd設定を再読み込み
echo ""
echo "systemd設定を再読み込み中..."
sudo systemctl daemon-reload

# 7. ユニットファイルの構文チェック
echo ""
echo "=== ユニットファイルの構文チェック ==="
sudo systemctl cat ${UNIT_NAME}.mount
sudo systemctl cat ${UNIT_NAME}.automount

# 8. 自動マウントを有効化
echo ""
echo "自動マウントを有効化中..."
sudo systemctl enable ${UNIT_NAME}.automount
sudo systemctl start ${UNIT_NAME}.automount

# 9. 動作確認
echo ""
echo "=== 動作確認 ==="
sudo systemctl status ${UNIT_NAME}.automount --no-pager -l

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











