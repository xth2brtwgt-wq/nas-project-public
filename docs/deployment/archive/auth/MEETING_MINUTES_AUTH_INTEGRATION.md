# 🔐 Meeting Minutes BYC 認証統合手順

**作成日**: 2025-11-04  
**目的**: `meeting-minutes-byc`にダッシュボード認証を統合

---

## 📋 実装内容

### 1. Docker Compose設定の更新

`docker-compose.yml`に認証データベースのマウントを追加：

```yaml
volumes:
  # 既存のマウント
  - /home/AdminUser/nas-project-data/meeting-minutes-byc/uploads:/app/uploads
  - /home/AdminUser/nas-project-data/meeting-minutes-byc/transcripts:/app/transcripts
  - /home/AdminUser/nas-project-data/meeting-minutes-byc/logs:/app/logs
  # 認証データベースのマウント（追加）
  - /home/AdminUser/nas-project-data:/nas-project-data:ro
```

### 2. 認証ミドルウェアの追加

`app.py`に認証機能を追加：

```python
# 共通認証モジュールのインポート
import sys
from pathlib import Path

# nas-dashboardのutilsディレクトリをパスに追加
nas_dashboard_path = Path('/nas-project/nas-dashboard')
if nas_dashboard_path.exists():
    sys.path.insert(0, str(nas_dashboard_path))

from utils.auth_common import get_current_user_from_request, get_dashboard_login_url
from functools import wraps
from flask import redirect

# 認証デコレータ
def require_auth(f):
    """認証が必要なエンドポイントのデコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user_from_request(request)
        if not user:
            # ログインページにリダイレクト
            login_url = get_dashboard_login_url()
            return redirect(login_url)
        return f(*args, **kwargs)
    return decorated_function
```

### 3. ルートへの認証適用

認証が必要なルートにデコレータを追加：

```python
@app.route('/')
@require_auth
def index():
    """メインページ"""
    # ...

@app.route('/history')
@require_auth
def get_history():
    """履歴取得"""
    # ...

# 認証不要なエンドポイント
@app.route('/health')
def health():
    """ヘルスチェック（認証不要）"""
    # ...
```

---

## 🔍 認証不要なエンドポイント

以下のエンドポイントは認証不要：

- `/health`: ヘルスチェック
- `/static/*`: 静的ファイル
- `/socket.io/*`: WebSocket（必要に応じて認証を追加）

---

## ✅ 動作確認

1. 未認証でアクセスした場合、ダッシュボードのログインページにリダイレクトされる
2. ログイン後、サービスにアクセスできる
3. セッション期限切れの場合、ログインページにリダイレクトされる

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

