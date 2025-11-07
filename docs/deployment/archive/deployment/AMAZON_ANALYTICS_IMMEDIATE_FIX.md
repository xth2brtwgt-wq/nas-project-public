# 🔧 amazon-analytics 静的ファイル404エラー 即座の修正手順

**作成日**: 2025-11-02  
**目的**: amazon-analyticsの静的ファイル404エラーを即座に修正

---

## ⚠️ 問題

- `https://yoshi-nas-sys.duckdns.org:8443/analytics/static/css/style.css` - 404エラー
- `https://yoshi-nas-sys.duckdns.org:8443/analytics/static/js/app.js` - 404エラー

---

## ✅ 即座の修正手順

### ステップ1: Nginx Proxy Managerの設定を確認・再保存

1. **Nginx Proxy ManagerのWeb UI**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

4. **「Custom Nginx Configuration」を確認**

5. **以下が含まれているか確認**（含まれていない場合は追加）:

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

**重要**: これらの設定は、`/monitoring`や`/meetings`の設定より**前に**記述してください。

6. **「Save」をクリック**

7. **Proxy Hostのステータスが「Online」のままであることを確認**

### ステップ2: Nginx設定の再読み込み

```bash
# Nginx設定の構文チェック
docker exec nginx-proxy-manager nginx -t

# Nginx設定の再読み込み
docker exec nginx-proxy-manager nginx -s reload
```

### ステップ3: amazon-analyticsの環境変数を確認・設定

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# amazon-analyticsのディレクトリに移動
cd ~/nas-project/amazon-analytics

# .envファイルを確認
cat .env | grep SUBFOLDER_PATH

# SUBFOLDER_PATHが設定されていない場合は追加
if ! grep -q "SUBFOLDER_PATH" .env; then
    echo "SUBFOLDER_PATH=/analytics" >> .env
fi

# コンテナを再起動
docker compose down
docker compose up -d

# ログを確認
docker compose logs backend | tail -50
```

### ステップ4: amazon-analyticsのコードが最新か確認

```bash
# NAS環境で確認（まだSSH接続している場合）
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

### ステップ5: 直接アクセステスト

```bash
# Nginx経由でアクセス
curl -I https://yoshi-nas-sys.duckdns.org:8443/analytics/static/css/style.css

# アプリケーションに直接アクセス
curl -I http://192.168.68.110:8001/static/css/style.css
```

**期待される結果**: 
- Nginx経由: HTTP 200 OK
- 直接アクセス: HTTP 200 OK

### ステップ6: ブラウザのキャッシュをクリア

1. **ブラウザの開発者ツールを開く**（F12キー）
2. **「Network」タブを開く**
3. **「Disable cache」にチェックを入れる**
4. **ページをリロード**（`Cmd+Shift+R`または`Ctrl+Shift+R`）

---

## 🔍 確認手順

### 1. Nginx設定ファイルの確認

```bash
# Nginx設定ファイルを確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 5 -A 10 "analytics/static"
```

**期待される結果**: `location ^~ /analytics/static/`の設定が含まれている

### 2. amazon-analyticsの環境変数の確認

```bash
# NAS環境で確認
ssh -p 23456 AdminUser@192.168.68.110

cd ~/nas-project/amazon-analytics

# 環境変数を確認
docker compose exec backend env | grep SUBFOLDER_PATH
```

**期待される結果**: `SUBFOLDER_PATH=/analytics`

### 3. amazon-analyticsのアプリケーションログの確認

```bash
# NAS環境で確認
cd ~/nas-project/amazon-analytics

# アプリケーションのログを確認
docker compose logs backend | tail -100 | grep -i "static\|subfolder\|root_path"
```

---

## 📝 チェックリスト

- [ ] Nginx Proxy ManagerのAdvancedタブに`/analytics/static/`の設定が含まれているか確認
- [ ] Nginx Proxy Managerの設定を保存
- [ ] Proxy Hostのステータスが「Online」のままであることを確認
- [ ] Nginx設定の構文チェック（`nginx -t`）
- [ ] Nginx設定の再読み込み（`nginx -s reload`）
- [ ] amazon-analyticsの`.env`ファイルに`SUBFOLDER_PATH=/analytics`が設定されているか確認
- [ ] amazon-analyticsのコンテナを再起動
- [ ] amazon-analyticsのコードが最新か確認（`git pull`）
- [ ] amazon-analyticsのコンテナを再ビルド・再起動
- [ ] `curl`で直接アクセスして確認（200 OKか）
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
echo "SUBFOLDER_PATH=/analytics" >> .env
docker compose down
docker compose up -d
```

### 問題3: コードが最新でない

**原因**: NAS環境のコードが最新でない

**解決方法**:
```bash
git pull origin feature/monitoring-fail2ban-integration
docker compose down
docker compose build
docker compose up -d
```

### 問題4: ブラウザのキャッシュ

**原因**: ブラウザが古い静的ファイルをキャッシュしている

**解決方法**:
1. ブラウザの開発者ツールを開く（F12キー）
2. 「Network」タブを開く
3. 「Disable cache」にチェックを入れる
4. ページをリロード（`Cmd+Shift+R`または`Ctrl+Shift+R`）

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

