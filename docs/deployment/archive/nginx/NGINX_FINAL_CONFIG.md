# 📝 Nginx Proxy Manager 最終設定

**作成日**: 2025-01-27  
**対象**: yoshi-nas-sys.duckdns.org の Custom Nginx Configuration

---

## 📋 概要

既存の設定に重複ヘッダー警告の修正、各サービスのルートパスへのlocationブロック、セキュリティヘッダーを追加した最終設定です。

**重要**: 
- Custom locationsの設定を削除した場合、この設定に各サービスのルートパスへのlocationブロックが含まれています。
- セキュリティヘッダーを追加していますが、レート制限（`limit_req_zone`）は`server`コンテキストで使用できないため、含まれていません。

---

## 📝 完全なNginx設定

```nginx
# ==========================================
# IPアドレスブロックリスト（ブラックリスト）
# ==========================================
# 不正アクセスを検出したIPアドレスをブロック
# 2025-11-07: 51.159.103.26 (フランス・Scaleway) - 404エラー21回を検出
deny 51.159.103.26;

# ==========================================
# セキュリティヘッダー設定
# ==========================================
# グローバルに適用（すべてのlocationブロックの前に記述）

# HSTS（HTTP Strict Transport Security）
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# XSS保護
add_header X-XSS-Protection "1; mode=block" always;

# クリックジャッキング対策
add_header X-Frame-Options "SAMEORIGIN" always;

# MIMEタイプスニッフィング対策
add_header X-Content-Type-Options "nosniff" always;

# リファラーポリシー
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Content Security Policy（CDNを許可）
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.socket.io; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' data: https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; connect-src 'self' wss: ws: http: https:; form-action 'self'; frame-ancestors 'self';" always;

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
# ルートパス設定（各サービスの基本ルーティング）
# 順序が重要：より具体的なパスの後に記述
# ==========================================

# /analytics のルートパス（amazon-analytics）
location /analytics {
    proxy_pass http://192.168.68.110:8001/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /monitoring のルートパス（nas-dashboard-monitoring - Reactアプリ）
location /monitoring {
    proxy_pass http://192.168.68.110:3002/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /meetings のルートパス（meeting-minutes-byc）
location /meetings {
    proxy_pass http://192.168.68.110:5002/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /documents のルートパス（document-automation）
location /documents {
    proxy_pass http://192.168.68.110:8080/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /youtube のルートパス（youtube-to-notion）
location /youtube {
    proxy_pass http://192.168.68.110:8111/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# ==========================================
# タイムアウト設定（ファイルアップロード・長時間処理用・接続タイムアウト対策）
# ==========================================

# ファイルアップロードサイズ制限（500MB）
client_max_body_size 500M;

# プロキシタイムアウト設定（長時間処理対応）
proxy_connect_timeout 600s;
proxy_send_timeout 600s;
proxy_read_timeout 600s;

# クライアント接続タイムアウト設定（接続タイムアウト対策）
client_body_timeout 300s;
client_header_timeout 300s;

# キープアライブタイムアウト（接続を維持する時間を延長）
keepalive_timeout 300s;

# バッファ設定（大きなファイルアップロード用）
proxy_request_buffering off;
proxy_buffering off;

# バッファサイズ設定
proxy_buffer_size 128k;
proxy_buffers 4 256k;
proxy_busy_buffers_size 256k;
```

---

## 🔍 変更点

### 追加した設定

#### 1. セキュリティヘッダー設定

**位置**: 設定の最上部（すべてのlocationブロックの前）

```nginx
# ==========================================
# セキュリティヘッダー設定
# ==========================================

# HSTS（HTTP Strict Transport Security）
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# XSS保護
add_header X-XSS-Protection "1; mode=block" always;

# クリックジャッキング対策
add_header X-Frame-Options "SAMEORIGIN" always;

# MIMEタイプスニッフィング対策
add_header X-Content-Type-Options "nosniff" always;

# リファラーポリシー
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Content Security Policy（CDNを許可）
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.socket.io; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' data: https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; connect-src 'self' wss: ws: http: https:; form-action 'self'; frame-ancestors 'self';" always;
```

**注意**: 
- レート制限（`limit_req_zone`）は`server`コンテキストで使用できないため、含まれていません
- レート制限が必要な場合は、Fail2banやアプリケーションレベルで実装してください

#### 2. 重複ヘッダーの削除

**位置**: セキュリティヘッダー設定の後、locationブロックの前

```nginx
# ==========================================
# 重複ヘッダーの削除
# ==========================================
# バックエンドから送信されるDateヘッダーを削除（Nginxが自動的に設定するため）
proxy_hide_header Date;
```

#### 3. ルートパスへのlocationブロック

**位置**: 詳細なlocationブロック（静的ファイル、API、WebSocket）の後、タイムアウト設定の前

```nginx
# ==========================================
# ルートパス設定（各サービスの基本ルーティング）
# ==========================================

# /analytics のルートパス（amazon-analytics）
location /analytics {
    proxy_pass http://192.168.68.110:8001/;
    # ... その他の設定 ...
}

# /monitoring のルートパス（nas-dashboard-monitoring）
location /monitoring {
    proxy_pass http://192.168.68.110:3002/;
    # ... その他の設定 ...
}

# /meetings のルートパス（meeting-minutes-byc）
location /meetings {
    proxy_pass http://192.168.68.110:5002/;
    # ... その他の設定 ...
}

# /documents のルートパス（document-automation）
location /documents {
    proxy_pass http://192.168.68.110:8080/;
    # ... その他の設定 ...
}

# /youtube のルートパス（youtube-to-notion）
location /youtube {
    proxy_pass http://192.168.68.110:8111/;
    # ... その他の設定 ...
}
```

**注意**: 
- これらのlocationブロックは、より具体的なlocationブロック（/analytics/static/, /analytics/api/など）の後に配置されています。Nginxは、より具体的なパスを先に処理するためです。
- `proxy_pass`の後にスラッシュ（`/`）を追加することで、Nginxが自動的にパスをリライトします。`rewrite`を使う必要はありません。
- 例: `/analytics` → `http://192.168.68.110:8001/`
- 例: `/analytics/page` → `http://192.168.68.110:8001/page`

---

## 🚀 設定手順

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hosts → yoshi-nas-sys.duckdns.org → Advanced → Custom Nginx Configuration**

3. **上記の完全な設定をコピー&ペースト**

4. **「Save」をクリック**

5. **設定が正しく適用されたか確認**
   ```bash
   docker logs nginx-proxy-manager --tail 50 | grep -i "duplicate header"
   ```

---

## 📚 参考資料

- **セキュリティヘッダー設定（レート制限なし）**: `docs/deployment/NGINX_SECURITY_HEADERS_WITHOUT_RATE_LIMIT.md`
- **重複ヘッダー警告の修正ガイド**: `docs/deployment/DUPLICATE_HEADER_FIX_GUIDE.md`
- **重複ヘッダー警告の修正 - 設定位置ガイド**: `docs/deployment/DUPLICATE_HEADER_FIX_POSITION.md`
- **セキュリティ対策設定状況の確認結果**: `docs/deployment/SECURITY_STATUS_VERIFICATION.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

