# 🔧 Nginx Proxy Manager - サブフォルダ配信時の静的ファイル問題解決（簡易版）

**作成日**: 2025-11-02  
**目的**: Custom Location内でlocationブロックが使えない場合の代替方法

---

## ⚠️ 問題

Custom Locationの「Custom Nginx configuration」に`location`ブロックを追加すると、Proxy Hostのステータスがオフラインになる。

**原因**: Custom Location内で`location`ブロックをネストすることはできません。

---

## ✅ 解決方法

### 方法1: Advancedタブでリライトルールを追加（推奨）

Proxy Host全体のAdvancedタブでリライトルールを追加します。

#### ステップ1: Proxy HostのAdvancedタブを開く

1. **Nginx Proxy ManagerのWeb UI**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

4. **「Custom Nginx Configuration」に以下を追加**:

```nginx
# 静的ファイルのパス修正（各サービスのCustom Locationより前に記述）
location ~ ^/(analytics|documents|monitoring|meetings|youtube)/static/ {
    rewrite ^/(analytics|documents|monitoring|meetings|youtube)/static/(.*)$ /static/$1 break;
    
    # 各サービスに応じたポート番号で転送
    if ($uri ~* "^/analytics/") {
        proxy_pass http://192.168.68.110:8001;
        break;
    }
    if ($uri ~* "^/documents/") {
        proxy_pass http://192.168.68.110:8080;
        break;
    }
    if ($uri ~* "^/monitoring/") {
        proxy_pass http://192.168.68.110:3002;
        break;
    }
    if ($uri ~* "^/meetings/") {
        proxy_pass http://192.168.68.110:5002;
        break;
    }
    if ($uri ~* "^/youtube/") {
        proxy_pass http://192.168.68.110:8111;
        break;
    }
}

# APIエンドポイントのパス修正
location ~ ^/(analytics|documents|monitoring|meetings|youtube)/api/ {
    rewrite ^/(analytics|documents|monitoring|meetings|youtube)/api/(.*)$ /api/$1 break;
    
    # 各サービスに応じたポート番号で転送
    if ($uri ~* "^/analytics/") {
        proxy_pass http://192.168.68.110:8001;
        break;
    }
    if ($uri ~* "^/documents/") {
        proxy_pass http://192.168.68.110:8080;
        break;
    }
    if ($uri ~* "^/monitoring/") {
        proxy_pass http://192.168.68.110:3002;
        break;
    }
    if ($uri ~* "^/meetings/") {
        proxy_pass http://192.168.68.110:5002;
        break;
    }
    if ($uri ~* "^/youtube/") {
        proxy_pass http://192.168.68.110:8111;
        break;
    }
}
```

**注意**: この方法は複雑で、Nginxの`if`文を使用するため推奨されません。

---

### 方法2: アプリケーション側でサブフォルダ対応にする（推奨・最確実）

各アプリケーション側でベースパスを設定します。

#### meeting-minutes-bycの設定

`meeting-minutes-byc/app.py`で`APPLICATION_ROOT`を設定：

```python
app = Flask(__name__, static_url_path='/meetings/static', static_folder='static')
app.config['APPLICATION_ROOT'] = '/meetings'
```

または、Flaskの`url_for`を使用している場合、`SCRIPT_NAME`を設定：

```python
from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)
app.config['APPLICATION_ROOT'] = '/meetings'
```

---

### 方法3: シンプルなリライトルール（推奨・簡単）

Custom Locationの「Custom Nginx configuration」に、`location`ブロックを使わずにリライトルールを記述します。

#### `/meetings`のCustom Location設定

**「Custom Nginx configuration」に以下を追加**:

```nginx
# 静的ファイルとAPIのパス修正（rewriteのみ）
rewrite ^/meetings/static/(.*)$ /static/$1 break;
rewrite ^/meetings/api/(.*)$ /api/$1 break;

# WebSocket設定（Socket.IO用）
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

**重要**: `location`ブロックは使わず、`rewrite`ディレクティブのみを使用します。

---

## ✅ 推奨される解決方法

### ステップ1: Custom Locationからlocationブロックを削除

1. **Custom Locationの`/meetings`を編集**

2. **「Custom Nginx configuration」から`location`ブロックを削除**

3. **以下を追加**（`location`ブロックなし）:

```nginx
# 静的ファイルとAPIのパス修正
rewrite ^/meetings/static/(.*)$ /static/$1 break;
rewrite ^/meetings/api/(.*)$ /api/$1 break;

# WebSocket設定
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

4. **「Save」をクリック**

5. **Proxy Host全体を保存**

---

### ステップ2: 他のCustom Locationにも同様に設定

#### `/analytics`
```nginx
rewrite ^/analytics/static/(.*)$ /static/$1 break;
rewrite ^/analytics/api/(.*)$ /api/$1 break;
```

#### `/documents`
```nginx
rewrite ^/documents/static/(.*)$ /static/$1 break;
rewrite ^/documents/api/(.*)$ /api/$1 break;
```

#### `/monitoring`
```nginx
rewrite ^/monitoring/static/(.*)$ /static/$1 break;
rewrite ^/monitoring/api/(.*)$ /api/$1 break;

# WebSocket設定
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

#### `/youtube`
```nginx
rewrite ^/youtube/static/(.*)$ /static/$1 break;
rewrite ^/youtube/api/(.*)$ /api/$1 break;
```

---

## 📝 チェックリスト

- [ ] `/meetings`のCustom Locationから`location`ブロックを削除
- [ ] `/meetings`に`rewrite`ディレクティブのみを追加
- [ ] Proxy Host全体を保存
- [ ] Proxy Hostのステータスが「Online」になることを確認
- [ ] `/meetings`でレイアウトが正しく表示されることを確認
- [ ] 他のCustom Locationにも同様の設定を追加

---

## 📚 参考資料

- [Nginx rewriteモジュール](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html)
- [Flask APPLICATION_ROOT](https://flask.palletsprojects.com/en/latest/config/#APPLICATION_ROOT)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant



