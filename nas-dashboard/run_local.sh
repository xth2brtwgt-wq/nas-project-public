#!/bin/bash
# nas-dashboard ローカル起動スクリプト

set -e

echo "🚀 nas-dashboard ローカル起動スクリプト"
echo "=========================================="

# カレントディレクトリを確認
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 仮想環境の確認
if [ ! -d "venv" ]; then
    echo "📦 仮想環境を作成中..."
    python3 -m venv venv
fi

# 仮想環境をアクティベート
echo "🔧 仮想環境をアクティベート中..."
source venv/bin/activate

# 依存関係のインストール
echo "📥 依存関係をインストール中..."
pip install --upgrade pip
pip install -r requirements.txt

# ローカル用データディレクトリの作成
echo "📁 ローカル用データディレクトリを作成中..."
mkdir -p data
mkdir -p logs

# 認証データベースの初期化（初回のみ）
if [ ! -f data/auth.db ]; then
    echo "🔐 認証データベースを初期化中..."
    python3 -c "
from utils.auth_db import init_auth_db
init_auth_db()
print('✅ 認証データベースを初期化しました')
"
    
    # 初期ユーザーを作成
    echo "👤 初期ユーザーを作成中..."
    python3 -c "
from utils.auth_db import create_user
if create_user('admin', 'admin123'):
    print('✅ 初期ユーザー「admin」を作成しました')
else:
    print('⚠️  初期ユーザーの作成に失敗しました（既に存在する可能性があります）')
"
else
    echo "✅ 認証データベースは既に存在します"
fi

# 環境変数の設定
export NAS_MODE=false
export FLASK_ENV=development
export SECRET_KEY=local-secret-key-2025
export LOG_DIR=./logs
export TZ=Asia/Tokyo

# .env.localファイルがある場合は読み込む
if [ -f .env.local ]; then
    echo "📄 .env.localファイルを読み込み中..."
    export $(cat .env.local | grep -v '^#' | xargs)
fi

# アプリケーションの起動
echo ""
echo "✅ 準備完了！"
echo "🌐 ブラウザで http://localhost:9000 にアクセスしてください"
echo "📝 デフォルトユーザー: admin / admin123"
echo ""
echo "🛑 停止するには Ctrl+C を押してください"
echo ""

python3 app.py

