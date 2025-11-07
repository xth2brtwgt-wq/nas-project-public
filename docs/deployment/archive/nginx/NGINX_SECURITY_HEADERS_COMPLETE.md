# 🔒 Nginx Proxy Manager - セキュリティヘッダー完全設定ガイド

**作成日**: 2025-01-27  
**対象**: Nginx Proxy Managerで複数のサービスをサブパスで運用している環境

---

## 📋 概要

既存のNginx設定（静的ファイル・API・WebSocket設定）に、セキュリティヘッダーを追加する方法を説明します。

---

## 🚀 設定手順

### ステップ1: Nginx Proxy ManagerのWeb UIにアクセス

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブを開く**

3. **yoshi-nas-sys.duckdns.orgのProxy Hostを編集**

4. **「Advanced」タブを開く**

5. **Custom Nginx Configurationに以下を追加**（既存の設定の先頭に追加）

---

## 📝 完全なNginx設定

```nginx
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

# Content Security Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: ws:;" always;

# レート制限
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req zone=general burst=20 nodelay;

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

---

## 🔍 セキュリティヘッダーの説明

### 1. Strict-Transport-Security (HSTS)
- **効果**: HTTPS接続を強制し、中間者攻撃を防止
- **設定**: 2年間（63072000秒）有効

### 2. X-XSS-Protection
- **効果**: XSS（クロスサイトスクリプティング）攻撃を防止
- **設定**: ブラウザのXSS保護を有効化

### 3. X-Frame-Options
- **効果**: クリックジャッキング攻撃を防止
- **設定**: 同一オリジンからのみフレーム表示を許可

### 4. X-Content-Type-Options
- **効果**: MIMEタイプスニッフィングを防止
- **設定**: コンテンツタイプの推測を無効化

### 5. Referrer-Policy
- **効果**: リファラー情報の漏洩を防止
- **設定**: 同一オリジンまたはHTTPS接続時のみリファラーを送信

### 6. Content-Security-Policy
- **効果**: XSS攻撃やデータインジェクション攻撃を防止
- **設定**: スクリプト、スタイル、画像、フォント、接続のソースを制限

### 7. レート制限
- **効果**: DoS攻撃やブルートフォース攻撃を軽減
- **設定**: 1秒あたり10リクエスト、バースト20リクエストまで許可

---

## ✅ 設定後の確認

### 1. セキュリティヘッダーの確認

```bash
# 外部からHTTPSでアクセスしてヘッダーを確認
curl -I https://yoshi-nas-sys.duckdns.org:8443/

# セキュリティヘッダーが含まれていることを確認
# 以下のヘッダーが表示されることを確認：
# - Strict-Transport-Security
# - X-Frame-Options
# - X-Content-Type-Options
# - X-XSS-Protection
# - Referrer-Policy
# - Content-Security-Policy
```

### 2. 動作確認

各サービスにアクセスして、正常に動作することを確認：

- `https://yoshi-nas-sys.duckdns.org:8443/analytics/`
- `https://yoshi-nas-sys.duckdns.org:8443/monitoring/`
- `https://yoshi-nas-sys.duckdns.org:8443/meetings/`
- `https://yoshi-nas-sys.duckdns.org:8443/documents/`
- `https://yoshi-nas-sys.duckdns.org:8443/youtube/`

---

## 📚 参考資料

- **セキュリティ対策設定完了レポート**: `docs/deployment/SECURITY_SETTINGS_COMPLETE.md`
- **外部アクセス時のセキュリティ対策ガイド**: `docs/deployment/EXTERNAL_ACCESS_SECURITY.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

