FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージを更新・インストール
RUN apt-get update && apt-get install -y \
    cifs-utils \
    rsync \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# ログディレクトリを作成
RUN mkdir -p logs

# スケジューラーモードで起動（毎日00:00に自動実行）
CMD ["python", "scripts/sync.py"]