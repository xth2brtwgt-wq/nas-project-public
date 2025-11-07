#!/bin/bash
# NAS環境で実行する最終クリーンアップコマンド

set -e

echo "=== NAS環境での最終クリーンアップ ==="
echo ""

# 1. 最新コードを取得
echo "1. 最新コードを取得..."
cd ~/nas-project
git pull origin main
echo "✅ 完了"
echo ""

# 2. nas-dashboardの再デプロイ
echo "2. nas-dashboardの再デプロイ..."
cd ~/nas-project/nas-dashboard

# .envファイルを確認・作成
if [ ! -f .env ]; then
    if [ -f .env.restore ]; then
        cp .env.restore .env
        echo "✅ .env.restoreから.envを作成"
    elif [ -f env.example ]; then
        cp env.example .env
        echo "NAS_MODE=true" >> .env
        echo "✅ env.exampleから.envを作成"
    else
        echo "⚠️  .envファイルが見つかりません。環境変数を確認してください。"
    fi
fi

docker compose down
docker compose up -d --build
sleep 5
docker compose ps
echo "✅ 完了"
echo ""

# 3. 残りのクリーンアップ
echo "3. 残りのクリーンアップ..."
cd ~/nas-project
~/nas-project/scripts/cleanup-all-projects.sh
echo "✅ 完了"
echo ""

# 4. 手動で削除（もし残っている場合）
echo "4. 手動で残りの生成物を削除..."
rm -rf ~/nas-project/nas-dashboard/logs 2>/dev/null || true
rm -rf ~/nas-project/data/reports 2>/dev/null || true
echo "✅ 完了"
echo ""

# 5. amazon-analyticsの起動確認
echo "5. amazon-analyticsの起動確認..."
cd ~/nas-project/amazon-analytics

# .envファイルを確認・作成
if [ ! -f .env ]; then
    if [ -f .env.restore ]; then
        cp .env.restore .env
        echo "✅ .env.restoreから.envを作成"
    elif [ -f env.example ]; then
        cp env.example .env
        echo "NAS_MODE=true" >> .env
        echo "✅ env.exampleから.envを作成"
    else
        echo "⚠️  .envファイルが見つかりません"
    fi
fi

# コンテナを再起動
docker compose down
docker compose up -d --build
sleep 5
docker compose ps
echo "✅ 完了"
echo ""

# 6. document-automationの起動確認
echo "6. document-automationの起動確認..."
cd ~/nas-project/document-automation

# .envファイルを確認・作成
if [ ! -f .env ]; then
    if [ -f .env.restore ]; then
        cp .env.restore .env
        echo "✅ .env.restoreから.envを作成"
    elif [ -f env.example ]; then
        cp env.example .env
        echo "NAS_MODE=true" >> .env
        echo "✅ env.exampleから.envを作成"
    else
        echo "⚠️  .envファイルが見つかりません"
    fi
fi

# コンテナを再起動
docker compose down
docker compose up -d --build
sleep 5
docker compose ps
echo "✅ 完了"
echo ""

# 7. 最終確認
echo "7. 最終確認..."
cd ~/nas-project

echo ""
echo "=== デプロイ確認 ==="
~/nas-project/scripts/verify-deployment.sh

echo ""
echo "=== 容量確認 ==="
~/nas-project/scripts/check-disk-usage.sh

echo ""
echo "=== プロジェクト内の生成物確認 ==="
find ~/nas-project -type d \( -name "logs" -o -name "data" -o -name "uploads" -o -name "cache" \) | grep -v ".git" | grep -v "node_modules" | grep -v "venv" || echo "生成物なし（正常）"

echo ""
echo "=== ログファイルの確認 ==="
ls -lh /home/AdminUser/nas-project-data/*/logs/app.log 2>/dev/null || echo "ログファイルが見つかりません"

echo ""
echo "=== 完了 ==="
echo "すべてのクリーンアップが完了しました。"

