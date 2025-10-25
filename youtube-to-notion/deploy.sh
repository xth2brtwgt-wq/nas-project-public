#!/bin/bash

# YouTube-to-Notion デプロイスクリプト
# 使用方法: ./deploy.sh

echo "🚀 YouTube-to-Notion デプロイを開始します..."

# 1. 最新コードを取得
echo "📥 最新コードを取得中..."
git pull origin main

# 2. マウント先ディレクトリの確認・作成
echo "📁 マウント先ディレクトリを確認中..."
mkdir -p /home/YOUR_USERNAME/youtube-to-notion-data/uploads
mkdir -p /home/YOUR_USERNAME/youtube-to-notion-data/outputs
mkdir -p /home/YOUR_USERNAME/youtube-to-notion-data/cache
mkdir -p /home/YOUR_USERNAME/youtube-to-notion-data/logs

# 3. 環境変数ファイルの確認
echo "🔧 環境変数ファイルを確認中..."
if [ ! -f .env ]; then
    echo "❌ .envファイルが見つかりません"
    echo "📋 env.exampleをコピーして.envを作成してください"
    cp env.example .env
    echo "⚠️  .envファイルを編集してAPIキーを設定してください"
    exit 1
fi

# 4. Dockerコンテナを停止・削除
echo "🛑 Dockerコンテナを停止中..."
docker compose down -v

# 5. Dockerイメージを削除
echo "🗑️ 古いDockerイメージを削除中..."
docker image rm youtube-to-notion:latest 2>/dev/null || true

# 6. システムクリーンアップ
echo "🧹 システムクリーンアップ中..."
docker system prune -f

# 7. 新しいイメージをビルド
echo "🔨 新しいDockerイメージをビルド中..."
docker compose build --no-cache

# 8. コンテナを起動
echo "🚀 コンテナを起動中..."
docker compose up -d

# 9. 起動確認
echo "✅ 起動確認中..."
sleep 10
docker compose ps

# 10. ヘルスチェック
echo "🔍 ヘルスチェック中..."
for i in {1..30}; do
    if curl -f http://localhost:8110/health >/dev/null 2>&1; then
        echo "✅ アプリケーションが正常に起動しました"
        break
    fi
    echo "⏳ 起動待機中... ($i/30)"
    sleep 2
done

# 11. 最終確認
echo "🎯 最終確認中..."
if docker ps | grep -q "youtube-to-notion"; then
    echo "✅ YouTube-to-Notionコンテナが稼働中です"
else
    echo "❌ YouTube-to-Notionコンテナの起動に失敗しました"
    echo "📋 ログを確認してください:"
    docker compose logs
    exit 1
fi

echo "🎉 デプロイが完了しました！"
echo "🌐 アプリケーション: http://YOUR_NAS_IP:8111"
echo "📊 ダッシュボード: http://YOUR_NAS_IP:9001"
echo "📁 データディレクトリ: /home/YOUR_USERNAME/youtube-to-notion-data/"