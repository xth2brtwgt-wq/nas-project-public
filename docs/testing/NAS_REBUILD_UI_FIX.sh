#!/bin/bash
# NAS環境：UI統一修正の再ビルドスクリプト
# 使用方法: bash NAS_REBUILD_UI_FIX.sh

set -e  # エラーが発生したら処理を停止

echo "🚀 NAS環境：UI統一修正の再ビルドを開始します"
echo ""

# 1. プロジェクトルートに移動
cd ~/nas-project

# 2. 最新コードを取得
echo "📥 最新コードを取得中..."
git pull origin feature/monitoring-fail2ban-integration
echo "✅ 最新コードを取得しました"
echo ""

# 3. 各システムを再ビルド
echo "🔨 各システムを再ビルド中..."
echo ""

# meeting-minutes-byc
echo "🎤 meeting-minutes-byc を再ビルド中..."
cd ~/nas-project/meeting-minutes-byc
docker compose down
docker compose build --no-cache
docker compose up -d
echo "✅ meeting-minutes-byc の再ビルドが完了しました"
echo ""

# nas-dashboard
echo "📊 nas-dashboard を再ビルド中..."
cd ~/nas-project/nas-dashboard
docker compose down
docker compose build --no-cache
docker compose up -d
echo "✅ nas-dashboard の再ビルドが完了しました"
echo ""

# nas-dashboard-monitoring
echo "🛡️ nas-dashboard-monitoring を再ビルド中..."
cd ~/nas-project/nas-dashboard-monitoring
docker compose down
docker compose build --no-cache
docker compose up -d
echo "✅ nas-dashboard-monitoring の再ビルドが完了しました"
echo ""

echo "🎉 UI統一修正の再ビルドが完了しました！"
echo ""
echo "📋 再ビルドしたシステム："
echo "  - meeting-minutes-byc（タイトル修正）"
echo "  - nas-dashboard（ログイン画面、ログ監視画面の修正）"
echo "  - nas-dashboard-monitoring（統一ヘッダー追加）"

