#!/bin/bash

# nas-dashboard デプロイスクリプト
# 使用方法: ./deploy.sh

echo "🚀 NASダッシュボード デプロイを開始します..."

# 1. 最新コードを取得
echo "📥 最新コードを取得中..."
git pull origin main

# 2. マウント先ディレクトリの確認・作成
echo "📁 マウント先ディレクトリを確認中..."
mkdir -p /home/YOUR_USERNAME/nas-dashboard-data/backups
mkdir -p /home/YOUR_USERNAME/nas-dashboard-data/reports
mkdir -p /home/YOUR_USERNAME/nas-dashboard-data/logs
mkdir -p logs

# 3. 最新ファイルをマウント先にコピー
echo "📋 最新ファイルをマウント先にコピー中..."
cp -r templates/* /home/YOUR_USERNAME/nas-dashboard-data/templates/ 2>/dev/null || true

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

# 9.5. スケジューラーの確認
echo "📅 週次レポートスケジューラーの確認中..."
if docker exec nas-dashboard-scheduler ps aux | grep -q "weekly_report_scheduler.py"; then
    echo "✅ 週次レポートスケジューラーが正常に起動しています"
else
    echo "❌ 週次レポートスケジューラーの起動に失敗しました"
    docker logs nas-dashboard-scheduler
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
echo "📧 週次レポート自動送信機能が追加されました"
echo "📅 スケジュール: 毎週月曜日 09:00（固定）"
echo "📧 送信先: nas.system.0828@gmail.com"
