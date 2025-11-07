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

# コンテナを常時起動させる（cronジョブから実行されるため、スケジューラーは無効化）
# cronジョブが同期処理を実行するため、コンテナは待機状態で起動
CMD ["tail", "-f", "/dev/null"]