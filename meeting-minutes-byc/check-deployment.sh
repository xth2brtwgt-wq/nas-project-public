#!/bin/bash

# デプロイメント確認スクリプト
# 使用方法: ./check-deployment.sh

echo "🔍 デプロイメント状況を確認中..."

# 1. コンテナの状態確認
echo "📊 コンテナの状態:"
docker compose ps

# 2. 参加者フィールドの確認
echo "🔍 参加者フィールドの確認:"
if docker exec meeting-minutes-byc cat /app/templates/index.html | grep -q "participants"; then
    echo "✅ 参加者フィールドが正常に表示されています"
else
    echo "❌ 参加者フィールドが見つかりません"
    echo "🔄 デプロイスクリプトを実行してください: ./deploy.sh"
    exit 1
fi

# 3. バージョン確認
echo "📋 アプリケーションバージョン:"
docker exec meeting-minutes-byc cat /app/config/version.py | grep APP_VERSION

# 4. ヘルスチェック
echo "🏥 ヘルスチェック:"
if docker exec meeting-minutes-byc curl -f http://localhost:5000/health >/dev/null 2>&1; then
    echo "✅ アプリケーションが正常に動作しています"
else
    echo "❌ アプリケーションに問題があります"
fi

echo "🎉 確認完了！"

