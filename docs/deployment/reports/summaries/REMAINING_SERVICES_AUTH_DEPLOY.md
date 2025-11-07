# ✅ 残りサービスの認証機能デプロイと確認

**作成日**: 2025-11-04  
**目的**: `amazon-analytics`、`document-automation`、`nas-dashboard-monitoring`の認証機能をデプロイして確認

---

## 📋 デプロイ対象サービス

1. ✅ `amazon-analytics` (FastAPI) - ポート: 8001
2. ✅ `document-automation` (FastAPI) - ポート: 8080
3. ✅ `nas-dashboard-monitoring` (FastAPI) - ポート: 8002 (バックエンド), 3002 (フロントエンド)

---

## 🔧 デプロイ手順（各サービス共通）

### ステップ1: 最新のコードをプル

```bash
cd ~/nas-project/<サービス名>
git pull origin feature/monitoring-fail2ban-integration
```

### ステップ2: コンテナを完全停止

```bash
sudo docker compose down
```

### ステップ3: Dockerイメージを再ビルド（必要に応じて）

```bash
# 認証機能の実装が含まれている場合のみ
sudo docker compose build --no-cache
```

### ステップ4: コンテナを起動

```bash
sudo docker compose up -d
```

### ステップ5: 起動ログを確認

```bash
# 認証関連のログを確認
sudo docker compose logs <サービス名> | grep -i "認証\|auth\|AUTH"

# 起動ログ全体を確認（最新50行）
sudo docker compose logs <サービス名> --tail 50
```

**期待されるログ**:
```
認証モジュールを読み込みました
```

### ステップ6: 直接アクセスして認証を確認

```bash
# ルートエンドポイントにアクセス
curl -v http://localhost:<ポート>/

# ヘルスチェック（認証不要）
curl http://localhost:<ポート>/health
# または
curl http://localhost:<ポート>/api/health
```

**期待される動作**:
- ルートエンドポイント（`/`）にアクセスすると、HTTP 307が返ってきて、ログインページにリダイレクトされる
- ヘルスチェックエンドポイントは認証不要で正常に応答する

---

## 🚀 サービス別デプロイ手順

### 1. `amazon-analytics` (FastAPI)

```bash
cd ~/nas-project/amazon-analytics

# 最新のコードをプル
git pull origin feature/monitoring-fail2ban-integration

# コンテナを完全停止
sudo docker compose down

# コンテナを起動（必要に応じて再ビルド）
sudo docker compose build --no-cache
sudo docker compose up -d

# 起動ログを確認
sudo docker compose logs web | grep -i "認証\|auth\|AUTH"
sudo docker compose logs web --tail 50

# 直接アクセスして認証を確認
curl -v http://localhost:8001/
curl http://localhost:8001/health
```

**期待される動作**:
- `GET /` → HTTP 307、`Location: http://192.168.68.110:9001/login`
- `GET /health` → HTTP 200、正常に応答

### 2. `document-automation` (FastAPI)

```bash
cd ~/nas-project/document-automation

# 最新のコードをプル
git pull origin feature/monitoring-fail2ban-integration

# コンテナを完全停止
sudo docker compose down

# コンテナを起動（必要に応じて再ビルド）
sudo docker compose build --no-cache
sudo docker compose up -d

# 起動ログを確認
sudo docker compose logs web | grep -i "認証\|auth\|AUTH"
sudo docker compose logs web --tail 50

# 直接アクセスして認証を確認
curl -v http://localhost:8080/
curl http://localhost:8080/status
```

**期待される動作**:
- `GET /` → HTTP 307、`Location: http://192.168.68.110:9001/login`
- `GET /status` → HTTP 200、正常に応答（認証不要）

### 3. `nas-dashboard-monitoring` (FastAPI)

```bash
cd ~/nas-project/nas-dashboard-monitoring

# 最新のコードをプル
git pull origin feature/monitoring-fail2ban-integration

# コンテナを完全停止
sudo docker compose down

# コンテナを起動（必要に応じて再ビルド）
sudo docker compose build --no-cache
sudo docker compose up -d

# 起動ログを確認（バックエンド）
sudo docker compose logs backend | grep -i "認証\|auth\|AUTH"
sudo docker compose logs backend --tail 50

# 直接アクセスして認証を確認（バックエンド）
curl -v http://localhost:8002/
curl http://localhost:8002/api/v1/health
```

**期待される動作**:
- `GET /` → HTTP 307、`Location: http://192.168.68.110:9001/login`
- `GET /api/v1/health` → HTTP 200、正常に応答（認証不要）

---

## 📝 クイックコマンド（一括実行）

### `amazon-analytics`

```bash
cd ~/nas-project/amazon-analytics && \
git pull origin feature/monitoring-fail2ban-integration && \
sudo docker compose down && \
sudo docker compose build --no-cache && \
sudo docker compose up -d && \
echo "=== 起動ログを確認 ===" && \
sudo docker compose logs web | grep -i "認証\|auth\|AUTH" && \
echo "=== 直接アクセスして認証を確認 ===" && \
curl -v http://localhost:8001/
```

### `document-automation`

```bash
cd ~/nas-project/document-automation && \
git pull origin feature/monitoring-fail2ban-integration && \
sudo docker compose down && \
sudo docker compose build --no-cache && \
sudo docker compose up -d && \
echo "=== 起動ログを確認 ===" && \
sudo docker compose logs web | grep -i "認証\|auth\|AUTH" && \
echo "=== 直接アクセスして認証を確認 ===" && \
curl -v http://localhost:8080/
```

### `nas-dashboard-monitoring`

```bash
cd ~/nas-project/nas-dashboard-monitoring && \
git pull origin feature/monitoring-fail2ban-integration && \
sudo docker compose down && \
sudo docker compose build --no-cache && \
sudo docker compose up -d && \
echo "=== 起動ログを確認 ===" && \
sudo docker compose logs backend | grep -i "認証\|auth\|AUTH" && \
echo "=== 直接アクセスして認証を確認 ===" && \
curl -v http://localhost:8002/
```

---

## 🔍 動作確認（ブラウザ）

### 1. 未認証でのアクセス

1. **ダッシュボードにログインしていない状態で**、各サービスに直接アクセス：
   - `http://192.168.68.110:8001/` (amazon-analytics)
   - `http://192.168.68.110:8080/` (document-automation)
   - `http://192.168.68.110:8002/` (nas-dashboard-monitoring)
   - `http://192.168.68.110:3002/` (nas-dashboard-monitoring フロントエンド)

2. **ログインページにリダイレクトされることを確認**

### 2. ログイン後のアクセス

1. **ダッシュボードでログイン** (`http://192.168.68.110:9001/`)

2. **ダッシュボードから各サービスにアクセス**、または直接アクセス：
   - 各サービスの画面が表示されることを確認

### 3. 外部アクセス（Nginx Proxy Manager経由）

1. **未認証でアクセス**:
   - `https://yoshi-nas-sys.duckdns.org:8443/analytics` (amazon-analytics)
   - `https://yoshi-nas-sys.duckdns.org:8443/documents` (document-automation)
   - `https://yoshi-nas-sys.duckdns.org:8443/monitoring` (nas-dashboard-monitoring)

2. **ログインページにリダイレクトされることを確認**

3. **ダッシュボードでログイン後、再度アクセス**:
   - 各サービスの画面が表示されることを確認

---

## 🔧 トラブルシューティング

### 認証モジュールが読み込まれない場合

1. **マウント設定を確認**:
   ```bash
   sudo docker compose exec <サービス名> ls -la /nas-project/nas-dashboard/utils/auth_common.py
   ```

2. **環境変数を確認**:
   ```bash
   sudo docker compose exec <サービス名> env | grep NAS_MODE
   ```

3. **コンテナを完全再ビルド**:
   ```bash
   sudo docker compose down
   sudo docker compose build --no-cache
   sudo docker compose up -d
   ```

### 認証チェックが機能しない場合

1. **ログを確認**:
   ```bash
   sudo docker compose logs <サービス名> | grep -i auth
   ```

2. **Cookieを確認**:
   - ブラウザの開発者ツールでCookieの`session_id`を確認
   - Cookieの`Path`が`/`に設定されているか確認

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

