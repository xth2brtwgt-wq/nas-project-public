# 🔧 Nginx Proxy Manager - Advancedタブ 完全設定

**作成日**: 2025-11-02  
**目的**: Nginx Proxy ManagerのAdvancedタブに設定する完全な設定内容

---

## 📋 設定方法

1. **Nginx Proxy ManagerのWeb UIにアクセス**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

4. **「Custom Nginx Configuration」に以下をすべてコピー&ペースト**

---

## 📝 完全な設定内容（コピペ用）

```nginx
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
```

---

## 📋 設定の説明

### 設定の順序

**重要**: より具体的なパス（`^~`や完全一致）を先に記述してください。Nginxは上から順に評価します。

1. **`location ^~`** - 前方一致（最優先、正規表現マッチを無効化）
2. **`location ~`** - 正規表現マッチ
3. **`location =`** - 完全一致（最優先）

### 各サービスの設定

#### amazon-analytics (`/analytics`)
- **静的ファイル**: `/analytics/static/` → `/static/` にリライト
- **API**: `/analytics/api/` → `/api/` にリライト
- **転送先**: `http://192.168.68.110:8001`

#### nas-dashboard-monitoring (`/monitoring`)
- **静的ファイル**: `/monitoring/static/` → `/static/` にリライト（フロントエンド）
- **manifest.json**: `/monitoring/manifest.json` → `/manifest.json` にリライト
- **API**: `/monitoring/api/` → `/api/` にリライト（バックエンドに直接転送）
- **WebSocket**: `/monitoring/ws` → `/ws` にリライト（バックエンドに直接転送）
- **転送先（静的）**: `http://192.168.68.110:3002`（フロントエンド）
- **転送先（API/WebSocket）**: `http://192.168.68.110:8002`（バックエンド）

#### meeting-minutes-byc (`/meetings`)
- **静的ファイル**: `/meetings/static/` → `/static/` にリライト
- **Socket.IO**: `/meetings/socket.io/` → `/socket.io/` にリライト
- **API**: `/meetings/api/` → `/api/` にリライト
- **転送先**: `http://192.168.68.110:5002`

#### document-automation (`/documents`)
- **静的ファイル**: `/documents/static/` → `/static/` にリライト
- **API**: `/documents/api/` → `/api/` にリライト
- **転送先**: `http://192.168.68.110:8080`

#### youtube-to-notion (`/youtube`)
- **静的ファイル**: `/youtube/static/` → `/static/` にリライト
- **Socket.IO**: `/youtube/socket.io/` → `/socket.io/` にリライト
- **API**: `/youtube/api/` → `/api/` にリライト
- **転送先**: `http://192.168.68.110:8111`

---

## ✅ 設定後の確認

### ステップ1: 設定を保存

1. **「Save」をクリック**
2. **Proxy Hostのステータスが「Online」のままであることを確認**
3. **「Offline」になった場合は、設定に構文エラーがある可能性があります**

### ステップ2: Nginx設定の確認

```bash
# Nginx設定の構文チェック
docker exec nginx-proxy-manager nginx -t

# Nginx設定の再読み込み
docker exec nginx-proxy-manager nginx -s reload
```

### ステップ3: 動作確認

#### amazon-analytics
1. **`https://yoshi-nas-sys.duckdns.org:8443/analytics`にアクセス**
2. **ブラウザの開発者ツール → Networkタブ**:
   - `style.css`のステータス: **200 OK**
   - `app.js`のステータス: **200 OK**
   - APIリクエスト: **200 OK**

#### nas-dashboard-monitoring
1. **`https://yoshi-nas-sys.duckdns.org:8443/monitoring`にアクセス**
2. **ブラウザの開発者ツール → Networkタブ**:
   - `main.*.css`のステータス: **200 OK**
   - `main.*.js`のステータス: **200 OK**
   - `manifest.json`のステータス: **200 OK**
   - APIリクエスト: **200 OK**（404エラーが出ていないか）
   - WebSocket接続: **正常に確立される**

#### meeting-minutes-byc
1. **`https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセス**
2. **ブラウザの開発者ツール → Networkタブ**:
   - `style.css`のステータス: **200 OK**
   - `app.js`のステータス: **200 OK**
   - Socket.IO接続: **正常に確立される**
   - APIリクエスト: **200 OK**

#### document-automation
1. **`https://yoshi-nas-sys.duckdns.org:8443/documents`にアクセス**
2. **ブラウザの開発者ツール → Networkタブ**:
   - `style.css`のステータス: **200 OK**
   - `app.js`のステータス: **200 OK**
   - APIリクエスト: **200 OK**
   - `/status`エンドポイント: **200 OK**

#### youtube-to-notion
1. **`https://yoshi-nas-sys.duckdns.org:8443/youtube`にアクセス**
2. **ブラウザの開発者ツール → Networkタブ**:
   - `favicon.svg`のステータス: **200 OK**
   - Socket.IO接続: **正常に確立される**
   - APIリクエスト: **200 OK**

---

## 📝 チェックリスト

- [ ] Advancedタブに上記の設定をすべてコピー&ペースト
- [ ] 「Save」をクリック
- [ ] Proxy Hostのステータスが「Online」のままであることを確認
- [ ] Nginx設定の構文チェック（`nginx -t`）
- [ ] Nginx設定の再読み込み（`nginx -s reload`）
- [ ] `/analytics`で静的ファイルが正しく読み込まれることを確認
- [ ] `/monitoring`で静的ファイルが正しく読み込まれることを確認
- [ ] `/monitoring`でAPIリクエストが正常に動作することを確認
- [ ] `/monitoring`でWebSocket接続が正常に確立されることを確認
- [ ] `/meetings`で静的ファイルが正しく読み込まれることを確認
- [ ] `/meetings`でSocket.IO接続が正常に確立されることを確認
- [ ] `/meetings`でAPIリクエストが正常に動作することを確認
- [ ] `/documents`で静的ファイルが正しく読み込まれることを確認
- [ ] `/documents`でAPIリクエストが正常に動作することを確認
- [ ] `/documents`で`/status`エンドポイントが正常に動作することを確認
- [ ] `/youtube`で静的ファイルが正しく読み込まれることを確認
- [ ] `/youtube`でSocket.IO接続が正常に確立されることを確認
- [ ] `/youtube`でAPIリクエストが正常に動作することを確認

---

## ⚠️ 注意事項

### 設定の順序

- **`location ^~`** を使用する設定は、**`location ~`** を使用する設定より**前に**記述してください
- より具体的なパス（`/meetings/static/`など）を先に記述することで、正しくマッチします

### auth_basic off

- 静的ファイル、API、WebSocket、Socket.IOには`auth_basic off;`を設定しています
- これにより、Basic認証を回避してアクセスできます

### プロキシパス

- `proxy_pass`の後に`break;`を指定することで、リライト後のパスをそのまま使用します
- `auth_basic off;`により、Basic認証を除外します

---

## 🔍 トラブルシューティング

### Proxy Hostが「Offline」になった場合

1. **設定の構文エラーを確認**
   - セミコロン（`;`）が抜けていないか
   - 波括弧（`{}`）が正しく閉じられているか
   - 引用符が正しく閉じられているか

2. **Nginx設定の構文チェック**
   ```bash
   docker exec nginx-proxy-manager nginx -t
   ```

3. **エラーログを確認**
   ```bash
   docker logs nginx-proxy-manager --tail 100 | grep -i error
   ```

### 404エラーが続く場合

1. **設定が正しく保存されているか確認**
   ```bash
   docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -A 10 "location.*static"
   ```

2. **アクセスログを確認**
   ```bash
   docker exec nginx-proxy-manager tail -f /data/logs/proxy-host-6_access.log | grep -i "static\|api\|ws"
   ```

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

