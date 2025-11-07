# ✅ 静的ファイル404エラー - 最終的な修正手順

**作成日**: 2025-11-02  
**目的**: `/meetings/static/...`で404エラーが発生する問題の最終的な解決

---

## ✅ 修正内容

### アプリケーション側の変更

- `static_url_path`を`/meetings/static`に設定（`SUBFOLDER_PATH`が設定されている場合）
- `APPLICATION_ROOT`を設定（`url_for`が自動的に`/meetings`を付ける）

**動作**:
- `SUBFOLDER_PATH=/meetings`を設定すると、`static_url_path`が`/meetings/static`になる
- これにより、`url_for('static', ...)`が`/meetings/static/css/style.css`を生成
- ただし、Flask側では実際の静的ファイルは`/static/css/style.css`にある（物理パスは`static/`フォルダ）
- そのため、Nginx側で`/meetings/static/...`を`/static/...`にリライトする必要がある

---

## 🔧 Nginx Proxy Managerの設定

### ステップ1: Proxy HostのAdvancedタブを開く

1. **Nginx Proxy ManagerのWeb UI**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

### ステップ2: Custom Nginx Configurationにリライトルールを追加

**「Custom Nginx Configuration」に以下を追加**（既存の設定があれば削除してから追加）:

```nginx
# /meetings の静的ファイル修正（Custom Locationより前に記述）
# static_url_path=/meetings/staticに設定したため、url_forが/meetings/static/...を生成するが、
# Flask側では実際の静的ファイルは/static/...にある（物理パスはstatic/フォルダ）ため、リライトが必要
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

**重要**: `location`ブロックは**Custom Locationより前に記述**する必要があります。Nginxは最初にマッチした`location`を使用するためです。

### ステップ3: Saveして確認

1. **「Save」をクリック**

2. **Proxy Hostのステータスを確認**
   - 「Online」のままであることを確認
   - 「Offline」になった場合は、設定を削除して再試行

---

## 📦 NAS環境でのデプロイ

### ステップ1: 最新コードを取得

```bash
ssh -p 23456 AdminUser@192.168.68.110
cd /home/AdminUser/nas-project/meeting-minutes-byc
git pull origin feature/monitoring-fail2ban-integration
```

### ステップ2: 環境変数の確認

`.env`ファイルに`SUBFOLDER_PATH=/meetings`が設定されているか確認：

```bash
cat .env | grep SUBFOLDER_PATH
```

設定されていない場合は追加：

```bash
echo "SUBFOLDER_PATH=/meetings" >> .env
```

### ステップ3: Dockerコンテナを再ビルド・再起動

```bash
docker compose down
docker compose build
docker compose up -d
```

### ステップ4: ログを確認

```bash
docker logs meeting-minutes-byc --tail 50
```

以下のようなログが表示されることを確認：

```
サブフォルダ対応を有効化: APPLICATION_ROOT=/meetings
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

---

## 📝 チェックリスト

- [ ] `meeting-minutes-byc/app.py`を修正（`static_url_path`を`/meetings/static`に設定）
- [ ] 変更をコミット・プッシュ
- [ ] Nginx Proxy ManagerのAdvancedタブでリライトルールを追加
- [ ] Proxy Hostのステータスが「Online」のままであることを確認
- [ ] NAS環境で最新コードを取得
- [ ] `.env`ファイルに`SUBFOLDER_PATH=/meetings`が設定されているか確認
- [ ] Dockerコンテナを再ビルド・再起動
- [ ] アプリケーション側のログで`APPLICATION_ROOT=/meetings`が設定されているか確認
- [ ] ブラウザのキャッシュをクリア
- [ ] `/meetings`でアクセスしてCSS/JSが正しく読み込まれることを確認
- [ ] 404エラーが出ていないか確認
- [ ] CSSが正しく適用されているか確認

---

## 📚 参考資料

- [Flask APPLICATION_ROOT](https://flask.palletsprojects.com/en/latest/config/#APPLICATION_ROOT)
- [Flask static_url_path](https://flask.palletsprojects.com/en/latest/config/#static-url-path)
- [Nginx locationディレクティブ](https://nginx.org/en/docs/http/ngx_http_core_module.html#location)
- [Nginx rewriteモジュール](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


