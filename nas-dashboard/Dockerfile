FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージを更新
RUN apt-get update && apt-get install -y \
    docker.io \
    openssh-client \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# ポートを公開
EXPOSE 9000

# アプリケーションを起動
CMD ["gunicorn", "--bind", "0.0.0.0:9000", "--workers", "2", "--timeout", "600", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
