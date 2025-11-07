# 🔧 Nginx Proxy Manager - amazon-analytics / nas-dashboard-monitoring 静的ファイル修正

**作成日**: 2025-11-02  
**目的**: amazon-analyticsとnas-dashboard-monitoringの静的ファイル404エラーを解決

---

## ⚠️ 問題

- `https://yoshi-nas-sys.duckdns.org:8443/analytics` - 静的ファイルが404エラー
- `https://yoshi-nas-sys.duckdns.org:8443/monitoring` - 静的ファイルが404エラー

---

## ✅ 解決方法

### Nginx Proxy ManagerのAdvancedタブでリライト設定を追加

1. **Nginx Proxy ManagerのWeb UIにアクセス**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

4. **「Custom Nginx Configuration」に以下を追加**:

```nginx
# /analytics の静的ファイル修正
location ^~ /analytics/static/ {
    rewrite ^/analytics/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /analytics のAPI修正
location ~ ^/analytics/api/(.*)$ {
    rewrite ^/analytics/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /monitoring の静的ファイル修正（Reactアプリの静的ファイル）
location ^~ /monitoring/static/ {
    rewrite ^/monitoring/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:3002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /monitoring のmanifest.json修正
location = /monitoring/manifest.json {
    rewrite ^/monitoring/manifest.json$ /manifest.json break;
    proxy_pass http://192.168.68.110:3002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /monitoring のAPI修正（バックエンドに直接転送）
location ~ ^/monitoring/api/(.*)$ {
    rewrite ^/monitoring/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /monitoring のWebSocket修正（バックエンドに直接転送）
location ~ ^/monitoring/ws(.*)$ {
    rewrite ^/monitoring/ws(.*)$ /ws$1 break;
    proxy_pass http://192.168.68.110:8002;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

**重要**: これらの設定は、既存の`/meetings`の設定より**前に**記述してください（より具体的なパスを先に処理）。

5. **「Save」をクリック**

6. **Proxy Hostのステータスが「Online」のままであることを確認**

---

## 🔍 設定の説明

### amazon-analytics (`/analytics`)

- **静的ファイル**: `/analytics/static/...` → `/static/...`にリライト
- **API**: `/analytics/api/...` → `/api/...`にリライト

### nas-dashboard-monitoring (`/monitoring`)

- **静的ファイル**: `/monitoring/static/...` → `/static/...`にリライト（フロントエンドのnginx経由）
- **manifest.json**: `/monitoring/manifest.json` → `/manifest.json`にリライト
- **API**: `/monitoring/api/...` → `/api/...`にリライト（バックエンドに直接アクセス）

---

## 🧪 動作確認

### amazon-analytics

1. **`https://yoshi-nas-sys.duckdns.org:8443/analytics`にアクセス**
2. **ブラウザの開発者ツール → Networkタブ**:
   - `style.css`のステータス: **200 OK**
   - `app.js`のステータス: **200 OK**
   - APIリクエスト: **200 OK**

### nas-dashboard-monitoring

1. **`https://yoshi-nas-sys.duckdns.org:8443/monitoring`にアクセス**
2. **ブラウザの開発者ツール → Networkタブ**:
   - `main.*.css`のステータス: **200 OK**
   - `main.*.js`のステータス: **200 OK**
   - `manifest.json`のステータス: **200 OK**
   - APIリクエスト: **200 OK**

---

## 📝 チェックリスト

- [ ] Advancedタブに静的ファイルのリライト設定を追加
- [ ] AdvancedタブにAPIのリライト設定を追加
- [ ] Proxy Hostのステータスが「Online」のままであることを確認
- [ ] `/analytics`でアクセスして静的ファイルが正しく読み込まれることを確認
- [ ] `/monitoring`でアクセスして静的ファイルが正しく読み込まれることを確認
- [ ] 404エラーが出ていないことを確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

