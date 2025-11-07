#!/bin/bash

# nas-dashboard デプロイスクリプト
# 使用方法: ./deploy.sh

echo "🚀 NASダッシュボード デプロイを開始します..."

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
mkdir -p ~/nas-dashboard-data/backups
mkdir -p ~/nas-dashboard-data/reports
mkdir -p ~/nas-dashboard-data/logs
mkdir -p logs

# 3. 最新ファイルをマウント先にコピー
echo "📋 最新ファイルをマウント先にコピー中..."
cp -r templates/* ~/nas-dashboard-data/templates/ 2>/dev/null || true

# 4. Dockerコンテナを停止・削除
echo "🛑 Dockerコンテナを停止中..."
docker compose down -v

# 5. Dockerイメージを削除
echo "🗑️ 古いDockerイメージを削除中..."
docker image rm nas-dashboard:latest 2>/dev/null || true

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

# 9.5. 月次レポートスケジューラーの確認
echo "📅 月次AI分析レポートスケジューラーの確認中..."
sleep 3
if docker exec nas-dashboard-monthly-scheduler ps aux | grep -q "monthly_ai_report_scheduler.py"; then
    echo "✅ 月次AI分析レポートスケジューラーが正常に起動しています"
else
    echo "⚠️  月次AI分析レポートスケジューラーの確認中..."
    docker logs nas-dashboard-monthly-scheduler | tail -20
fi

# 10. ダッシュボードの確認
echo "🔍 ダッシュボードの確認中..."
if docker exec nas-dashboard cat /app/templates/dashboard.html | grep -q "システム監視"; then
    echo "✅ システム監視セクションが正常に表示されています"
else
    echo "❌ システム監視セクションが見つかりません"
    exit 1
fi

# 11. 重複したシステム情報セクションが削除されているか確認
echo "🔍 重複したシステム情報セクションの削除確認中..."
if docker exec nas-dashboard cat /app/templates/dashboard.html | grep -q "システム情報"; then
    echo "⚠️  システム情報セクションがまだ存在します"
else
    echo "✅ 重複したシステム情報セクションが正常に削除されています"
fi

echo "🎉 デプロイが完了しました！"
echo "🌐 NASダッシュボード: http://localhost:9001"
echo "📊 システム監視機能が統合されました"
echo "📧 月次AI分析レポート自動送信機能が有効です"
echo "📅 スケジュール: 毎月1日 10:00（固定）"
echo "📧 送信先: nas.system.0828@gmail.com"
echo ""
echo "📋 デプロイ後の確認:"
echo "  - docker compose ps でコンテナ起動確認"
echo "  - docker logs nas-dashboard-monthly-scheduler でログ確認"
echo "  - レポートディレクトリ: ~/nas-project-data/nas-dashboard/reports/"
