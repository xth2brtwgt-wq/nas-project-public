# 🔧 Nginx Proxy Manager - 静的ファイル404エラー解決

**作成日**: 2025-11-02  
**目的**: `/meetings/static/...`へのアクセスで404エラーが発生する問題を解決

---

## ⚠️ 問題

`static_url_path=/meetings/static`を設定したため、`url_for('static', ...)`が`/meetings/static/css/style.css`を生成するようになりました。

しかし、Nginx Proxy ManagerのCustom Location（`/meetings`）は、`/meetings`へのアクセスを`http://192.168.68.110:5002/`に転送しているため、`/meetings/static/css/style.css`へのリクエストが`http://192.168.68.110:5002/meetings/static/css/style.css`に転送され、アプリケーション側で見つからず404エラーになります。

---

## ✅ 解決方法

### 方法1: Proxy Host全体のAdvancedタブでリライトルールを追加

Custom Location内では設定できないため、Proxy Host全体のAdvancedタブで設定します。

#### ステップ1: Proxy HostのAdvancedタブを開く

1. **Nginx Proxy ManagerのWeb UI**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

4. **「Custom Nginx Configuration」に以下を追加**:

```nginx
# /meetings の静的ファイル修正（Custom Locationより前に記述）
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

5. **「Save」をクリック**

6. **Proxy Hostのステータスを確認**
   - 「Online」のままであることを確認

---

### 方法2: アプリケーション側でstatic_url_pathを変更（代替案）

`static_url_path`を`/meetings/static`ではなく、通常の`/static`のままにして、Nginx側でリライトする方法もあります。

この場合、`app.py`の設定を変更：

```python
# static_url_pathは通常の'/static'のまま
app = Flask(__name__, static_url_path='/static')
```

ただし、この場合、HTML内の`url_for('static', ...)`が`/static/css/style.css`を生成するため、ブラウザは`/static/css/style.css`をリクエストします。

Nginx側で`/static/css/style.css`へのアクセスを`/meetings/static/css/style.css`にリライトする必要がありますが、これは複雑です。

**推奨**: 方法1（Advancedタブでリライトルールを追加）を試してください。

---

## ✅ 動作確認

### ブラウザの開発者ツールで確認

1. **ブラウザで`https://yoshi-nas-sys.duckdns.org:8443/meetings`を開く**

2. **開発者ツールを開く**（F12キー）

3. **「Network」タブを開く**

4. **ページをリロード**（`Cmd+Shift+R`または`Ctrl+Shift+R`）

5. **CSSファイルとJavaScriptファイルを確認**:
   - `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css`
   - `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/js/app.js`
   - これらのURLで200 OKが返ることを確認

6. **404エラーが出ていないか確認**

---

## 📝 チェックリスト

- [ ] Proxy HostのAdvancedタブを開く
- [ ] Custom Nginx Configurationにリライトルールを追加
- [ ] Proxy Host全体を保存
- [ ] Proxy Hostのステータスが「Online」のままであることを確認
- [ ] `/meetings`でアクセスしてCSS/JSが正しく読み込まれることを確認
- [ ] 404エラーが出ていないか確認

---

## 🧪 トラブルシューティング

### Proxy HostがOfflineになった場合

1. **Advancedタブの設定を一旦削除**

2. **Proxy Hostを保存**

3. **オンラインに戻ったか確認**

4. **設定を少しずつ追加して確認**

### まだ404エラーが出る場合

1. **Nginx Proxy Managerのログを確認**:
   ```bash
   docker logs nginx-proxy-manager --tail 100
   ```

2. **アプリケーション側のログを確認**:
   ```bash
   docker logs meeting-minutes-byc --tail 100
   ```

---

## 📚 参考資料

- [Nginx locationディレクティブ](https://nginx.org/en/docs/http/ngx_http_core_module.html#location)
- [Nginx rewriteモジュール](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant



