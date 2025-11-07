# 🔧 静的ファイル404エラー - 再発時の修正

**作成日**: 2025-11-02  
**目的**: 静的ファイル404エラーが再発した場合の修正手順

---

## ⚠️ 現在の問題

- `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css` → 404エラー
- `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/js/app.js` → 404エラー

**原因**: Nginx設定を変更したことで、locationブロックの順序が変わった可能性があります。

---

## ✅ 解決方法

### ステップ1: Nginx設定ファイルを確認

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# Nginx設定ファイルを確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 10 -A 15 "meetings/static"
```

### ステップ2: locationブロックの順序を確認

```bash
# locationブロックの順序を確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 5 -A 10 "location.*meetings"
```

### ステップ3: Advancedタブの設定を確認・修正

1. **Nginx Proxy ManagerのWeb UI**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

4. **「Custom Nginx Configuration」を確認**

以下の設定が**正しい順序で**記述されているか確認してください：

```nginx
# /meetings の静的ファイル修正（Custom Locationより前に記述）
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

**重要**: 
- `location ~ ^/meetings/static/(.*)$` が**最優先**で記述されている必要があります
- `location ~ ^/meetings/socket.io/(.*)$` と `location ~ ^/meetings/api/(.*)$` も**Custom Locationより前に**記述されています
- `location /meetings` は**これらの後に**記述されます

### ステップ4: 設定を保存して確認

1. **「Save」をクリック**

2. **Proxy Hostのステータスが「Online」のままであることを確認**

3. **Nginx設定の再読み込み**:

```bash
docker exec nginx-proxy-manager nginx -t
docker exec nginx-proxy-manager nginx -s reload
```

### ステップ5: ブラウザのキャッシュをクリア

1. **ブラウザの開発者ツールを開く**（F12キー）
2. **「Network」タブを開く**
3. **「Disable cache」にチェックを入れる**
4. **ページをリロード**（`Cmd+Shift+R`または`Ctrl+Shift+R`）

---

## 🐛 トラブルシューティング

### まだ404エラーが出る場合

#### 1. locationの優先順位を確認

`location /meetings`が`location ~ ^/meetings/static/(.*)$`より先にマッチしている可能性があります。

**解決方法**: `location ^~ /meetings/static/`を使用して、正規表現マッチを優先します：

```nginx
# より具体的なlocation（^~ を使用して正規表現マッチを優先）
location ^~ /meetings/static/ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

#### 2. アクセスログで確認

```bash
# リアルタイムでアクセスログを監視
docker exec nginx-proxy-manager tail -f /data/logs/proxy-host-6_access.log | grep meetings
```

ブラウザでページをリロードして、静的ファイルへのリクエストがログに表示されるか確認してください。

---

## 📝 チェックリスト

- [ ] Nginx設定ファイルを確認（locationブロックの順序）
- [ ] Advancedタブの設定を確認（正しい順序で記述されているか）
- [ ] Proxy Hostのステータスが「Online」のままであることを確認
- [ ] Nginx設定の再読み込み
- [ ] ブラウザのキャッシュをクリア
- [ ] `/meetings`でアクセスしてCSS/JSが正しく読み込まれることを確認
- [ ] 404エラーが出ていないか確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


