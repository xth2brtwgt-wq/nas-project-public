# 🔧 meeting-minutes-byc - 静的ファイル404エラー最終修正

**作成日**: 2025-11-02  
**目的**: 静的ファイル404エラーの最終的な解決

---

## ⚠️ 現在の問題

- `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css` → 404エラー
- `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/js/app.js` → 404エラー
- アプリケーション側で直接アクセス: `http://192.168.68.110:5002/static/css/style.css` → 404エラー

---

## ✅ 修正内容

### 1. アプリケーション側の修正

#### `app.py`の修正
- `static_url_path`を`/static`に戻した（物理パスは`static/`フォルダ）
- テンプレートに`subfolder_path`を渡すように修正

#### `templates/index.html`の修正
- `{{ subfolder_path }}{{ url_for('static', ...) }}`を使用して静的ファイルのURLを生成

### 2. Nginx Proxy Managerの設定

#### Advancedタブの設定
```nginx
# /meetings の静的ファイル修正（認証を除外）
location ~ ^/meetings/static/(.*)$ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    # Basic認証を除外（静的ファイルは認証不要）
    auth_basic off;
}
```

---

## 📦 NAS環境でのデプロイ手順

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
docker compose build --no-cache
docker compose up -d
```

### ステップ4: アプリケーションのログを確認

```bash
docker logs meeting-minutes-byc --tail 50
```

以下のようなログが表示されることを確認：

```
サブフォルダ対応を有効化: APPLICATION_ROOT=/meetings
```

### ステップ5: 静的ファイルの存在を確認

```bash
# コンテナ内で静的ファイルの存在を確認
docker exec meeting-minutes-byc ls -la /app/static/css/
docker exec meeting-minutes-byc ls -la /app/static/js/
```

### ステップ6: アプリケーションに直接アクセスして静的ファイルを確認

```bash
# アプリケーションに直接アクセスして静的ファイルを確認
curl -I http://192.168.68.110:5002/static/css/style.css
```

**期待される結果**: HTTP 200 OK

もし404エラーが出る場合、Dockerイメージのビルド時に静的ファイルが正しくコピーされていない可能性があります。

---

## 🔍 トラブルシューティング

### アプリケーション側で静的ファイルが見つからない場合

#### 1. Dockerイメージを再ビルド

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

#### 2. 静的ファイルを手動でコピー（一時的な解決）

```bash
# コンテナ内で静的ファイルの存在を確認
docker exec meeting-minutes-byc ls -la /app/static/

# 静的ファイルが存在しない場合、手動でコピー
docker cp static/css/style.css meeting-minutes-byc:/app/static/css/
docker cp static/js/app.js meeting-minutes-byc:/app/static/js/
```

#### 3. Dockerfileを確認

`meeting-minutes-byc/Dockerfile`に静的ファイルをコピーする設定があるか確認：

```dockerfile
COPY static/ /app/static/
```

### Nginx経由で404エラーが出る場合

#### 1. Nginx設定の再読み込み

```bash
docker exec nginx-proxy-manager nginx -t
docker exec nginx-proxy-manager nginx -s reload
```

#### 2. アクセスログを確認

```bash
docker exec nginx-proxy-manager tail -f /data/logs/proxy-host-6_access.log | grep meetings
```

#### 3. エラーログを確認

```bash
docker exec nginx-proxy-manager tail -f /data/logs/proxy-host-6_error.log
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

## 📝 チェックリスト

- [ ] 最新コードを取得
- [ ] `.env`ファイルに`SUBFOLDER_PATH=/meetings`が設定されているか確認
- [ ] Dockerコンテナを再ビルド・再起動
- [ ] アプリケーションのログで`APPLICATION_ROOT=/meetings`が設定されているか確認
- [ ] 静的ファイルの存在を確認（コンテナ内）
- [ ] アプリケーションに直接アクセスして静的ファイルを確認（200 OKか404か）
- [ ] Nginx Proxy ManagerのAdvancedタブで認証を除外する設定を追加
- [ ] Nginx設定の再読み込み
- [ ] ブラウザのキャッシュをクリア
- [ ] `/meetings`でアクセスしてCSS/JSが正しく読み込まれることを確認
- [ ] 404エラーが出ていないか確認
- [ ] CSSが正しく適用されているか確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


