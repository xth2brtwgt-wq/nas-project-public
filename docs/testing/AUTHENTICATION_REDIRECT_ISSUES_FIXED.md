# 認証・リダイレクト問題の解決まとめ

**日時**: 2025-11-06  
**影響範囲**: nas-dashboard, document-automation

---

## 📋 解決した問題一覧

1. **ログイン後のリダイレクト問題** - `/documents`へのリダイレクトが機能しない
2. **nextパラメータの伝播問題** - ログイン後に元のページに戻れない
3. **ドキュメント画面の認証回避問題** - ログアウト後もアクセス可能だった
4. **システムステータス表示問題** - ドキュメント画面でシステム情報が表示されない
5. **認証データベースアクセス権限エラー** - `Permission denied`エラー

---

## 🐛 問題1: ログイン後のリダイレクト問題

### 症状
- ログイン後に`/documents`にアクセスしようとすると、ダッシュボード（`/`）にリダイレクトされる
- `next`パラメータが正しく処理されない

### 原因
1. **フロントエンド**: ログインフォーム送信時に`next`パラメータが失われる
2. **バックエンド**: `next`パラメータがフォームデータとURL引数の両方から取得されていない
3. **URLエンコード**: `next`パラメータが正しくURLエンコードされていない

### 解決方法

#### 1. ログインテンプレートにhidden inputを追加

**ファイル**: `nas-dashboard/templates/login.html`

```html
<form method="POST" action="{{ url_for('login') }}" id="loginForm">
    {# nextパラメータをhidden inputとして保持 #}
    {% set next_param = request.args.get('next') or '' %}
    {% if next_param %}
    <input type="hidden" name="next" id="nextInput" value="{{ next_param }}">
    {% else %}
    <input type="hidden" name="next" id="nextInput" value="">
    {% endif %}
    <!-- ... username and password fields ... -->
</form>
```

#### 2. JavaScriptでnextパラメータを動的に設定

**ファイル**: `nas-dashboard/templates/login.html`

```javascript
(function() {
    const urlParams = new URLSearchParams(window.location.search);
    const nextParam = urlParams.get('next');
    const nextInput = document.getElementById('nextInput');
    
    if (nextParam && nextInput) {
        nextInput.value = nextParam;
        console.log('[AUTH] フロントエンドでnextパラメータを設定:', nextParam);
    }
    
    // フォーム送信時にnextパラメータが含まれているか確認
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const formData = new FormData(loginForm);
            const nextValue = formData.get('next');
            console.log('[AUTH] フォーム送信時のnextパラメータ:', nextValue);
        });
    }
})();
```

#### 3. バックエンドでnextパラメータを正しく処理

**ファイル**: `nas-dashboard/app.py`

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # ... username/password validation ...
        if session_id:
            # フォームデータとURL引数の両方からnextパラメータを取得
            form_next = request.form.get('next')
            args_next = request.args.get('next')
            next_param = form_next or args_next
            
            if next_param:
                from urllib.parse import unquote
                redirect_url = unquote(next_param)
                
                # セキュリティチェック（相対パスのみ許可）
                if not redirect_url.startswith('/') or redirect_url.startswith('//'):
                    redirect_url = url_for('dashboard')
                else:
                    # Nginx Proxy Manager経由の場合は外部URLに変換
                    base_url = get_base_url()
                    if 'yoshi-nas-sys.duckdns.org' in base_url or ':8443' in base_url:
                        # ... 外部URLへの変換処理 ...
                        redirect_url = full_redirect_url
                
                response = redirect(redirect_url)
            else:
                response = redirect(url_for('dashboard'))
            
            response.set_cookie('session_id', session_id, ...)
            return response
```

#### 4. require_authデコレータでnextパラメータを追加

**ファイル**: `nas-dashboard/app.py`

```python
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            current_path = request.path
            login_url = url_for('login')
            if current_path and current_path != '/login' and current_path != '/':
                from urllib.parse import quote
                encoded_path = quote(current_path, safe='/')
                login_url = f"{url_for('login')}?next={encoded_path}"
            return redirect(login_url)
        return f(*args, **kwargs)
    return decorated_function
```

---

## 🐛 問題2: ドキュメント画面の認証回避問題

### 症状
- ログアウト後、直接`/documents`にアクセスすると、ドキュメント画面が表示される
- 認証チェックが機能していない

### 原因
1. **フロントエンド**: 認証チェックが実行される前にページが表示される
2. **バックエンド**: `/status`エンドポイントに認証が設定されていない

### 解決方法

#### 1. /statusエンドポイントに認証を追加

**ファイル**: `document-automation/app/api/main.py`

```python
@app.get("/status")
async def system_status(request: Request, user: Optional[Dict] = Depends(require_auth)):
    """システム状態"""
    version_info = get_version_info()
    return {
        "status": "healthy",
        "version": version_info["version"],
        # ... その他の情報 ...
    }
```

#### 2. フロントエンドで認証チェックを追加

**ファイル**: `document-automation/app/templates/index.html`

```javascript
window.SUBFOLDER_PATH = '{{ subfolder_path }}';
(function() {
    async function checkAuth() {
        try {
            const subfolderPath = window.SUBFOLDER_PATH || '/documents';
            const statusPath = `${subfolderPath}/status`;
            
            const response = await fetch(statusPath, {
                credentials: 'include',
                redirect: 'manual'
            });
            
            if (response.status === 307 || response.status === 302) {
                const location = response.headers.get('Location');
                if (location && location.includes('/login')) {
                    const loginUrl = location.includes('next=') 
                        ? location 
                        : `${location}?next=${encodeURIComponent(subfolderPath)}`;
                    window.location.href = loginUrl;
                    return;
                }
            }
            
            if (response.ok) {
                console.log('[AUTH] 認証成功');
            } else {
                // 認証エラー
                const loginUrl = `${externalUrl}/login?next=${encodeURIComponent(subfolderPath)}`;
                window.location.href = loginUrl;
                return;
            }
        } catch (error) {
            console.error('[AUTH] 認証チェックエラー:', error);
        }
    }
    checkAuth();
})();
```

---

## 🐛 問題3: システムステータス表示問題

### 症状
- ドキュメント画面でシステムステータス（バージョン、処理モードなど）が表示されない
- コンソールにエラーが表示される

### 原因
1. **HttpOnly Cookie**: JavaScriptから`session_id`クッキーを読み取れない
2. **ネットワークエラー**: ステータスコード0のエラーが無限ループする
3. **認証チェックのタイミング**: ログイン直後に認証チェックがスキップされる

### 解決方法

#### 1. ステータスコード0の再試行ロジックを追加

**ファイル**: `document-automation/app/templates/index.html`

```javascript
async function checkAuth() {
    try {
        // ... 認証チェック処理 ...
        
        if (response.status === 0) {
            if (typeof window.authCheckRetryCount === 'undefined') {
                window.authCheckRetryCount = 0;
            }
            window.authCheckRetryCount++;
            const MAX_AUTH_RETRY_COUNT = 3;
            
            if (window.authCheckRetryCount <= MAX_AUTH_RETRY_COUNT) {
                console.log(`[AUTH] ネットワークエラーが検出されました。${window.authCheckRetryCount}回目の再試行（最大${MAX_AUTH_RETRY_COUNT}回）。1秒後に再試行します。`);
                setTimeout(() => {
                    checkAuth();
                }, 1000);
                return;
            } else {
                console.error('[AUTH] ネットワークエラーが継続しています。認証チェックの再試行を中止します。');
                window.authCheckRetryCount = 0;
                return;
            }
        }
        
        if (typeof window.authCheckRetryCount !== 'undefined') {
            window.authCheckRetryCount = 0;
        }
        
        // ... 残りの処理 ...
    } catch (error) {
        console.error('[AUTH] 認証チェックエラー:', error);
    }
}
```

#### 2. loadSystemStatus関数の再試行ロジックを追加

**ファイル**: `document-automation/app/static/js/app.js`

```javascript
let systemStatusRetryCount = 0;
const MAX_RETRY_COUNT = 3;

async function loadSystemStatus() {
    try {
        const response = await fetch(apiPath('/status'), {
            credentials: 'include',
            redirect: 'manual'
        });
        
        if (response.status === 0) {
            systemStatusRetryCount++;
            if (systemStatusRetryCount <= MAX_RETRY_COUNT) {
                console.log(`[AUTH] ネットワークエラーが検出されました（ステータスコード0）。${systemStatusRetryCount}回目の再試行（最大${MAX_RETRY_COUNT}回）。1秒後に再試行します。`);
                setTimeout(() => {
                    loadSystemStatus();
                }, 1000);
                return;
            } else {
                console.error('[AUTH] ネットワークエラーが継続しています。再試行を中止します。');
                document.getElementById('processing-mode').textContent = 'エラー: ネットワークエラー';
                document.getElementById('ocr-engine').textContent = 'エラー: ネットワークエラー';
                document.getElementById('ai-provider').textContent = 'エラー: ネットワークエラー';
                systemStatusRetryCount = 0;
                return;
            }
        }
        
        systemStatusRetryCount = 0;
        
        // ... 残りの処理 ...
    } catch (error) {
        console.error('システムステータス読み込みエラー:', error);
    }
}
```

#### 3. HttpOnly Cookieのチェックを削除

**ファイル**: `document-automation/app/static/js/app.js`

```javascript
// ❌ 削除: HttpOnly CookieはJavaScriptから読み取れない
// if (document.cookie.includes('session_id=') === false) {
//     // ...
// }

// ✅ 正しい方法: 認証チェックはAPIリクエストのレスポンスで判断
if (response.status === 307 || response.status === 302) {
    // リダイレクトが返された場合は認証が必要
}
```

---

## 🐛 問題4: 認証データベースアクセス権限エラー

### 症状
- ログに`Permission denied: '/nas-project-data/nas-dashboard/auth.db'`エラーが表示される
- ドキュメント画面で認証が機能しない

### 原因
1. **ファイル所有者**: `auth.db`の所有者が`root:root`で、コンテナ内の`appuser`（UID 1000）がアクセスできない
2. **ディレクトリ権限**: 親ディレクトリに実行権限がない

### 解決方法

#### 1. ファイル所有者を変更

```bash
# NAS上で実行
# 1. AdminUserのUID/GIDを確認
id AdminUser
# 出力例: uid=1002(AdminUser) gid=10(admin)

# 2. auth.dbの所有者をUID 1000（コンテナ内のappuser）に変更
sudo chown 1000:1000 /home/AdminUser/nas-project-data/nas-dashboard/auth.db

# 3. ディレクトリの所有者も変更
sudo chown AdminUser:admin /home/AdminUser/nas-project-data/nas-dashboard/

# 4. ディレクトリのパーミッションを755に設定
sudo chmod 755 /home/AdminUser/nas-project-data/nas-dashboard/

# 5. 親ディレクトリのパーミッションも確認
sudo chmod 755 /home/AdminUser/nas-project-data/
```

#### 2. コンテナ内からアクセス確認

```bash
# appuser（UID 1000）として実行してアクセス確認
docker exec -u 1000 doc-automation-web ls -la /nas-project-data/nas-dashboard/auth.db

# SQLiteファイルを読み取りテスト
docker exec -u 1000 doc-automation-web python3 -c "import sqlite3; conn = sqlite3.connect('/nas-project-data/nas-dashboard/auth.db'); print('OK'); conn.close()"
```

#### 3. コンテナを再起動

```bash
cd ~/nas-project/document-automation
docker compose restart web

# ログを確認（Permission deniedエラーが解消されているか確認）
docker logs -f doc-automation-web | grep -i "auth"
```

---

## 🔍 診断手順

### 1. ログイン後のリダイレクト問題の診断

```bash
# ブラウザの開発者ツールで以下を確認
# 1. ログインフォーム送信時にnextパラメータが含まれているか
# 2. サーバーログでnextパラメータが正しく処理されているか
# 3. リダイレクト先のURLが正しいか

# nas-dashboardのログを確認
docker logs -f nas-dashboard | grep -i "next"
```

### 2. 認証チェック問題の診断

```bash
# document-automationのログを確認
docker logs -f doc-automation-web | grep -i "auth"

# ブラウザの開発者ツールで以下を確認
# 1. /statusエンドポイントへのリクエストが正常に返されているか
# 2. ステータスコードが200か、それとも307/302か
# 3. 認証チェックの再試行が無限ループしていないか
```

### 3. 権限エラーの診断

```bash
# ファイル所有者と権限を確認
ls -la /home/AdminUser/nas-project-data/nas-dashboard/auth.db

# ディレクトリの権限を確認
ls -ld /home/AdminUser/nas-project-data/nas-dashboard/

# コンテナ内からアクセス確認
docker exec -u 1000 doc-automation-web ls -la /nas-project-data/nas-dashboard/auth.db
```

---

## 📝 注意事項

### 1. HttpOnly Cookieについて

- `session_id`は`HttpOnly`クッキーとして設定されているため、JavaScriptから読み取れない
- 認証状態の確認は、APIリクエストのレスポンス（HTTPステータスコード）で判断する

### 2. ネットワークエラー（ステータスコード0）について

- ステータスコード0は、ネットワークエラーやCORSエラーを示す
- 無限ループを防ぐため、再試行回数に上限を設定する（推奨: 3回）
- 再試行間隔は1秒以上を推奨

### 3. nextパラメータのセキュリティ

- `next`パラメータは相対パスのみ許可（`/`で始まり、`//`で始まらない）
- 外部URLへのリダイレクトは許可しない（オープンリダイレクト脆弱性を防ぐ）

### 4. ファイル権限について

- コンテナ内のユーザー（`appuser`、UID 1000）がアクセスできるように、ファイル所有者を設定する
- ディレクトリには実行権限（`x`）が必要（ファイルにアクセスするため）

---

## ✅ 確認項目

修正後、以下を確認してください：

1. **ログイン後のリダイレクト**
   - [ ] `/documents`にアクセスしようとすると、ログインページにリダイレクトされる
   - [ ] ログイン後、`/documents`に正しくリダイレクトされる
   - [ ] `next`パラメータが正しく処理されている

2. **認証チェック**
   - [ ] ログアウト後、直接`/documents`にアクセスすると、ログインページにリダイレクトされる
   - [ ] ログイン後、`/documents`にアクセスできる
   - [ ] `/status`エンドポイントが正常に動作する

3. **システムステータス表示**
   - [ ] ドキュメント画面でシステムステータス（バージョン、処理モードなど）が表示される
   - [ ] コンソールにエラーが表示されない
   - [ ] 認証チェックの再試行が無限ループしていない

4. **権限エラー**
   - [ ] ログに`Permission denied`エラーが表示されない
   - [ ] コンテナ内から`auth.db`にアクセスできる

---

## 🔄 関連ファイル

### nas-dashboard
- `nas-dashboard/app.py` - ログイン処理、`require_auth`デコレータ
- `nas-dashboard/templates/login.html` - ログインフォーム
- `nas-dashboard/utils/auth_common.py` - 認証共通関数

### document-automation
- `document-automation/app/api/main.py` - `/status`エンドポイント
- `document-automation/app/templates/index.html` - 認証チェック
- `document-automation/app/static/js/app.js` - システムステータス読み込み

---

## 📚 参考資料

- [Flask セッション管理](https://flask.palletsprojects.com/en/2.3.x/quickstart/#sessions)
- [FastAPI 依存性注入](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [HttpOnly Cookie](https://developer.mozilla.org/ja/docs/Web/HTTP/Cookies#httponly_%E3%82%AF%E3%83%83%E3%82%AD%E3%83%BC)
- [SQLite ファイル権限](https://www.sqlite.org/lockingv3.html)

---

**更新日**: 2025-11-06  
**修正者**: AI Assistant  
**テスト状況**: ✅ すべて解決済み

