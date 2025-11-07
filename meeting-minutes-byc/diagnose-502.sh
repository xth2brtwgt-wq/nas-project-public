#!/bin/bash

# 502エラー診断スクリプト
# 使用方法: ./diagnose-502.sh

echo "🔍 502 Bad Gateway エラー診断を開始します..."
echo ""

# 1. コンテナの状態確認
echo "📊 1. コンテナの状態確認:"
docker compose ps
echo ""

# 2. コンテナが起動しているか確認
echo "📊 2. meeting-minutes-bycコンテナの状態:"
if docker ps | grep -q "meeting-minutes-byc"; then
    echo "✅ コンテナは起動しています"
    CONTAINER_STATUS=$(docker ps --format "{{.Status}}" --filter "name=meeting-minutes-byc")
    echo "   状態: $CONTAINER_STATUS"
else
    echo "❌ コンテナが起動していません！"
    echo "   実行: docker compose up -d"
    exit 1
fi
echo ""

# 3. アプリケーションログの確認（直近50行）
echo "📋 3. アプリケーションログ（直近50行）:"
docker logs meeting-minutes-byc --tail 50
echo ""

# 4. エラーログの確認
echo "🔴 4. エラーログの確認:"
docker logs meeting-minutes-byc 2>&1 | grep -i "error\|exception\|traceback" | tail -20
echo ""

# 5. ヘルスチェック（コンテナ内部）
echo "🏥 5. コンテナ内部でのヘルスチェック:"
if docker exec meeting-minutes-byc curl -f http://localhost:5000/health >/dev/null 2>&1; then
    echo "✅ アプリケーションは正常に応答しています"
    docker exec meeting-minutes-byc curl -s http://localhost:5000/health
else
    echo "❌ アプリケーションが応答していません"
fi
echo ""

# 6. ポート5002の確認（ホスト側）
echo "🌐 6. ホスト側からのポート5002アクセステスト:"
if curl -f http://localhost:5002/health >/dev/null 2>&1; then
    echo "✅ ポート5002は正常に動作しています"
    curl -s http://localhost:5002/health
else
    echo "❌ ポート5002にアクセスできません"
    echo "   ポートマッピングを確認してください"
fi
echo ""

# 7. 環境変数の確認
echo "⚙️ 7. 重要な環境変数の確認:"
docker exec meeting-minutes-byc env | grep -E "GEMINI_API_KEY|FLASK_ENV|PORT|HOST" | sed 's/=.*/=***/'
echo ""

# 8. ファイルマウントの確認
echo "📁 8. ボリュームマウントの確認:"
docker inspect meeting-minutes-byc | grep -A 10 "Mounts" | grep -E "Source|Destination" | head -10
echo ""

# 9. ネットワーク接続の確認
echo "🌐 9. Nginx Proxy Managerからの接続テスト:"
if docker ps | grep -q "nginx-proxy-manager"; then
    echo "   Nginx Proxy Managerコンテナからテスト:"
    docker exec nginx-proxy-manager curl -I http://YOUR_IP_ADDRESS110:5002/health 2>&1 | head -5
else
    echo "   ⚠️ Nginx Proxy Managerコンテナが見つかりません"
fi
echo ""

# 10. 推奨される修正手順
echo "🔧 10. 推奨される修正手順:"
echo ""
echo "   コンテナが起動していない場合:"
echo "   docker compose up -d"
echo ""
echo "   アプリケーションエラーの場合:"
echo "   docker compose down"
echo "   docker compose build --no-cache"
echo "   docker compose up -d"
echo ""
echo "   ログを詳しく確認:"
echo "   docker logs meeting-minutes-byc --tail 100"
echo ""

echo "🎉 診断完了！"









