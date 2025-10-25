# YouTube要約システム - Dockerfile
FROM python:3.11-slim

# システムパッケージの更新と必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ディレクトリの作成
RUN mkdir -p /app/data/uploads \
    /app/data/outputs \
    /app/data/cache \
    /app/logs

# ポートの公開
EXPOSE 8110

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8110/health || exit 1

# アプリケーション起動
CMD ["python", "app.py"]
