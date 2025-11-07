#!/bin/bash
# Insta360自動同期 - マウント状態確認スクリプト

echo "=== 1. マウント状態の確認 ==="
if mount | grep -q "mac-share"; then
    echo "✅ マウントされています:"
    mount | grep mac-share
else
    echo "❌ マウントされていません"
fi

echo ""
echo "=== 2. /mnt/mac-share の確認 ==="
if [ -d "/mnt/mac-share" ]; then
    echo "✅ ディレクトリが存在します"
    echo "ファイル数: $(ls -A /mnt/mac-share 2>/dev/null | wc -l)"
    echo "権限: $(ls -ld /mnt/mac-share)"
    echo ""
    echo "=== /mnt/mac-share の内容 ==="
    ls -la /mnt/mac-share | head -20
else
    echo "❌ ディレクトリが存在しません"
fi

echo ""
echo "=== 3. コンテナ内の /source の確認 ==="
echo "ディレクトリの存在確認:"
docker exec insta360-auto-sync test -d /source && echo "✅ /source は存在します" || echo "❌ /source は存在しません"

echo ""
echo "ファイル一覧:"
docker exec insta360-auto-sync ls -la /source

echo ""
echo "=== 4. Mac側への接続テスト ==="
MAC_IP="${MAC_IP:-YOUR_MAC_IP_ADDRESS}"
MAC_USERNAME="${MAC_USERNAME:-YOUR_USERNAME}"
MAC_PASSWORD="${MAC_PASSWORD:-YOUR_PASSWORD}"
if [ "${MAC_IP}" != "YOUR_MAC_IP_ADDRESS" ] && ping -c 2 -W 2 "${MAC_IP}" > /dev/null 2>&1; then
    echo "✅ Mac側への接続成功"
else
    echo "❌ Mac側への接続失敗（IP: ${MAC_IP}）"
    echo "   環境変数 MAC_IP を設定してください"
fi

echo ""
echo "=== 5. SMB共有の確認 ==="
echo "共有フォルダ 'Insta360' が存在するか確認:"
if command -v smbclient >/dev/null 2>&1 && [ "${MAC_IP}" != "YOUR_MAC_IP_ADDRESS" ] && [ "${MAC_USERNAME}" != "YOUR_USERNAME" ] && [ "${MAC_PASSWORD}" != "YOUR_PASSWORD" ]; then
    smbclient -L "//${MAC_IP}" -U "${MAC_USERNAME}%${MAC_PASSWORD}" 2>/dev/null | grep -i insta360 || echo "共有フォルダ 'Insta360' が見つかりません"
else
    echo "smbclientが利用できないか、環境変数が設定されていません。手動で確認してください。"
fi

echo ""
echo "=== 6. 推奨アクション ==="
if ! mount | grep -q "mac-share"; then
    echo "⚠️  マウントされていません。以下を実行してください:"
    echo "  sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755"
    echo "  実際のIPアドレス、ユーザー名、パスワードに置き換えてください"
elif [ $(ls -A /mnt/mac-share 2>/dev/null | wc -l) -eq 0 ]; then
    echo "⚠️  マウントはされていますが、ディレクトリが空です。"
    echo "Mac側の共有フォルダ 'Insta360' にファイルが存在するか確認してください。"
fi











