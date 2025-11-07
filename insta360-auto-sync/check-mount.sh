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
echo "=== 2. CIFSマウントの確認 ==="
if mount | grep -q "cifs"; then
    echo "✅ CIFSマウントが存在します:"
    mount | grep cifs
else
    echo "❌ CIFSマウントが存在しません"
fi

echo ""
echo "=== 3. Mac側への接続テスト ==="
MAC_IP="${MAC_IP:-YOUR_MAC_IP_ADDRESS}"
if [ "${MAC_IP}" != "YOUR_MAC_IP_ADDRESS" ] && ping -c 2 -W 2 "${MAC_IP}" > /dev/null 2>&1; then
    echo "✅ Mac側への接続成功"
else
    echo "❌ Mac側への接続失敗（IP: ${MAC_IP}）"
    echo "   環境変数 MAC_IP を設定してください"
fi

echo ""
echo "=== 4. /mnt/mac-share の確認 ==="
if [ -d "/mnt/mac-share" ]; then
    echo "✅ ディレクトリが存在します"
    echo "ファイル数: $(ls -A /mnt/mac-share 2>/dev/null | wc -l)"
    echo "権限: $(ls -ld /mnt/mac-share)"
    
    if mount | grep -q "mac-share"; then
        echo ""
        echo "=== 5. マウントされた共有フォルダの内容 ==="
        ls -la /mnt/mac-share | head -20
    else
        echo "⚠️  ディレクトリは存在しますが、マウントされていません"
    fi
else
    echo "❌ ディレクトリが存在しません"
fi

echo ""
echo "=== 6. fstab設定の確認 ==="
if grep -q "mac-share" /etc/fstab 2>/dev/null; then
    echo "✅ fstabに設定があります:"
    grep "mac-share" /etc/fstab
else
    echo "❌ fstabに設定がありません"
fi

echo ""
echo "=== 7. 推奨アクション ==="
if ! mount | grep -q "mac-share"; then
    echo "マウントを実行してください:"
    echo "  sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755"
    echo "  実際のIPアドレス、ユーザー名、パスワードに置き換えてください"
fi











