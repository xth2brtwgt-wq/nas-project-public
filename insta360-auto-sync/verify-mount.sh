#!/bin/bash
# Insta360自動同期 - マウント検証スクリプト

echo "=== 1. Mac側の共有フォルダ確認 ==="
echo "Mac側のローカルパス: /Users/Yoshi/Movies/Insta360/"
echo "（このパスがファイル共有で公開されている必要があります）"
echo ""

echo "=== 2. NAS側のマウント状態確認 ==="
if mount | grep -q "mac-share"; then
    echo "✅ マウントされています:"
    mount | grep mac-share
else
    echo "❌ マウントされていません"
    echo "以下を実行してマウントしてください:"
    echo "  sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755"
fi

echo ""
echo "=== 3. /mnt/mac-share の内容確認 ==="
if [ -d "/mnt/mac-share" ]; then
    echo "ディレクトリが存在します"
    file_count=$(ls -A /mnt/mac-share 2>/dev/null | wc -l)
    echo "ファイル数: $file_count"
    if [ $file_count -gt 0 ]; then
        echo ""
        echo "ファイル一覧（最初の10件）:"
        ls -la /mnt/mac-share | head -10
    else
        echo "⚠️  ディレクトリが空です"
        echo "Mac側の共有フォルダ /Users/Yoshi/Movies/Insta360/ にファイルが存在するか確認してください"
    fi
else
    echo "❌ ディレクトリが存在しません"
fi

echo ""
echo "=== 4. コンテナ内の /source 確認 ==="
echo "コンテナ内のファイル一覧:"
docker exec insta360-auto-sync ls -la /source 2>/dev/null || echo "コンテナが見つかりません"

echo ""
echo "=== 5. 推奨アクション ==="
if ! mount | grep -q "mac-share"; then
    echo "1. Mac側でファイル共有を確認"
    echo "   - システム設定 > 一般 > 共有 > ファイル共有"
    echo "   - /Users/Yoshi/Movies/Insta360/ が共有されているか確認"
    echo ""
    echo "2. NAS側でマウントを実行"
    echo "   sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755"
elif [ $(ls -A /mnt/mac-share 2>/dev/null | wc -l) -eq 0 ]; then
    echo "1. Mac側で共有フォルダの内容を確認"
    echo "   ls -la /Users/Yoshi/Movies/Insta360/"
    echo ""
    echo "2. Mac側でファイル共有の設定を確認"
    echo "   - システム設定 > 一般 > 共有 > ファイル共有"
    echo "   - /Users/Yoshi/Movies/Insta360/ が共有されているか確認"
    echo "   - SMB共有が有効になっているか確認"
fi











