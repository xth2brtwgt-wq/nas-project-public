#!/bin/bash
# Insta360自動同期 - systemd自動マウント完全リセットスクリプト

set -e

MOUNT_POINT="/mnt/mac-share"
MOUNT_SOURCE="//YOUR_MAC_IP_ADDRESS/Insta360"
MOUNT_OPTIONS="username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755"
UNIT_NAME="mnt-mac-share"

echo "=== systemd自動マウント設定を完全リセット ==="
echo ""

# 1. 既存のマウントを解除
echo "既存のマウントを解除中..."
if mount | grep -q "${MOUNT_POINT}"; then
    sudo umount "${MOUNT_POINT}" 2>/dev/null || true
    echo "✅ マウントを解除しました"
else
    echo "マウントされていません"
fi

# 2. 既存のユニットを完全に削除
echo ""
echo "既存のユニットファイルを削除中..."
sudo systemctl stop ${UNIT_NAME}.automount 2>/dev/null || true
sudo systemctl stop ${UNIT_NAME}.mount 2>/dev/null || true
sudo systemctl disable ${UNIT_NAME}.automount 2>/dev/null || true
sudo systemctl disable ${UNIT_NAME}.mount 2>/dev/null || true
sudo rm -f /etc/systemd/system/${UNIT_NAME}.automount
sudo rm -f /etc/systemd/system/${UNIT_NAME}.mount
sudo rm -f /etc/systemd/system/multi-user.target.wants/${UNIT_NAME}.automount
sudo rm -f /etc/systemd/system/multi-user.target.wants/${UNIT_NAME}.mount
sudo systemctl daemon-reload

# 3. マウントユニットファイルを作成
echo ""
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
echo "=== 作成されたユニットファイルの内容 ==="
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
if sudo systemctl cat ${UNIT_NAME}.mount > /dev/null 2>&1; then
    echo "✅ ${UNIT_NAME}.mount の構文は正しいです"
else
    echo "❌ ${UNIT_NAME}.mount に構文エラーがあります"
    sudo systemctl cat ${UNIT_NAME}.mount
fi

if sudo systemctl cat ${UNIT_NAME}.automount > /dev/null 2>&1; then
    echo "✅ ${UNIT_NAME}.automount の構文は正しいです"
else
    echo "❌ ${UNIT_NAME}.automount に構文エラーがあります"
    sudo systemctl cat ${UNIT_NAME}.automount
fi

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
if ls ${MOUNT_POINT} > /dev/null 2>&1; then
    echo "✅ マウント成功"
    mount | grep mac-share
else
    echo "⚠️  マウントされていません"
    echo "手動でマウントをテスト:"
    echo "  sudo systemctl start ${UNIT_NAME}.mount"
fi

echo ""
echo "✅ 設定完了！"











