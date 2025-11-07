#!/bin/bash
# Insta360自動同期 - マウント成功後の確認スクリプト

echo "=== 1. マウント状態の確認 ==="
mount | grep mac-share

echo ""
echo "=== 2. /mnt/mac-share の内容確認 ==="
ls -la /mnt/mac-share

echo ""
echo "=== 3. Downloadディレクトリの内容確認 ==="
if [ -d "/mnt/mac-share/Download" ]; then
    echo "Downloadディレクトリが存在します"
    echo "ファイル数: $(find /mnt/mac-share/Download -type f 2>/dev/null | wc -l)"
    echo ""
    echo "ファイル一覧（最初の10件）:"
    find /mnt/mac-share/Download -type f 2>/dev/null | head -10
else
    echo "Downloadディレクトリが存在しません"
fi

echo ""
echo "=== 4. コンテナ内の /source 確認 ==="
echo "ディレクトリの存在確認:"
docker exec insta360-auto-sync test -d /source && echo "✅ /source は存在します" || echo "❌ /source は存在しません"

echo ""
echo "ファイル一覧:"
docker exec insta360-auto-sync ls -la /source

echo ""
echo "=== 5. コンテナ内の Download ディレクトリ確認 ==="
docker exec insta360-auto-sync ls -la /source/Download 2>/dev/null || echo "Downloadディレクトリが見つかりません"

echo ""
echo "=== 6. テスト実行 ==="
echo "テストモードで実行:"
docker exec insta360-auto-sync python /app/scripts/sync.py --test

echo ""
echo "=== 7. 実際の同期実行 ==="
echo "1回だけ同期を実行:"
docker exec insta360-auto-sync python /app/scripts/sync.py --once











