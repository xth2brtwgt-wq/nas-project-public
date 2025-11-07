# ✅ youtube-to-notion サブフォルダ対応完了

**作成日**: 2025-11-04  
**目的**: `youtube-to-notion`のサブフォルダ対応が完了したことを記録

---

## ✅ 完了した作業

### 1. アプリケーション側の修正

#### `app.py`
- ✅ `SUBFOLDER_PATH`環境変数を読み込むように修正
- ✅ `APPLICATION_ROOT`と`SESSION_COOKIE_PATH`を設定
- ✅ 起動時に`SUBFOLDER_PATH`をログ出力するように修正
- ✅ テンプレートに`subfolder_path`を渡すように修正

#### `templates/index.html`
- ✅ 静的ファイルのパスを`subfolder_path`でプレフィックス
- ✅ `window.SUBFOLDER_PATH`をJavaScriptに渡すように修正
- ✅ Socket.IO接続のパスを修正（`path: socketPath`）
- ✅ API呼び出しを`apiPath()`関数でラップ

#### `env.example`
- ✅ `SUBFOLDER_PATH`の例を追加

### 2. Nginx Proxy Manager設定

#### Custom Locationsタブ
- ✅ `/youtube` のCustom Locationを追加
- ✅ Websockets Supportを有効化

#### Advancedタブに追加した設定
- ✅ `/youtube/static/` → `/static/` にリライト（静的ファイル）
- ✅ `/youtube/socket.io/` → `/socket.io/` にリライト（Socket.IO）
- ✅ `/youtube/api/` → `/api/` にリライト（API）
- ✅ `auth_basic off;` を設定（Basic認証を除外）

---

## 📋 設定内容

### 環境変数

`.env`ファイルに以下を追加：

```bash
# Subfolder Support (Optional)
# Nginx Proxy Manager経由でサブフォルダ（/youtube）でアクセスする場合に設定
# 内部ネットワークから直接アクセスする場合は設定不要（空欄のまま）
SUBFOLDER_PATH=/youtube
```

### Nginx Proxy Manager設定

**Proxy Host**: `yoshi-nas-sys.duckdns.org`  
**Custom Locationsタブ**:
- **Location**: `/youtube`
- **Scheme**: `http`
- **Forward Hostname/IP**: `192.168.68.110:8111`
- **Forward Port**: `8111`
- **Websockets Support**: ✅ チェック

**Advancedタブ**に以下を追加：

```nginx
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

## ✅ 動作確認

### 確認項目

1. ✅ 環境変数`SUBFOLDER_PATH=/youtube`が正しく読み込まれている
2. ✅ 起動時に`[INIT] SUBFOLDER_PATH from env: /youtube`がログに表示される
3. ✅ `APPLICATION_ROOT`と`SESSION_COOKIE_PATH`が正しく設定されている
4. ✅ テンプレートで`subfolder_path`が正しく設定されている
5. ✅ Nginx Proxy Managerの設定が正しく反映されている
6. ✅ 静的ファイル（`favicon.svg`）が正常に読み込まれる（404エラーなし）
7. ✅ Socket.IO接続が正常に確立される（404エラーなし）
8. ✅ APIリクエストが正常に動作する（200 OK）

### アクセスURL

- **外部アクセス**: `https://yoshi-nas-sys.duckdns.org:8443/youtube`
- **内部アクセス**: `http://192.168.68.110:8111`

---

## 📝 注意事項

### 内部アクセス時の動作

内部ネットワークから直接アクセス（`http://192.168.68.110:8111`）する場合、環境変数`SUBFOLDER_PATH=/youtube`が設定されているため、静的ファイルのパスが`/youtube/static/...`になります。

これは想定動作です。内部アクセスでも`SUBFOLDER_PATH`を設定しているため、一貫した動作を実現しています。

もし内部アクセス時に`/static/...`を使用したい場合は、`.env`ファイルで`SUBFOLDER_PATH`を空欄にするか、環境変数を削除してください。

---

## 🎯 完了したタスク

- ✅ `youtube-to-notion`のサブフォルダ対応（`/youtube`）
- ✅ 静的ファイルのパス修正
- ✅ Socket.IO接続のパス修正
- ✅ APIエンドポイントのパス修正
- ✅ Nginx Proxy Managerの設定追加
- ✅ 動作確認完了

---

## 📚 参考資料

- [youtube-to-notion サブフォルダ対応デプロイ手順](YOUTUBE_TO_NOTION_SUBFOLDER_DEPLOY.md)
- [全サービスのサブフォルダ対応完了](ALL_SERVICES_SUBFOLDER_COMPLETE.md)
- [Nginx Proxy Manager Advancedタブ完全設定](NGINX_PROXY_MANAGER_ADVANCED_TAB_COMPLETE_CONFIG.md)

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

