#!/bin/bash
# NAS環境：全システムのプル＆再ビルドスクリプト
# 使用方法: bash NAS_REBUILD_ALL.sh

set -e  # エラーが発生したら処理を停止

echo "🚀 NAS環境：全システムのプル＆再ビルドを開始します"
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

# nas-dashboard
echo "📊 nas-dashboard を再ビルド中..."
cd ~/nas-project/nas-dashboard
docker compose down
docker compose build --no-cache
docker compose up -d
echo "✅ nas-dashboard の再ビルドが完了しました"
echo ""

# meeting-minutes-byc
echo "🎤 meeting-minutes-byc を再ビルド中..."
cd ~/nas-project/meeting-minutes-byc
docker compose down
docker compose build --no-cache
docker compose up -d
echo "✅ meeting-minutes-byc の再ビルドが完了しました"
echo ""

# youtube-to-notion
echo "📺 youtube-to-notion を再ビルド中..."
cd ~/nas-project/youtube-to-notion
docker compose down
docker compose build --no-cache
docker compose up -d
echo "✅ youtube-to-notion の再ビルドが完了しました"
echo ""

# notion-knowledge-summaries
echo "🧠 notion-knowledge-summaries を再ビルド中..."
cd ~/nas-project/notion-knowledge-summaries
docker compose down
docker compose build --no-cache
docker compose up -d
echo "✅ notion-knowledge-summaries の再ビルドが完了しました"
echo ""

# amazon-analytics
echo "📊 amazon-analytics を再ビルド中..."
cd ~/nas-project/amazon-analytics
docker compose down
docker compose build --no-cache
docker compose up -d
echo "✅ amazon-analytics の再ビルドが完了しました"
echo ""

echo "🎉 全システムの再ビルドが完了しました！"
echo ""
echo "📋 再ビルドしたシステム："
echo "  - nas-dashboard（ログ監視画面のヘッダー変更）"
echo "  - meeting-minutes-byc（ヘッダー統一）"
echo "  - youtube-to-notion（ヘッダー統一）"
echo "  - notion-knowledge-summaries（ヘッダー統一）"
echo "  - amazon-analytics（ヘッダー統一）"
echo ""
echo "⚠️  注意: Insta360自動同期システムはWebアプリケーションではないため、再ビルドの対象外です。"

