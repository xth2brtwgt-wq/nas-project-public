#!/bin/bash

# Meeting Minutes BYC - 開発用実行スクリプト

echo "🚀 Meeting Minutes BYC - 開発環境を起動します..."

# 環境変数ファイルのチェック
if [ ! -f .env ]; then
    echo "⚠️  .envファイルが見つかりません。"
    echo "📝 env_example.txtを参考に.envファイルを作成してください。"
    echo ""
    echo "必要な環境変数:"
    echo "  GEMINI_API_KEY=your_gemini_api_key_here"
    echo ""
    exit 1
fi

# 必要なディレクトリの作成
mkdir -p uploads transcripts

# Python仮想環境の確認
if [ ! -d "venv" ]; then
    echo "📦 Python仮想環境を作成しています..."
    python3 -m venv venv
fi

# 仮想環境のアクティベート
echo "🔧 仮想環境をアクティベートしています..."
source venv/bin/activate

# 依存関係のインストール
echo "📚 依存関係をインストールしています..."
pip install -r requirements.txt

# アプリケーションの起動
echo "🎯 Flaskアプリケーションを起動しています..."
echo "🌐 アクセスURL: http://localhost:5000"
echo "⏹️  停止するには Ctrl+C を押してください"
echo ""

python app.py
