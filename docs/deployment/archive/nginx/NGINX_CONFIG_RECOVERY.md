# 🔧 Nginx Proxy Manager 設定復旧ガイド

**作成日**: 2025-01-27  
**対象**: 設定ファイルが削除された場合の復旧方法

---

## 📋 概要

Nginx Proxy Managerの設定ファイルが削除された場合の復旧方法を説明します。

---

## 🔍 確認結果

### ログの分析

```
[11/7/2025] [11:10:41 AM] [Nginx    ] › ⬤  debug     Deleting file: /data/nginx/proxy_host/6.conf
[11/7/2025] [11:10:41 AM] [Global   ] › ⬤  debug     CMD: /usr/sbin/nginx -t -g "error_log off;"
[11/7/2025] [11:10:41 AM] [Nginx    ] › ℹ  info      Reloading Nginx
```

**確認結果**:
- ✅ Nginx Proxy Managerのコンテナは正常に稼働中（Up 4 days）
- ✅ Nginxの設定ファイルの構文は正常
- ⚠️ 設定ファイル（`/data/nginx/proxy_host/6.conf`）が削除されている可能性

---

## 🔧 復旧手順

### ステップ1: 現在の設定ファイルの状態を確認

```bash
# NAS環境で実行
ssh -p 23456 AdminUser@192.168.68.110

# 設定ファイルが存在するか確認
docker exec nginx-proxy-manager ls -la /data/nginx/proxy_host/

# 設定ファイルの内容を確認（存在する場合）
docker exec nginx-proxy-manager cat /data/nginx/proxy_host/6.conf
```

### ステップ2: Nginx Proxy ManagerのWeb UIで設定を確認

1. **内部ネットワークからNginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hosts → yoshi-nas-sys.duckdns.org を確認**
   - 設定が正しく保存されているか確認
   - Custom Nginx Configurationの設定を確認

3. **設定が失われている場合**
   - 設定を再入力
   - 「Save」をクリック

### ステップ3: 設定を再適用

**推奨設定**（`docs/deployment/NGINX_FINAL_CONFIG.md` を参照）:

1. **Proxy Hosts → yoshi-nas-sys.duckdns.org → Advanced → Custom Nginx Configuration**

2. **以下の設定をコピー&ペースト**:

```nginx
# ==========================================
# 重複ヘッダーの削除
# ==========================================
# バックエンドから送信されるDateヘッダーを削除（Nginxが自動的に設定するため）
proxy_hide_header Date;

# ==========================================
# 静的ファイル・API・WebSocket設定
# 順序が重要：より具体的なパスを先に記述
# ==========================================

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

# /monitoring の静的ファイル修正（nas-dashboard-monitoring - Reactアプリ）
location ^~ /monitoring/static/ {
    rewrite ^/monitoring/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:3002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /monitoring のmanifest.json修正（nas-dashboard-monitoring）
location = /monitoring/manifest.json {
    rewrite ^/monitoring/manifest.json$ /manifest.json break;
    proxy_pass http://192.168.68.110:3002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /monitoring のAPI修正（nas-dashboard-monitoring - バックエンドに直接転送）
location ~ ^/monitoring/api/(.*)$ {
    rewrite ^/monitoring/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /monitoring のWebSocket修正（nas-dashboard-monitoring - バックエンドに直接転送）
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

# /meetings の静的ファイル修正（meeting-minutes-byc）
location ^~ /meetings/static/ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /meetings のSocket.IO修正（meeting-minutes-byc）
location ~ ^/meetings/socket.io/(.*)$ {
    rewrite ^/meetings/socket.io/(.*)$ /socket.io/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    auth_basic off;
}

# /meetings のAPI修正（meeting-minutes-byc）
location ~ ^/meetings/api/(.*)$ {
    rewrite ^/meetings/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /documents の静的ファイル修正（document-automation）
location ^~ /documents/static/ {
    rewrite ^/documents/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /documents のAPI修正（document-automation）
location ~ ^/documents/api/(.*)$ {
    rewrite ^/documents/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /documents のstatusエンドポイント修正（document-automation）
location ~ ^/documents/status$ {
    rewrite ^/documents/status$ /status break;
    proxy_pass http://192.168.68.110:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /youtube の静的ファイル修正（youtube-to-notion）
location ^~ /youtube/static/ {
    rewrite ^/youtube/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8111;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /youtube のSocket.IO修正（youtube-to-notion）
location ~ ^/youtube/socket.io/(.*)$ {
    rewrite ^/youtube/socket.io/(.*)$ /socket.io/$1 break;
    proxy_pass http://192.168.68.110:8111;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    auth_basic off;
}

# /youtube のAPI修正（youtube-to-notion）
location ~ ^/youtube/api/(.*)$ {
    rewrite ^/youtube/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8111;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# ==========================================
# タイムアウト設定（ファイルアップロード・長時間処理用）
# ==========================================

# ファイルアップロードサイズ制限（500MB）
client_max_body_size 500M;

# タイムアウト設定（長時間処理対応）
proxy_connect_timeout 600s;
proxy_send_timeout 600s;
proxy_read_timeout 600s;

# バッファ設定（大きなファイルアップロード用）
proxy_request_buffering off;
proxy_buffering off;

# バッファサイズ設定
proxy_buffer_size 128k;
proxy_buffers 4 256k;
proxy_busy_buffers_size 256k;
```

3. **「Save」をクリック**

4. **アクセスできるか確認**

---

## 🔍 追加確認項目

### 設定ファイルの状態確認

```bash
# 設定ファイルが存在するか確認
docker exec nginx-proxy-manager ls -la /data/nginx/proxy_host/

# 設定ファイルの内容を確認（存在する場合）
docker exec nginx-proxy-manager cat /data/nginx/proxy_host/6.conf

# Nginxの設定ファイルの構文を確認
docker exec nginx-proxy-manager nginx -t
```

### Nginx Proxy Managerの再起動（必要に応じて）

```bash
# Nginx Proxy Managerのコンテナを再起動
docker restart nginx-proxy-manager

# 再起動後のログを確認
docker logs nginx-proxy-manager --tail 50
```

---

## 📚 参考資料

- **Nginx Proxy Manager最終設定**: `docs/deployment/NGINX_FINAL_CONFIG.md`
- **Nginx Proxy Managerアクセスエラーのトラブルシューティング**: `docs/deployment/NGINX_ACCESS_ERROR_TROUBLESHOOTING.md`
- **重複ヘッダー警告の修正ガイド**: `docs/deployment/DUPLICATE_HEADER_FIX_GUIDE.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

