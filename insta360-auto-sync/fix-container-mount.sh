#!/bin/bash
# Insta360自動同期 - コンテナマウント修正スクリプト

echo "=== 1. マウント状態の確認 ==="
mount | grep mac-share

echo ""
echo "=== 2. /mnt/mac-share の内容確認 ==="
ls -la /mnt/mac-share
echo ""
echo "Downloadディレクトリの内容:"
ls -la /mnt/mac-share/Download 2>/dev/null || echo "Downloadディレクトリが見つかりません"

echo ""
echo "=== 3. Dockerコンテナの状態確認 ==="
docker ps | grep insta360-auto-sync

echo ""
echo "=== 4. コンテナを再起動（docker composeを使用） ==="
cd ~/nas-project/insta360-auto-sync
docker compose down
docker compose up -d

echo ""
echo "=== 5. コンテナの起動を待機 ==="
sleep 5

echo ""
echo "=== 6. コンテナ内の /source 確認 ==="
docker exec insta360-auto-sync ls -la /source

echo ""
echo "=== 7. コンテナ内の Download ディレクトリ確認 ==="
docker exec insta360-auto-sync ls -la /source/Download 2>/dev/null || echo "Downloadディレクトリが見つかりません"

echo ""
echo "=== 8. コンテナ内でファイル検索 ==="
docker exec insta360-auto-sync find /source -type f | head -10

echo ""
echo "=== 9. テスト実行 ==="
docker exec insta360-auto-sync python /app/scripts/sync.py --test











