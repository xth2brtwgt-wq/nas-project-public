# 🔧 amazon-analytics 静的ファイル404エラー トラブルシューティング

**作成日**: 2025-11-02  
**目的**: amazon-analyticsの静的ファイル404エラーを解決

---

## ⚠️ 問題

- `https://yoshi-nas-sys.duckdns.org:8443/analytics/static/css/style.css` - 404エラー
- `https://yoshi-nas-sys.duckdns.org:8443/analytics/static/js/app.js` - 404エラー

---

## 🔍 原因の確認

### 1. Nginx Proxy Managerの設定が反映されているか確認

```bash
# Nginx設定ファイルを確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -A 10 "analytics/static"
```

**期待される結果**: `location ^~ /analytics/static/`の設定が含まれている

### 2. Nginx Proxy Managerの設定を直接確認

1. **Nginx Proxy ManagerのWeb UI**: `http://192.168.68.110:8181`
2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**
3. **「Advanced」タブをクリック**
4. **「Custom Nginx Configuration」に以下が含まれているか確認**:

```nginx
# /analytics の静的ファイル修正（amazon-analytics）
location ^~ /analytics/static/ {
    rewrite ^/analytics/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

### 3. 直接アクセステスト

```bash
# Nginx経由でアクセスして静的ファイルを確認
curl -I https://yoshi-nas-sys.duckdns.org:8443/analytics/static/css/style.css
```

**期待される結果**: HTTP 200 OK（404ではない）

### 4. amazon-analyticsのアプリケーション側の確認

#### NAS環境で確認

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# amazon-analyticsのコンテナに接続
cd ~/nas-project/amazon-analytics
docker compose exec backend bash

# 環境変数を確認
echo $SUBFOLDER_PATH

# アプリケーションのログを確認
docker compose logs backend | tail -50
```

**期待される結果**: `SUBFOLDER_PATH=/analytics`が設定されている

---

## ✅ 解決方法

### 方法1: Nginx Proxy Managerの設定を確認・再保存

1. **Nginx Proxy ManagerのWeb UI**: `http://192.168.68.110:8181`
2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**
3. **「Advanced」タブをクリック**
4. **「Custom Nginx Configuration」を確認**
5. **`/analytics/static/`の設定が含まれているか確認**
6. **含まれていない場合は、以下を追加**:

```nginx
# /analytics の静的ファイル修正（amazon-analytics）
location ^~ /analytics/static/ {
    rewrite ^/analytics/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /analytics のAPI修正（amazon-analytics）
location ~ ^/analytics/api/(.*)$ {
    rewrite ^/analytics/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

7. **「Save」をクリック**
8. **Proxy Hostのステータスが「Online」のままであることを確認**

### 方法2: amazon-analyticsの環境変数を確認・設定

#### NAS環境で確認

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# amazon-analyticsのディレクトリに移動
cd ~/nas-project/amazon-analytics

# .envファイルを確認
cat .env | grep SUBFOLDER_PATH

# SUBFOLDER_PATHが設定されていない場合は追加
echo "SUBFOLDER_PATH=/analytics" >> .env

# コンテナを再起動
docker compose down
docker compose up -d

# ログを確認
docker compose logs backend | tail -50
```

### 方法3: amazon-analyticsのコードが最新か確認

#### NAS環境で確認

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# amazon-analyticsのディレクトリに移動
cd ~/nas-project/amazon-analytics

# 最新のコードを取得
git pull origin feature/monitoring-fail2ban-integration

# コンテナを再ビルド・再起動
docker compose down
docker compose build
docker compose up -d

# ログを確認
docker compose logs backend | tail -50
```

---

## 🔍 詳細な確認手順

### ステップ1: Nginx設定の確認

```bash
# Nginx設定ファイルを確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 5 -A 10 "analytics/static"

# Nginx設定の構文チェック
docker exec nginx-proxy-manager nginx -t

# Nginx設定の再読み込み
docker exec nginx-proxy-manager nginx -s reload
```

### ステップ2: 直接アクセステスト

```bash
# Nginx経由でアクセス
curl -I https://yoshi-nas-sys.duckdns.org:8443/analytics/static/css/style.css

# アプリケーションに直接アクセス
curl -I http://192.168.68.110:8001/static/css/style.css
```

### ステップ3: アプリケーションのログ確認

```bash
# NAS環境で確認
ssh -p 23456 AdminUser@192.168.68.110

cd ~/nas-project/amazon-analytics

# コンテナのログを確認
docker compose logs backend | tail -100

# 環境変数を確認
docker compose exec backend env | grep SUBFOLDER_PATH
```

---

## 📝 チェックリスト

- [ ] Nginx Proxy ManagerのAdvancedタブに`/analytics/static/`の設定が含まれているか確認
- [ ] Nginx設定ファイルを確認（`location ^~ /analytics/static/`が含まれているか）
- [ ] Nginx設定の構文チェック（`nginx -t`）
- [ ] Nginx設定の再読み込み（`nginx -s reload`）
- [ ] `curl`で直接アクセスして確認（200 OKか）
- [ ] amazon-analyticsの`.env`ファイルに`SUBFOLDER_PATH=/analytics`が設定されているか確認
- [ ] amazon-analyticsのコンテナが再起動されているか確認
- [ ] amazon-analyticsのコードが最新か確認（`git pull`）
- [ ] amazon-analyticsのコンテナを再ビルド・再起動
- [ ] ブラウザのキャッシュをクリア
- [ ] `/analytics`でアクセスして静的ファイルが正しく読み込まれることを確認

---

## ⚠️ よくある問題

### 問題1: Nginx設定が反映されていない

**原因**: Nginx Proxy Managerの設定を保存したが、Nginx設定が再読み込みされていない

**解決方法**:
```bash
docker exec nginx-proxy-manager nginx -s reload
```

### 問題2: SUBFOLDER_PATH環境変数が設定されていない

**原因**: amazon-analyticsの`.env`ファイルに`SUBFOLDER_PATH=/analytics`が設定されていない

**解決方法**:
```bash
# .envファイルに追加
echo "SUBFOLDER_PATH=/analytics" >> .env

# コンテナを再起動
docker compose down
docker compose up -d
```

### 問題3: コードが最新でない

**原因**: NAS環境のコードが最新でない

**解決方法**:
```bash
# 最新のコードを取得
git pull origin feature/monitoring-fail2ban-integration

# コンテナを再ビルド・再起動
docker compose down
docker compose build
docker compose up -d
```

### 問題4: ブラウザのキャッシュ

**原因**: ブラウザが古い静的ファイルをキャッシュしている

**解決方法**:
1. **ブラウザの開発者ツールを開く**（F12キー）
2. **「Network」タブを開く**
3. **「Disable cache」にチェックを入れる**
4. **ページをリロード**（`Cmd+Shift+R`または`Ctrl+Shift+R`）

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

