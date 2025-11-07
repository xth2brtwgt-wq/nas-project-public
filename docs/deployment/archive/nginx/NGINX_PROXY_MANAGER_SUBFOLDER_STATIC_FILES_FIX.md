# 🔧 Nginx Proxy Manager - サブフォルダ配信時の静的ファイル問題解決

**作成日**: 2025-11-02  
**目的**: Custom Locationでサブフォルダ配信時にCSS/JS/画像が読み込めない問題を解決

---

## ⚠️ 問題

`/meetings`でアクセスすると、ページは表示されるがレイアウトが崩れている。

**原因**: 
- 静的ファイル（CSS、JavaScript、画像）のパスが正しく解決されていない
- アプリケーションが`/static/style.css`を参照しているが、実際には`/meetings/static/style.css`を参照しようとする
- または、`/static/style.css`を参照しようとするが、Nginxが正しく処理できない

---

## ✅ 解決方法

### 方法1: Advancedタブでリライトルールを追加（推奨）

#### ステップ1: Proxy HostのAdvancedタブを開く

1. **Nginx Proxy ManagerのWeb UIにアクセス**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

4. **「Custom Nginx Configuration」に以下を追加**:

```nginx
# 静的ファイルのパス修正
location ~ ^/(analytics|documents|monitoring|meetings|youtube)/static/ {
    rewrite ^/(analytics|documents|monitoring|meetings|youtube)/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8001;  # 各サービスに応じてポート番号を変更
}

# APIエンドポイントのパス修正
location ~ ^/(analytics|documents|monitoring|meetings|youtube)/api/ {
    rewrite ^/(analytics|documents|monitoring|meetings|youtube)/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8001;  # 各サービスに応じてポート番号を変更
}
```

**注意**: 上記の設定は各サービスに応じて調整が必要です。より簡単な方法として、**各Custom Locationに個別に設定**する方法があります。

---

### 方法2: 各Custom Locationに個別にリライトルールを追加（推奨）

各Custom Locationの「Custom Nginx configuration」に以下を追加：

#### `/meetings`のCustom Location設定

1. **Custom Locationの`/meetings`を編集**

2. **「Custom Nginx configuration」に以下を追加**:

```nginx
# 静的ファイルのパス修正
location ~ ^/meetings/static/ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
}

location ~ ^/meetings/api/ {
    rewrite ^/meetings/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:5002;
}

# WebSocket設定（Socket.IO用）
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

3. **「Save」をクリック**

---

#### `/analytics`のCustom Location設定（amazon-analytics）

```nginx
location ~ ^/analytics/static/ {
    rewrite ^/analytics/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8001;
}

location ~ ^/analytics/api/ {
    rewrite ^/analytics/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8001;
}
```

---

#### `/documents`のCustom Location設定（document-automation）

```nginx
location ~ ^/documents/static/ {
    rewrite ^/documents/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8080;
}

location ~ ^/documents/api/ {
    rewrite ^/documents/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8080;
}
```

---

#### `/monitoring`のCustom Location設定（nas-dashboard-monitoring）

```nginx
location ~ ^/monitoring/static/ {
    rewrite ^/monitoring/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:3002;
}

location ~ ^/monitoring/api/ {
    rewrite ^/monitoring/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:3002;
}

# WebSocket設定
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

---

#### `/youtube`のCustom Location設定（youtube-to-notion）

```nginx
location ~ ^/youtube/static/ {
    rewrite ^/youtube/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8111;
}

location ~ ^/youtube/api/ {
    rewrite ^/youtube/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8111;
}
```

---

## 🔍 問題の詳細説明

### 静的ファイルのパス問題

**アプリケーション内のHTML**:
```html
<link rel="stylesheet" href="/static/style.css">
```

**問題**:
- `/meetings`でアクセスすると、ブラウザは`/meetings/static/style.css`を参照しようとする
- しかし、実際の静的ファイルは`/static/style.css`にある
- そのため、404エラーになり、CSSが読み込まれない

**解決**:
- `rewrite`ルールで`/meetings/static/style.css`を`/static/style.css`に書き換える
- これにより、正しいパスで静的ファイルにアクセスできる

---

## ✅ 動作確認

### ブラウザの開発者ツールで確認

1. **ブラウザで`https://yoshi-nas-sys.duckdns.org:8443/meetings`を開く**

2. **開発者ツールを開く**（F12キー）

3. **「Network」タブを開く**

4. **ページをリロード**

5. **以下のファイルが正常に読み込まれているか確認**:
   - CSSファイル: `style.css`など
   - JavaScriptファイル: `app.js`など
   - 画像ファイル: `logo.png`など

6. **404エラーが出ていないか確認**

---

## 📝 チェックリスト

- [ ] `/meetings`のCustom Locationにリライトルールを追加
- [ ] `/analytics`のCustom Locationにリライトルールを追加
- [ ] `/documents`のCustom Locationにリライトルールを追加
- [ ] `/monitoring`のCustom Locationにリライトルールを追加
- [ ] `/youtube`のCustom Locationにリライトルールを追加
- [ ] Proxy Host全体を保存
- [ ] 各サービスでCSS/JS/画像が正しく読み込まれることを確認

---

## 📚 参考資料

- [Nginx Proxy Manager公式ドキュメント](https://nginxproxymanager.com/)
- [Nginx rewriteルール](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant



