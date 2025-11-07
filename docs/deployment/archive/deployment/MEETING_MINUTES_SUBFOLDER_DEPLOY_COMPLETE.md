# ✅ meeting-minutes-byc - サブフォルダ対応完了

**作成日**: 2025-11-02  
**目的**: meeting-minutes-bycのサブフォルダ対応が完了したことを記録

---

## ✅ 完了した作業

### 1. アプリケーション側の修正

#### `app.py`の修正
- `static_url_path`を`/static`に戻した（物理パスは`static/`フォルダ）
- `APPLICATION_ROOT`を設定（`SUBFOLDER_PATH`が設定されている場合）
- テンプレートに`subfolder_path`を渡すように修正

#### `templates/index.html`の修正
- 静的ファイルのURLに`subfolder_path`を手動で追加
- JavaScriptに`window.SUBFOLDER_PATH`を設定

#### `static/js/app.js`の修正
- Socket.IOのパスに`subfolder_path`を追加
- APIエンドポイントのパスに`subfolder_path`を追加（`apiPath`ヘルパーメソッドを追加）

### 2. Nginx Proxy Managerの設定

#### Advancedタブの設定
```nginx
# /meetings の静的ファイル修正（^~ を使用して正規表現マッチを無効化）
location ^~ /meetings/static/ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /meetings のSocket.IO修正
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

# /meetings のAPI修正
location ~ ^/meetings/api/(.*)$ {
    rewrite ^/meetings/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

**重要**: 
- `location ^~ /meetings/static/`を使用することで、`location /meetings`より優先されます
- `auth_basic off;`を設定することで、静的ファイル、Socket.IO、APIエンドポイントへのBasic認証を除外します

### 3. 環境変数の設定

NAS環境の`.env`ファイルに以下を追加：

```bash
SUBFOLDER_PATH=/meetings
```

---

## ✅ 動作確認結果

### 静的ファイル
- ✅ `style.css`: 200 OKで正常に読み込まれる
- ✅ `app.js`: 200 OKで正常に読み込まれる
- ✅ CSSが正しく適用されている

### Socket.IO
- ✅ WebSocket接続が正常に確立される
- ✅ `/meetings/socket.io/`でアクセスできる
- ✅ エラーが出ていない

### APIエンドポイント
- ✅ `/meetings/api/templates`: 200 OKで正常に動作する
- ✅ `/meetings/api/dictionary`: 200 OKで正常に動作する
- ✅ その他のAPIエンドポイントも正常に動作する

---

## 📝 今後の注意事項

### 内部ネットワークからのアクセス

内部ネットワークから直接アクセスする場合（`http://192.168.68.110:5002`）は、`SUBFOLDER_PATH`を設定しないでください。

```bash
# 内部ネットワークからのアクセスの場合
# SUBFOLDER_PATHは空欄のまま（またはコメントアウト）
# SUBFOLDER_PATH=
```

### 外部ネットワークからのアクセス

外部ネットワークからNginx Proxy Manager経由でアクセスする場合（`https://yoshi-nas-sys.duckdns.org:8443/meetings`）は、`SUBFOLDER_PATH`を設定してください。

```bash
# 外部ネットワークからのアクセスの場合
SUBFOLDER_PATH=/meetings
```

---

## 📚 参考資料

- [Flask APPLICATION_ROOT](https://flask.palletsprojects.com/en/latest/config/#APPLICATION_ROOT)
- [Flask-SocketIO path](https://flask-socketio.readthedocs.io/en/latest/api.html#flask_socketio.SocketIO)
- [Nginx location優先順位](https://nginx.org/en/docs/http/ngx_http_core_module.html#location)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


