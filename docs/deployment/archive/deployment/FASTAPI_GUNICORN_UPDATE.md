# FastAPI Projects - Gunicorn + Uvicorn 移行完了

**amazon-analytics と document-automation を gunicorn + uvicorn workers に移行しました！**

---

## 🎯 変更内容

### 対象プロジェクト
1. **amazon-analytics**
2. **document-automation**

---

## 📝 変更詳細

### 1. requirements.txt
```diff
fastapi==0.115.0
uvicorn[standard]==0.31.0
+ gunicorn==23.0.0
python-multipart==0.0.12
```

### 2. Dockerfile / Dockerfile.web

#### Before:
```dockerfile
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### After:
```dockerfile
CMD ["gunicorn", "app.api.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--log-level", "info"]
```

---

## ⚙️ 設定パラメータ

| パラメータ | 値 | 説明 |
|-----------|-----|------|
| `--workers` | 4 | ワーカー数（CPUコア数に応じて調整可能） |
| `--worker-class` | uvicorn.workers.UvicornWorker | FastAPI/ASGI用ワーカー |
| `--bind` | 0.0.0.0:8000 / 8080 | バインドアドレス |
| `--timeout` | 120 | タイムアウト（秒） |
| `--log-level` | info | ログレベル |

---

## 🚀 NASで適用する手順

### amazon-analytics の更新

```bash
# 1. 最新版を取得
cd ~/nas-project
git pull origin main

# 2. プロジェクトに移動
cd amazon-analytics

# 3. .env.restore を作成（初回のみ）
cp .env .env.restore
nano .env.restore
# GEMINI_API_KEY と POSTGRES_PASSWORD を設定

# 4. データフォルダ作成（初回のみ）
mkdir -p data/{uploads,processed,exports,cache,db}

# 5. 再ビルド＆起動
docker compose down
docker compose up -d --build

# 6. ログ確認
docker compose logs web --tail=50
```

**期待されるログ:**
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:8000 (1)
[INFO] Using worker: uvicorn.workers.UvicornWorker
[INFO] Booting worker with pid: 8
[INFO] Booting worker with pid: 9
[INFO] Booting worker with pid: 10
[INFO] Booting worker with pid: 11
```

### document-automation の更新

```bash
# 1. プロジェクトに移動
cd ~/nas-project/document-automation

# 2. .env.restore を作成（初回のみ）
cp .env .env.restore
nano .env.restore
# GOOGLE_CLOUD_VISION_API_KEY または GEMINI_API_KEY を設定

# 3. データフォルダ作成（初回のみ）
sudo mkdir -p /volume2/data/doc-automation/{uploads,processed,exports,cache,db}
sudo chown -R 1000:1000 /volume2/data/doc-automation

# 4. 再ビルド＆起動
docker compose down
docker compose up -d --build

# 5. ログ確認
docker compose logs web --tail=50
```

**期待されるログ:**
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:8080 (1)
[INFO] Using worker: uvicorn.workers.UvicornWorker
[INFO] Booting worker with pid: 8
[INFO] Booting worker with pid: 9
[INFO] Booting worker with pid: 10
[INFO] Booting worker with pid: 11
```

---

## ✅ 動作確認

### amazon-analytics

```bash
# ヘルスチェック
curl http://localhost:8000/health

# ブラウザでアクセス
# http://[NASのIP]:8000
```

### document-automation

```bash
# ヘルスチェック
curl http://localhost:8080/health

# ブラウザでアクセス
# http://[NASのIP]:8080
```

---

## 📊 全プロジェクト統一完了

| プロジェクト | サーバー | 構成 | ステータス |
|-------------|---------|------|-----------|
| **meeting-minutes-byc** | gunicorn + gevent | 2 workers | ✅ 完了 |
| **amazon-analytics** | gunicorn + uvicorn | 4 workers | ✅ 完了 |
| **document-automation** | gunicorn + uvicorn | 4 workers | ✅ 完了 |
| **insta360-auto-sync** | スクリプト | N/A | - |

---

## ✨ メリット

### 安定性
- ✅ プロセス管理が堅牢
- ✅ ワーカーのクラッシュ時に自動再起動
- ✅ Graceful restart 対応

### パフォーマンス
- ✅ 複数ワーカーで並行処理
- ✅ 長時間実行タスクにも対応（120秒タイムアウト）
- ✅ 非同期処理の最適化

### 統一性
- ✅ 全プロジェクトで gunicorn 使用
- ✅ 一貫したログ形式
- ✅ 統一された管理方法

---

## 🎉 完了！

すべてのWebアプリケーションが本番環境向けに最適化されました！

