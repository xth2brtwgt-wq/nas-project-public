# 🔧 Nginx Proxy Manager - Socket.IOとAPIエンドポイント修正

**作成日**: 2025-11-02  
**目的**: Socket.IOとAPIエンドポイントの404エラーを解決

---

## ⚠️ 現在の問題

- `/socket.io/?EIO=4&transport=polling&t=...` → 404エラー
- `/api/templates` → 404エラー

**原因**: これらのリクエストがルートパス（`/socket.io/`、`/api/templates`）になっているため、`/meetings/socket.io/`や`/meetings/api/templates`にリライトされていません。

---

## ✅ 解決方法

### Nginx Proxy ManagerのAdvancedタブで設定を追加

1. **Nginx Proxy ManagerのWeb UI**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

4. **「Custom Nginx Configuration」を修正**:

```nginx
# /meetings の静的ファイル修正（認証を除外）
location ~ ^/meetings/static/(.*)$ {
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
    # WebSocket設定
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

**重要**: `location`ブロックは**Custom Locationより前に記述**する必要があります。

5. **「Save」をクリック**

6. **Proxy Hostのステータスが「Online」のままであることを確認**

---

## 🔍 アプリケーション側の設定も確認

### Socket.IOのパス設定

アプリケーション側でSocket.IOがルートパスでリッスンしている場合、`/meetings/socket.io/`でアクセスできるように設定する必要があります。

`meeting-minutes-byc/app.py`を確認：

```python
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False, allow_unsafe_werkzeug=True)
```

Socket.IOのパスを設定する場合：

```python
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False, allow_unsafe_werkzeug=True, path='/socket.io')
```

ただし、`APPLICATION_ROOT`を設定している場合、Socket.IOは自動的に`/meetings/socket.io/`でリッスンするはずです。

---

## 🧪 動作確認

### ステップ1: ブラウザのキャッシュをクリア

1. **ブラウザの開発者ツールを開く**（F12キー）
2. **「Network」タブを開く**
3. **「Disable cache」にチェックを入れる**
4. **ページをリロード**（`Cmd+Shift+R`または`Ctrl+Shift+R`）

### ステップ2: アクセステスト

1. **`https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセス**

2. **ブラウザの開発者ツール → Networkタブ**
   - `style.css`のステータス: **200 OK**
   - `app.js`のステータス: **200 OK**
   - `socket.io/?EIO=4&transport=polling&t=...`のステータス: **200 OK**（404ではない）
   - `api/templates`のステータス: **200 OK**（404ではない）

3. **WebSocket接続が正常に確立されるか確認**
   - コンソールに「WebSocket接続エラー」が出ていないか確認

---

## 📝 チェックリスト

- [ ] Nginx Proxy ManagerのAdvancedタブでSocket.IOとAPIのlocationブロックを追加
- [ ] Proxy Hostのステータスが「Online」のままであることを確認
- [ ] Nginx設定の再読み込み
- [ ] ブラウザのキャッシュをクリア
- [ ] `/meetings`でアクセスしてSocket.IOとAPIが正しく動作することを確認
- [ ] 404エラーが出ていないか確認
- [ ] WebSocket接続が正常に確立されるか確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


