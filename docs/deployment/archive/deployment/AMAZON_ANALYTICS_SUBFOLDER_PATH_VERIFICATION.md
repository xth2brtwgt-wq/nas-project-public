# 🔍 amazon-analytics SUBFOLDER_PATH 確認手順

**作成日**: 2025-11-02  
**目的**: amazon-analyticsの`SUBFOLDER_PATH`環境変数が正しく読み込まれているか確認

---

## ✅ 確認結果

### 1. 環境変数の確認

```bash
cat .env | grep SUBFOLDER_PATH
# 結果: SUBFOLDER_PATH=/analytics
```
✓ **正しく設定されています**

### 2. コンテナの状態確認

```bash
docker compose ps
```

**結果**:
- `amazon-analytics-db`: Up 4 minutes (healthy) ✓
- `amazon-analytics-redis`: Up 4 minutes (healthy) ✓
- `amazon-analytics-web`: Up 4 minutes ✓

**すべて正常に起動しています**

---

## 🔍 追加の確認手順

### ステップ1: コンテナ内の環境変数を確認

```bash
# amazon-analyticsのディレクトリに移動
cd ~/nas-project/amazon-analytics

# コンテナ内の環境変数を確認
docker compose exec web env | grep SUBFOLDER_PATH
```

**期待される結果**: `SUBFOLDER_PATH=/analytics`

### ステップ2: アプリケーションのログを確認

```bash
# アプリケーションのログを確認
docker compose logs web | tail -50

# root_pathが設定されているか確認
docker compose logs web | grep -i "root_path\|subfolder\|SUBFOLDER"
```

**期待される結果**: 
- `root_path=/analytics`がログに表示される
- または、`SUBFOLDER_PATH=/analytics`がログに表示される

### ステップ3: アプリケーションの起動確認

```bash
# アプリケーションのヘルスチェック
curl http://192.168.68.110:8001/api/health

# 静的ファイルへの直接アクセス
curl -I http://192.168.68.110:8001/static/css/style.css
```

**期待される結果**: 
- `/api/health`: HTTP 200 OK
- `/static/css/style.css`: HTTP 200 OK

### ステップ4: Nginx Proxy Manager経由でのアクセステスト

```bash
# Nginx経由でアクセス
curl -I https://yoshi-nas-sys.duckdns.org:8443/analytics/static/css/style.css
```

**期待される結果**: HTTP 200 OK（404ではない）

---

## 🔧 問題が続く場合の対処法

### 問題1: コンテナ内の環境変数が設定されていない

**原因**: `.env`ファイルがDocker Composeで正しく読み込まれていない

**解決方法**:
```bash
# .envファイルを確認
cat .env

# コンテナを再起動
docker compose down
docker compose up -d

# コンテナ内の環境変数を再確認
docker compose exec web env | grep SUBFOLDER_PATH
```

### 問題2: アプリケーションが環境変数を読み込んでいない

**原因**: アプリケーションのコードが最新でない

**解決方法**:
```bash
# 最新のコードを取得
git pull origin feature/monitoring-fail2ban-integration

# コンテナを再ビルド・再起動
docker compose down
docker compose build
docker compose up -d

# ログを確認
docker compose logs web | tail -50
```

### 問題3: Nginx Proxy Managerの設定が反映されていない

**原因**: Nginx設定が再読み込みされていない

**解決方法**:
```bash
# Nginx設定の構文チェック
docker exec nginx-proxy-manager nginx -t

# Nginx設定の再読み込み
docker exec nginx-proxy-manager nginx -s reload

# Nginx設定ファイルを確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 5 -A 10 "analytics/static"
```

---

## 📝 チェックリスト

- [ ] `.env`ファイルに`SUBFOLDER_PATH=/analytics`が設定されている
- [ ] コンテナが正常に起動している
- [ ] コンテナ内の環境変数が正しく設定されている（`docker compose exec web env | grep SUBFOLDER_PATH`）
- [ ] アプリケーションのログに`root_path`または`SUBFOLDER_PATH`が表示されている
- [ ] アプリケーションに直接アクセスできる（`curl http://192.168.68.110:8001/api/health`）
- [ ] 静的ファイルに直接アクセスできる（`curl -I http://192.168.68.110:8001/static/css/style.css`）
- [ ] Nginx Proxy Managerの設定が正しく保存されている
- [ ] Nginx設定が再読み込みされている（`nginx -s reload`）
- [ ] Nginx経由で静的ファイルにアクセスできる（`curl -I https://yoshi-nas-sys.duckdns.org:8443/analytics/static/css/style.css`）
- [ ] ブラウザのキャッシュをクリア
- [ ] `/analytics`でアクセスして静的ファイルが正しく読み込まれることを確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

