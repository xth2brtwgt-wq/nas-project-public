#!/bin/bash

# YouTube-to-Notion デプロイスクリプト
# 使用方法: ./deploy.sh

echo "🚀 YouTube-to-Notion デプロイを開始します..."

# 0. .envファイルの保護（git pull前にバックアップ）
echo "🔒 .envファイルを保護中..."
if [ -f .env ]; then
    # .envが存在する場合、.env.restoreにバックアップ
    if [ ! -f .env.restore ] || [ .env -nt .env.restore ]; then
        cp .env .env.restore
        echo "✅ .envを.env.restoreにバックアップしました"
    fi
fi

# 1. 最新コードを取得
echo "📥 最新コードを取得中..."
git pull origin main

# 2. .envファイルの復元・確認（git pull後に復元）
echo "🔧 環境変数ファイルを確認中..."
if [ ! -f .env ]; then
    echo "⚠️  .envファイルが見つかりません"
    if [ -f .env.restore ]; then
        echo "📋 .env.restoreから復元します..."
        cp .env.restore .env
        echo "✅ .envを復元しました"
    elif [ -f env.example ]; then
        echo "📋 env.exampleから作成します..."
        cp env.example .env
        echo "⚠️  .envファイルを編集してAPIキーを設定してください"
    else
        echo "❌ .envファイルが存在しません。手動で作成してください。"
        exit 1
    fi
else
    # .envが存在する場合、.env.restoreが新しければ更新
    if [ -f .env.restore ] && [ .env.restore -nt .env ]; then
        echo "⚠️  .env.restoreが.envより新しいです。復元しますか？"
        echo "   現在の.envは保持されます（手動で復元が必要な場合は cp .env.restore .env を実行）"
    fi
fi

# 3. マウント先ディレクトリの確認・作成
echo "📁 マウント先ディレクトリを確認中..."
mkdir -p ~/nas-project-data/youtube-to-notion/uploads
mkdir -p ~/nas-project-data/youtube-to-notion/outputs
mkdir -p ~/nas-project-data/youtube-to-notion/cache
mkdir -p ~/nas-project-data/youtube-to-notion/logs

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
echo "🌐 アプリケーション: http://YOUR_IP_ADDRESS110:8111"
echo "📊 ダッシュボード: http://YOUR_IP_ADDRESS110:9001"
echo "📁 データディレクトリ: ~/nas-project-data/youtube-to-notion/"