# 🔧 Nginx Proxy Manager - Advancedタブで静的ファイルパス修正

**作成日**: 2025-11-02  
**目的**: Proxy Host全体のAdvancedタブで静的ファイルのパスを修正

---

## ⚠️ 問題

Custom Location内で設定を追加するとProxy Hostがオフラインになるため、Proxy Host全体のAdvancedタブで設定します。

---

## ✅ 解決方法: Advancedタブでリライトルールを追加

### ステップ1: Proxy HostのAdvancedタブを開く

1. **Nginx Proxy ManagerのWeb UI**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

4. **「Custom Nginx Configuration」に以下を追加**:

```nginx
# /meetings の静的ファイルとAPI修正
location ~ ^/meetings/(static|api)/ {
    rewrite ^/meetings/(static|api)/(.*)$ /$1/$2 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# /analytics の静的ファイルとAPI修正
location ~ ^/analytics/(static|api)/ {
    rewrite ^/analytics/(static|api)/(.*)$ /$1/$2 break;
    proxy_pass http://192.168.68.110:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# /documents の静的ファイルとAPI修正
location ~ ^/documents/(static|api)/ {
    rewrite ^/documents/(static|api)/(.*)$ /$1/$2 break;
    proxy_pass http://192.168.68.110:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# /monitoring の静的ファイルとAPI修正
location ~ ^/monitoring/(static|api)/ {
    rewrite ^/monitoring/(static|api)/(.*)$ /$1/$2 break;
    proxy_pass http://192.168.68.110:3002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# /youtube の静的ファイルとAPI修正
location ~ ^/youtube/(static|api)/ {
    rewrite ^/youtube/(static|api)/(.*)$ /$1/$2 break;
    proxy_pass http://192.168.68.110:8111;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

5. **「Save」をクリック**

---

## ⚠️ 注意事項

### Custom Locationより前に記述する必要があります

**重要**: これらの`location`ブロックは、Custom Locationの設定より前に評価される必要があります。

Nginx Proxy Managerでは、Advancedタブの設定がCustom Locationの設定より前に配置されるため、この方法で動作するはずです。

---

## 🔍 動作確認

### ブラウザの開発者ツールで確認

1. **ブラウザで`https://yoshi-nas-sys.duckdns.org:8443/meetings`を開く**

2. **開発者ツールを開く**（F12キー）

3. **「Network」タブを開く**

4. **ページをリロード**

5. **以下のファイルが正常に読み込まれているか確認**:
   - CSSファイル: `style.css`など（200 OKが表示される）
   - JavaScriptファイル: `app.js`など
   - 画像ファイル: `logo.png`など

6. **404エラーが出ていないか確認**

---

## 📝 チェックリスト

- [ ] Proxy HostのAdvancedタブを開く
- [ ] Custom Nginx Configurationにリライトルールを追加
- [ ] Proxy Host全体を保存
- [ ] Proxy Hostのステータスが「Online」のままであることを確認
- [ ] `/meetings`でCSS/JSが正しく読み込まれることを確認
- [ ] 他のCustom Location（`/analytics`、`/documents`など）でも同様に確認

---

## 🧪 トラブルシューティング

### Proxy HostがOfflineになった場合

1. **Advancedタブの設定を一旦削除**

2. **Proxy Hostを保存**

3. **オンラインに戻ったか確認**

4. **設定を少しずつ追加して確認**

### 静的ファイルが読み込まれない場合

1. **ブラウザの開発者ツールで確認**
   - どのURLで静的ファイルを読み込もうとしているか
   - 404エラーが出ているか

2. **リライトルールを確認**
   - 正しいパスにリライトされているか
   - 正しいポート番号に転送されているか

---

## 📚 参考資料

- [Nginx locationディレクティブ](https://nginx.org/en/docs/http/ngx_http_core_module.html#location)
- [Nginx rewriteモジュール](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant



