# 🔧 静的ファイル404エラー - 代替修正方法

**作成日**: 2025-11-02  
**目的**: Advancedタブの設定が反映されない場合の代替修正方法

---

## ⚠️ 現在の問題

- Advancedタブにリライトルールを追加したが、まだ404エラーが出る
- 設定が反映されていない可能性がある

---

## ✅ 代替修正方法: Custom Locationの設定を変更

Advancedタブの設定が反映されない場合、Custom Locationの設定を変更して対応します。

### 方法1: Custom Locationに「Forward Scheme」と「Forward Port」を正しく設定

1. **Nginx Proxy ManagerのWeb UI**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Custom Locations」タブをクリック**

4. **`/meetings`のCustom Locationを編集**

5. **以下の設定を確認**:
   - **Location**: `/meetings`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110/`（末尾にスラッシュ）
   - **Forward Port**: `5002`

6. **「Custom Nginx configuration」に以下を追加**（以前試したが、再度試す）:

```nginx
# 静的ファイルのパス修正（rewriteのみ）
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

7. **「Save」をクリック**

8. **Proxy Hostのステータスを確認**
   - 「Online」のままであることを確認
   - 「Offline」になった場合は、設定を削除して以下を試してください

### 方法2: アプリケーション側の設定を変更

Custom LocationとNginx設定で解決できない場合、アプリケーション側の設定を変更します。

#### meeting-minutes-bycの設定を変更

1. **`meeting-minutes-byc/app.py`を確認**:

現在の設定：
```python
static_url_path = '/static'
if SUBFOLDER_PATH and SUBFOLDER_PATH != '/':
    static_url_path = f'{SUBFOLDER_PATH}/static'
```

この設定により、`url_for('static', ...)`が`/meetings/static/...`を生成しています。

2. **設定を変更**（`static_url_path`を通常の`/static`に戻す）:

```python
# static_url_pathを通常の/staticに戻す
static_url_path = '/static'

app = Flask(__name__, static_url_path=static_url_path)
```

3. **テンプレート側で`url_for`を修正**:

`templates/index.html`で、静的ファイルのURLを手動で生成：

```html
<!-- 変更前 -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

<!-- 変更後 -->
<link rel="stylesheet" href="/meetings/static/css/style.css">
```

または、Flaskの`url_for`を使いつつ、`SUBFOLDER_PATH`を手動で追加：

```html
<link rel="stylesheet" href="{{ SUBFOLDER_PATH }}{{ url_for('static', filename='css/style.css') }}">
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

- [ ] Custom Locationの設定を確認
- [ ] Custom Locationの「Custom Nginx configuration」に`rewrite`ディレクティブを追加
- [ ] Proxy Hostのステータスが「Online」のままであることを確認
- [ ] ブラウザのキャッシュをクリア
- [ ] `/meetings`でアクセスしてCSS/JSが正しく読み込まれることを確認
- [ ] 404エラーが出ていないか確認
- [ ] CSSが正しく適用されているか確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


