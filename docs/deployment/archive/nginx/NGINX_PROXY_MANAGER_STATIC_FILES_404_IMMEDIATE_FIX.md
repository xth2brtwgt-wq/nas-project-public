# 🔧 静的ファイル404エラー - 即座の修正手順

**作成日**: 2025-11-02  
**目的**: `/meetings/static/...`で404エラーが発生している問題を即座に解決

---

## ⚠️ 現在の問題

- `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css` → 404エラー
- `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/js/app.js` → 404エラー

**原因**: Nginx Proxy ManagerのAdvancedタブにリライトルールが追加されていない、または正しく動作していない可能性があります。

---

## ✅ 即座の修正手順

### ステップ1: Nginx Proxy ManagerのAdvancedタブを確認

1. **Nginx Proxy ManagerのWeb UI**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

4. **「Custom Nginx Configuration」を確認**

### ステップ2: リライトルールを追加または修正

**「Custom Nginx Configuration」に以下を追加**（既存の設定があれば**すべて削除**してから追加）:

```nginx
# /meetings の静的ファイル修正（Custom Locationより前に記述）
# url_forが/meetings/static/...を生成するが、Flask側では実際の静的ファイルは/static/...にある
location ~ ^/meetings/static/(.*)$ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# /meetings のAPI修正
location ~ ^/meetings/api/(.*)$ {
    rewrite ^/meetings/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**重要**: 
- `location`ブロックは**Custom Locationより前に記述**する必要があります
- Nginxは最初にマッチした`location`を使用するため、より具体的な`location`（`/meetings/static/`）を先に記述します

### ステップ3: Saveして確認

1. **「Save」をクリック**

2. **Proxy Hostのステータスを確認**
   - 「Online」のままであることを確認
   - 「Offline」になった場合は、設定を削除して以下を試してください

### ステップ4: もしOfflineになった場合の代替方法

Proxy HostがOfflineになった場合、設定を削除してから、**よりシンプルな設定**を試してください：

```nginx
# /meetings の静的ファイル修正（シンプル版）
location /meetings/static/ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

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
   - `style.css`のリクエストURL: `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css`
   - ステータスコード: **200 OK**（404ではない）
   - `app.js`のリクエストURL: `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/js/app.js`
   - ステータスコード: **200 OK**（404ではない）

3. **CSSが正しく適用されているか確認**
   - レイアウトが崩れていないか確認
   - 色が正しく表示されているか確認

---

## 🔍 トラブルシューティング

### Proxy HostがOfflineになった場合

1. **Advancedタブの設定を一旦削除**
2. **Proxy Hostを保存**
3. **オンラインに戻ったか確認**
4. **設定を少しずつ追加して確認**

### まだ404エラーが出る場合

1. **Nginx Proxy Managerのログを確認**:

```bash
ssh -p 23456 AdminUser@192.168.68.110
docker logs nginx-proxy-manager --tail 100 | grep meetings
```

2. **アプリケーション側のログを確認**:

```bash
docker logs meeting-minutes-byc --tail 100
```

3. **ブラウザの開発者ツール → Networkタブ**
   - リクエストURLを確認
   - ステータスコードを確認
   - レスポンスヘッダーを確認

4. **Custom Locationの設定を確認**
   - `/meetings`のCustom Locationが正しく設定されているか確認
   - 「Forward Hostname/IP」に`http://192.168.68.110:5002/`が設定されているか確認（末尾のスラッシュが重要）

---

## 📝 チェックリスト

- [ ] Nginx Proxy ManagerのAdvancedタブを開く
- [ ] 「Custom Nginx Configuration」にリライトルールを追加
- [ ] Proxy Hostのステータスが「Online」のままであることを確認
- [ ] ブラウザのキャッシュをクリア
- [ ] `/meetings`でアクセスしてCSS/JSが正しく読み込まれることを確認
- [ ] 404エラーが出ていないか確認
- [ ] CSSが正しく適用されているか確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


