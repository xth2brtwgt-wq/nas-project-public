# NASデプロイメント - 問題の修正

## 🔧 問題と解決策

---

## 1. amazon-analytics: .env ファイルが存在しない

### 問題
```bash
cp: cannot stat '.env': No such file or directory
```

### 解決策

NASで以下を実行:

```bash
cd ~/nas-project/amazon-analytics

# env.exampleから.env.localを作成
cp env.example .env.local

# 編集
nano .env.local
```

**以下の値を設定:**

```env
# AI Provider
AI_PROVIDER=gemini

# Gemini API (必須)
GEMINI_API_KEY=AIzaSyDS_gER_ei9mfkNoGG63P2VODorlayD9dM

# Database
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@db:5432/amazon_analytics
```

保存後:

```bash
# 起動
docker compose up -d --build

# ログ確認
docker compose logs web --tail=50

# 動作確認
curl http://localhost:8000/health
```

---

## 2. document-automation: ヘルスチェック失敗

### 問題
```bash
curl: (56) Recv failure: Connection reset by peer
```

### 原因
アプリケーションがまだ起動中の可能性があります。

### 解決策

```bash
cd ~/nas-project/document-automation

# ログを確認
docker compose logs web --tail=100

# 30秒待ってから再度テスト
sleep 30
curl http://localhost:8080/health

# それでも失敗する場合、詳細ログを確認
docker compose logs web -f
```

### 確認ポイント

1. **Gunicorn が起動しているか:**
   ```
   [INFO] Starting gunicorn 23.0.0
   [INFO] Booting worker with pid: X
   ```

2. **エラーメッセージがないか:**
   ```
   ERROR: ...
   ```

3. **コンテナのステータス:**
   ```bash
   docker compose ps
   ```

---

## 3. 完全リセット（必要な場合）

### amazon-analytics

```bash
cd ~/nas-project/amazon-analytics

# 完全停止
docker compose down -v

# 再起動
docker compose up -d --build

# ログ確認
docker compose logs -f
```

### document-automation

```bash
cd ~/nas-project/document-automation

# 完全停止
docker compose down -v

# データフォルダの権限確認
sudo chown -R 1000:1000 /volume2/data/doc-automation

# 再起動
docker compose up -d --build

# ログ確認
docker compose logs -f
```

---

## 📋 チェックリスト

### amazon-analytics
- [ ] .env.local ファイル作成済み
- [ ] GEMINI_API_KEY 設定済み
- [ ] POSTGRES_PASSWORD 設定済み
- [ ] docker compose up -d --build 実行済み
- [ ] ログにエラーがない
- [ ] curl http://localhost:8000/health が成功

### document-automation
- [ ] .env.local ファイル作成済み
- [ ] APIキー設定済み（Vision or Gemini）
- [ ] データフォルダの権限設定済み
- [ ] docker compose up -d --build 実行済み
- [ ] ログにエラーがない
- [ ] curl http://localhost:8080/health が成功

---

## 🎯 期待される成功ログ

### amazon-analytics
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Using worker: uvicorn.workers.UvicornWorker
[INFO] Booting worker with pid: 8
[INFO] Booting worker with pid: 9
[INFO] Booting worker with pid: 10
[INFO] Booting worker with pid: 11
```

### document-automation
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:8080
[INFO] Using worker: uvicorn.workers.UvicornWorker
[INFO] Booting worker with pid: 8
[INFO] Booting worker with pid: 9
[INFO] Booting worker with pid: 10
[INFO] Booting worker with pid: 11
```

---

## 💡 よくある問題

### ポートが使用中
```bash
# ポート確認
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :8080

# 既存のコンテナを停止
docker compose down
```

### データベース接続エラー
```bash
# データベースのステータス確認
docker compose ps

# データベースログ確認
docker compose logs db

# データベースのヘルスチェック
docker compose exec db pg_isready -U postgres
```

### パーミッションエラー
```bash
# データフォルダの権限を修正
sudo chown -R 1000:1000 /volume2/data/doc-automation
sudo chmod -R 755 /volume2/data/doc-automation
```

