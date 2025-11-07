# 🔧 Nginx Proxy Manager - location優先順位の修正

**作成日**: 2025-11-02  
**目的**: locationブロックの優先順位を修正して静的ファイル404エラーを解決

---

## ⚠️ 現在の問題

- `location ~ ^/meetings/static/(.*)$`が設定されているのに、静的ファイルが404エラーになる
- `curl`で直接アクセスすると401エラー（Basic認証）が出る
- アクセスログに静的ファイルへのリクエストが表示されない

**原因**: `location /meetings`（前方一致）が`location ~ ^/meetings/static/(.*)$`（正規表現マッチ）より優先されている可能性があります。

---

## ✅ 解決方法

### Nginx Proxy ManagerのAdvancedタブで設定を修正

`location ~ ^/meetings/static/(.*)$`を`location ^~ /meetings/static/`に変更します。

1. **Nginx Proxy ManagerのWeb UI**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

4. **「Custom Nginx Configuration」を修正**:

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

**重要**: 
- `location ^~ /meetings/static/`を使用することで、正規表現マッチを無効化し、`location /meetings`より優先されます
- `^~`は前方一致で、正規表現マッチを無効化します

5. **「Save」をクリック**

6. **Proxy Hostのステータスが「Online」のままであることを確認**

7. **Nginx設定の再読み込み**:

```bash
docker exec nginx-proxy-manager nginx -t
docker exec nginx-proxy-manager nginx -s reload
```

---

## 🔍 Nginxのlocation優先順位

Nginxのlocation優先順位（高い順）：

1. `=` - 完全一致（最優先）
2. `^~` - 前方一致（正規表現マッチを無効化）
3. `~` / `~*` - 正規表現マッチ
4. 通常のパス（前方一致）

`location ^~ /meetings/static/`を使用することで、`location /meetings`より優先されます。

---

## 🧪 動作確認

### ステップ1: 設定が反映されているか確認

```bash
# Nginx設定ファイルを確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 5 -A 10 "meetings/static"
```

### ステップ2: 直接アクセステスト

```bash
# Nginx経由でアクセスして静的ファイルを確認
curl -I https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css
```

**期待される結果**: HTTP 200 OK（401ではない）

### ステップ3: ブラウザのキャッシュをクリア

1. **ブラウザの開発者ツールを開く**（F12キー）
2. **「Network」タブを開く**
3. **「Disable cache」にチェックを入れる**
4. **ページをリロード**（`Cmd+Shift+R`または`Ctrl+Shift+R`）

### ステップ4: アクセステスト

1. **`https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセス**

2. **ブラウザの開発者ツール → Networkタブ**
   - `style.css`のステータス: **200 OK**（404ではない、401ではない）
   - `app.js`のステータス: **200 OK**（404ではない、401ではない）

3. **CSSが正しく適用されているか確認**
   - レイアウトが崩れていないか確認
   - 色が正しく表示されているか確認

---

## 📝 チェックリスト

- [ ] Advancedタブの設定を修正（`location ^~ /meetings/static/`を使用）
- [ ] Proxy Hostのステータスが「Online」のままであることを確認
- [ ] Nginx設定の再読み込み
- [ ] Nginx設定ファイルを確認（`location ^~ /meetings/static/`が含まれているか）
- [ ] `curl`で直接アクセスして確認（200 OKか）
- [ ] ブラウザのキャッシュをクリア
- [ ] `/meetings`でアクセスしてCSS/JSが正しく読み込まれることを確認
- [ ] 404エラーが出ていないか確認
- [ ] 401エラーが出ていないか確認
- [ ] CSSが正しく適用されているか確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


