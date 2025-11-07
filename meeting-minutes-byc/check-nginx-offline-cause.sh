#!/bin/bash

# Nginx Proxy Manager オフライン原因調査スクリプト
# 使用方法: ./check-nginx-offline-cause.sh

echo "🔍 Nginx Proxy Manager オフライン原因を調査中..."
echo ""

# 1. Nginx設定の構文チェック
echo "📋 1. Nginx設定の構文チェック:"
if docker exec nginx-proxy-manager nginx -t 2>&1 | grep -q "test is successful"; then
    echo "✅ Nginx設定の構文は正常です"
else
    echo "❌ Nginx設定に構文エラーがあります"
    docker exec nginx-proxy-manager nginx -t
fi
echo ""

# 2. meeting-minutes-bycコンテナの状態確認
echo "📊 2. meeting-minutes-bycコンテナの状態:"
if docker ps | grep -q "meeting-minutes-byc"; then
    echo "✅ コンテナは起動しています"
    CONTAINER_STATUS=$(docker ps --format "{{.Status}}" --filter "name=meeting-minutes-byc")
    echo "   状態: $CONTAINER_STATUS"
else
    echo "❌ コンテナが起動していません"
    echo "   実行: docker compose up -d"
fi
echo ""

# 3. ポート5002への直接アクセステスト
echo "🌐 3. ポート5002への直接アクセステスト:"
if curl -f -s -o /dev/null -w "HTTP Status: %{http_code}\n" --max-time 5 http://YOUR_IP_ADDRESS110:5002/health; then
    echo "✅ ポート5002は正常に応答しています"
else
    echo "❌ ポート5002にアクセスできません"
fi
echo ""

# 4. レスポンス時間の測定
echo "⏱️ 4. レスポンス時間の測定:"
RESPONSE_TIME=$(curl -o /dev/null -s -w "%{time_total}" --max-time 10 http://YOUR_IP_ADDRESS110:5002/health 2>/dev/null)
if [ -n "$RESPONSE_TIME" ]; then
    echo "   レスポンス時間: ${RESPONSE_TIME}秒"
    if (( $(echo "$RESPONSE_TIME > 5" | bc -l) )); then
        echo "⚠️ レスポンスが遅いです（5秒以上）"
        echo "   ヘルスチェックがタイムアウトする可能性があります"
    else
        echo "✅ レスポンス時間は正常です"
    fi
else
    echo "❌ レスポンス時間を測定できませんでした"
fi
echo ""

# 5. Nginx Proxy Managerコンテナからの接続テスト
echo "🔗 5. Nginx Proxy Managerコンテナからの接続テスト:"
if docker ps | grep -q "nginx-proxy-manager"; then
    echo "   Nginx Proxy Managerコンテナからテスト:"
    if docker exec nginx-proxy-manager curl -f -s -o /dev/null -w "HTTP Status: %{http_code}\n" --max-time 5 http://YOUR_IP_ADDRESS110:5002/health; then
        echo "✅ Nginx Proxy Managerからアプリケーションへの接続は成功しています"
    else
        echo "❌ Nginx Proxy Managerからアプリケーションへの接続が失敗しています"
    fi
else
    echo "⚠️ Nginx Proxy Managerコンテナが見つかりません"
fi
echo ""

# 6. Nginx Proxy Managerのログ確認（エラー）
echo "📋 6. Nginx Proxy Managerのエラーログ確認:"
ERROR_LOG=$(docker logs nginx-proxy-manager --tail 200 2>&1 | grep -i "error\|502\|timeout\|offline" | tail -10)
if [ -n "$ERROR_LOG" ]; then
    echo "   エラーログが見つかりました:"
    echo "$ERROR_LOG"
else
    echo "✅ エラーログは見つかりませんでした"
fi
echo ""

# 7. Nginx Proxy Managerのヘルスチェック設定確認
echo "🏥 7. ヘルスチェック設定の確認:"
echo "   Nginx Proxy Managerは転送先サービスのヘルスチェックを実行します"
echo "   デフォルトのタイムアウトは約30秒です"
echo "   レスポンスが30秒以上かかる場合、オフラインと表示されます"
echo ""

# 8. 推奨される修正手順
echo "🔧 8. 推奨される修正手順:"
echo ""
echo "   問題が判明した場合:"
echo "   1. アプリケーションのレスポンスが遅い場合:"
echo "      - アプリケーションのログを確認"
echo "      - データベース接続や外部APIの応答を確認"
echo ""
echo "   2. Nginx Proxy Managerの設定問題の場合:"
echo "      - Custom Nginx configurationを確認"
echo "      - Forward Hostname/IPとForward Portが正しいことを確認"
echo ""
echo "   3. ネットワーク問題の場合:"
echo "      - ファイアウォール設定を確認"
echo "      - ポートが正しく開放されていることを確認"
echo ""

echo "🎉 調査完了！"









