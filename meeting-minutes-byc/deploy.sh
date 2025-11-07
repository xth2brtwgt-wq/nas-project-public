#!/bin/bash

# meeting-minutes-byc デプロイスクリプト
# 使用方法: ./deploy.sh

echo "🚀 meeting-minutes-byc デプロイを開始します..."

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

# 1.5. .envファイルの復元・確認（git pull後に復元）
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
    fi
fi

# 2. マウント先ディレクトリの確認・作成
echo "📁 マウント先ディレクトリを確認中..."
mkdir -p ~/nas-project-data/meeting-minutes/templates
mkdir -p ~/nas-project-data/meeting-minutes/uploads
mkdir -p ~/nas-project-data/meeting-minutes/transcripts

# 3. 最新ファイルをマウント先にコピー
echo "📋 最新ファイルをマウント先にコピー中..."
cp -r templates/* ~/nas-project-data/meeting-minutes/templates/
cp -r static/* ~/nas-project-data/meeting-minutes/static/ 2>/dev/null || true

# 4. Dockerコンテナを停止・削除
echo "🛑 Dockerコンテナを停止中..."
docker compose down -v

# 5. Dockerイメージを削除
echo "🗑️ 古いDockerイメージを削除中..."
docker image rm meeting-minutes-byc:latest 2>/dev/null || true

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
sleep 5
docker compose ps

# 10. 参加者フィールドの確認
echo "🔍 参加者フィールドの確認中..."
if docker exec meeting-minutes-byc cat /app/templates/index.html | grep -q "participants"; then
    echo "✅ 参加者フィールドが正常に表示されています"
else
    echo "❌ 参加者フィールドが見つかりません"
    exit 1
fi

echo "🎉 デプロイが完了しました！"
echo "🌐 アプリケーション: http://localhost:5002"

