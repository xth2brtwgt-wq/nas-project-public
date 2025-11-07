# Gunicorn アップデート手順

**meeting-minutes-byc を gunicorn に移行しました！**

---

## 🎯 変更内容

### 1. requirements.txt
```diff
+ gevent==24.2.1
+ gevent-websocket==0.10.1
```

### 2. docker-compose.yml
```yaml
command: gunicorn --worker-class gevent --workers 2 --bind 0.0.0.0:5000 --timeout 300 --log-level info app:app
```

---

## 🚀 NASで適用する手順

### Step 1: 最新版を取得

```bash
cd ~/nas-project
git pull origin main
```

### Step 2: コンテナを再ビルド＆再起動

```bash
cd ~/nas-project/meeting-minutes-byc

# 停止
docker compose down

# 再ビルド＆起動
docker compose up -d --build
```

### Step 3: 確認

```bash
# ログを確認（gunicornのログが表示されるはず）
docker compose logs --tail=50

# 動作確認
curl http://localhost:5002/health
```

---

## ✅ 期待されるログ

```
[2025-10-21 12:00:00 +0900] [1] [INFO] Starting gunicorn 23.0.0
[2025-10-21 12:00:00 +0900] [1] [INFO] Listening at: http://0.0.0.0:5000 (1)
[2025-10-21 12:00:00 +0900] [1] [INFO] Using worker: gevent
[2025-10-21 12:00:00 +0900] [8] [INFO] Booting worker with pid: 8
[2025-10-21 12:00:00 +0900] [9] [INFO] Booting worker with pid: 9
```

**Werkzeug の警告が消えています！** ✨

---

## 📊 改善点

### Before (Werkzeug)
```
⚠️ WARNING: This is a development server.
⚠️ Do not use it in a production deployment.
```

### After (Gunicorn)
```
✅ Production-ready WSGI server
✅ Multiple workers for better performance
✅ Async/WebSocket support with gevent
✅ No warnings
```

---

## 🎉 完了！

gunicorn で本番環境に適した構成になりました！

