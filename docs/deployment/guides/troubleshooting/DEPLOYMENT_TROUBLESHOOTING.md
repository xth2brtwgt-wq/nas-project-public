# 議事録システム デプロイメント トラブルシューティングガイド

## 🚨 よくある問題と解決方法

### 1. 環境変数読み込みエラー

#### 問題の症状
```
ValueError: invalid literal for int() with base 10: ''
WARNING: The "SMTP_PORT" variable is not set. Defaulting to a blank string.
```

#### 原因
`docker-compose.yml`で環境変数を`${VARIABLE_NAME}`形式で参照しているが、`env.production`ファイルが正しく読み込まれていない。

#### 解決方法
`docker-compose.yml`に`env_file`を追加：

```yaml
services:
  meeting-minutes-byc:
    # ... 他の設定 ...
    env_file:
      - env.production
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
      - UPLOAD_DIR=/app/uploads
      - TRANSCRIPT_DIR=/app/transcripts
      - TEMPLATES_DIR=/app/templates
      - HOST=0.0.0.0
      - PORT=5000
      - TZ=Asia/Tokyo
```

**重要**: `env_file`を使用する場合は、`environment`セクションから個別の環境変数を削除する。

### 2. テンプレートファイルが見つからないエラー

#### 問題の症状
```
jinja2.exceptions.TemplateNotFound: index.html
```

#### 原因
Dockerイメージビルド時に`templates`ディレクトリのファイルが正しくコピーされていない。

#### 解決方法
1. **一時的な解決**: 手動でファイルをコピー
```bash
docker cp templates/index.html meeting-minutes-byc:/app/templates/
```

2. **根本的な解決**: Dockerイメージを再ビルド
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### 3. WebSocket接続エラー

#### 問題の症状
```
WebSocket接続エラー: Error: xhr poll error
Failed to load resource: サーバに接続できませんでした。
```

#### 原因
アプリケーションが正常に起動していない（環境変数エラーなど）。

#### 解決方法
1. コンテナの状態を確認
```bash
docker ps | grep meeting-minutes
```

2. ログを確認
```bash
docker logs meeting-minutes-byc --tail=50
```

3. 環境変数エラーを修正後、再起動
```bash
docker compose restart
```

## 📋 デプロイメント前チェックリスト

### 1. 環境変数ファイルの確認
```bash
# env.productionファイルの存在確認
ls -la env.production

# 必須環境変数の確認
grep -E "GEMINI_API_KEY|NOTION_API_KEY|SMTP_PORT" env.production
```

### 2. docker-compose.ymlの確認
```bash
# env_fileの設定確認
grep -A 5 "env_file:" docker-compose.yml
```

### 3. テンプレートファイルの確認
```bash
# templatesディレクトリの確認
ls -la templates/
```

## 🔧 標準的なデプロイメント手順

### 1. 最新コードの取得
```bash
git pull origin main
```

### 2. 環境変数の設定
```bash
# 環境変数ファイルのコピー
cp env.example env.production

# 実際のAPIキーを設定
nano env.production
```

### 3. デプロイメント実行
```bash
# デプロイスクリプトの実行
chmod +x deploy-nas.sh
./deploy-nas.sh
```

### 4. 動作確認
```bash
# コンテナの状態確認
docker ps | grep meeting-minutes

# ログの確認
docker logs meeting-minutes-byc --tail=20

# ヘルスチェック
curl http://localhost:5002/health
```

## 🚀 緊急時の復旧手順

### 1. コンテナの完全リセット
```bash
# コンテナの停止・削除
docker compose down

# イメージの再ビルド
docker compose build --no-cache

# コンテナの起動
docker compose up -d
```

### 2. 環境変数の再設定
```bash
# バックアップからの復元
cp env.production.backup env.production

# または、手動で再設定
nano env.production
```

### 3. ファイルの手動復元
```bash
# テンプレートファイルの復元
docker cp templates/index.html meeting-minutes-byc:/app/templates/

# 静的ファイルの復元
docker cp static/ meeting-minutes-byc:/app/
```

## 📝 ログの確認方法

### 1. リアルタイムログ
```bash
docker logs -f meeting-minutes-byc
```

### 2. エラーログの検索
```bash
docker logs meeting-minutes-byc 2>&1 | grep -i error
```

### 3. 起動ログの確認
```bash
docker logs meeting-minutes-byc --tail=50 | grep -E "(INFO|ERROR|WARNING)"
```

## 🔍 トラブルシューティングの流れ

1. **症状の特定** - エラーメッセージを確認
2. **ログの確認** - `docker logs`で詳細を確認
3. **原因の特定** - 上記のよくある問題と照合
4. **解決方法の実行** - 該当する解決方法を実行
5. **動作確認** - ヘルスチェックとアクセステスト

## ⚠️ 注意事項

- 環境変数ファイルには機密情報が含まれているため、Gitにコミットしない
- デプロイメント前には必ずバックアップを取る
- 本番環境での作業は慎重に行う
- 問題が解決しない場合は、ログを保存してからリセットを検討する

## 📞 サポート

問題が解決しない場合は、以下の情報を収集してください：
- エラーメッセージの全文
- `docker logs meeting-minutes-byc`の出力
- `docker ps`の出力
- `env.production`の内容（機密情報を除く）
