# 🔐 ダッシュボード認証統合 実装計画（複数ユーザー対応版）

**作成日**: 2025-11-04  
**目的**: 複数ユーザー対応とユーザー管理画面を含む認証統合の実装計画

---

## 📋 実装内容

### フェーズ1: ダッシュボード側の実装

1. **データベース設計**
   - ユーザーテーブル（`users`）を作成
   - セッションテーブル（`sessions`）を作成
   - 共有SQLiteデータベース（`/home/AdminUser/nas-project-data/nas-dashboard/auth.db`）

2. **ログイン機能**
   - ログインページ（`/login`）を作成
   - ユーザー名とパスワードで認証
   - パスワードハッシュ化（bcrypt）
   - セッションIDを発行してCookieに保存

3. **セッション管理**
   - セッションテーブルにセッション情報を保存
   - セッションタイムアウト機能（30分）
   - ログアウト機能

4. **ユーザー管理画面**
   - ユーザー一覧表示
   - ユーザー追加機能
   - ユーザー編集機能
   - ユーザー削除機能（無効化）
   - パスワード変更機能

5. **各サービスへのリンク**
   - セッションIDをCookieで各サービスに渡す

### フェーズ2: 各サービス側の実装

1. **共通認証モジュールの作成**
   - `auth_middleware.py`を作成
   - セッションID検証機能
   - 共有SQLiteデータベースからセッションを検証

2. **認証ミドルウェアの追加**
   - 各サービスに認証ミドルウェアを追加
   - セッションIDがない、または無効な場合は403エラーを返す

### フェーズ3: Nginx Proxy Managerの設定

1. **Basic認証の削除**
   - トークン認証が正常に動作することを確認後、Basic認証を削除

---

## 📊 データベース設計

### ユーザーテーブル（`users`）

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

### セッションテーブル（`sessions`）

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 🔧 実装の詳細

### 1. ダッシュボード側の実装

#### 依存関係の追加

```python
# requirements.txt
bcrypt==4.0.1
```

#### データベース初期化

```python
# utils/auth_db.py
import sqlite3
import bcrypt
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path('/home/AdminUser/nas-project-data/nas-dashboard/auth.db')

def init_auth_db():
    """認証データベースを初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ユーザーテーブルを作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # セッションテーブルを作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
```

#### ログイン機能

```python
# app.py
from flask import Flask, render_template, request, redirect, url_for, make_response
from utils.auth_db import init_auth_db, get_user_by_username, verify_password, create_session
import uuid
from datetime import datetime, timedelta

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # ユーザーを検索
        user = get_user_by_username(username)
        
        if user and verify_password(password, user['password_hash']) and user['is_active']:
            # セッションIDを発行
            session_id = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(minutes=30)
            create_session(session_id, user['id'], expires_at)
            
            # CookieにセッションIDを保存
            response = redirect(url_for('dashboard'))
            response.set_cookie(
                'session_id',
                session_id,
                secure=True,
                samesite='None',
                httponly=True,
                max_age=1800  # 30分
            )
            return response
        else:
            return render_template('login.html', error='ユーザー名またはパスワードが正しくありません')
    
    return render_template('login.html')
```

#### ユーザー管理画面

```python
# app.py
@app.route('/users', methods=['GET'])
def users_list():
    """ユーザー一覧"""
    # 認証チェック
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    users = get_all_users()
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
def users_add():
    """ユーザー追加"""
    # 認証チェック
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # ユーザーを追加
        create_user(username, password)
        return redirect(url_for('users_list'))
    
    return render_template('users_add.html')

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def users_edit(user_id):
    """ユーザー編集"""
    # 認証チェック
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # ユーザーを更新
        update_user(user_id, username, password)
        return redirect(url_for('users_list'))
    
    user = get_user_by_id(user_id)
    return render_template('users_edit.html', user=user)

@app.route('/users/delete/<int:user_id>', methods=['POST'])
def users_delete(user_id):
    """ユーザー削除（無効化）"""
    # 認証チェック
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    # ユーザーを無効化
    deactivate_user(user_id)
    return redirect(url_for('users_list'))
```

### 2. 共通認証モジュールの作成

```python
# common/auth_middleware.py
import sqlite3
from pathlib import Path
from datetime import datetime
from functools import wraps
from flask import request, jsonify
from fastapi import HTTPException, Depends

DB_PATH = Path('/home/AdminUser/nas-project-data/nas-dashboard/auth.db')

def verify_session(session_id):
    """セッションを検証"""
    if not session_id:
        return None
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, expires_at 
        FROM sessions 
        WHERE session_id = ? AND expires_at > ?
    ''', (session_id, datetime.now()))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]  # user_id
    return None

# Flask用デコレータ
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = request.cookies.get('session_id')
        user_id = verify_session(session_id)
        
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# FastAPI用依存関係
def get_current_user():
    session_id = request.cookies.get('session_id')
    user_id = verify_session(session_id)
    
    if not user_id:
        raise HTTPException(status_code=403, detail='Unauthorized')
    
    return user_id
```

### 3. 各サービス側の実装

#### Flaskアプリケーション（meeting-minutes-byc、youtube-to-notion）

```python
# app.py
from common.auth_middleware import require_auth

@app.route('/')
@require_auth
def index():
    return render_template('index.html')
```

#### FastAPIアプリケーション（amazon-analytics、document-automation、nas-dashboard-monitoring）

```python
# app/api/main.py
from common.auth_middleware import get_current_user
from fastapi import Depends

@app.get('/')
async def index(user_id: int = Depends(get_current_user)):
    return templates.TemplateResponse('index.html', {'request': request})
```

---

## ✅ 実装チェックリスト

### フェーズ1: ダッシュボード側

- [ ] bcryptを`requirements.txt`に追加
- [ ] データベース初期化スクリプトを作成
- [ ] ログインページ（`/login`）を作成
- [ ] ログイン機能を実装
- [ ] セッション管理機能を実装
- [ ] ログアウト機能を実装
- [ ] ユーザー管理画面（`/users`）を作成
- [ ] ユーザー一覧表示機能を実装
- [ ] ユーザー追加機能を実装
- [ ] ユーザー編集機能を実装
- [ ] ユーザー削除機能を実装
- [ ] パスワード変更機能を実装
- [ ] 各サービスへのリンクにセッションIDを追加
- [ ] 初期ユーザーの作成（マイグレーションスクリプト）

### フェーズ2: 各サービス側

- [ ] 共通認証モジュール（`common/auth_middleware.py`）を作成
- [ ] meeting-minutes-bycに認証ミドルウェアを追加
- [ ] amazon-analyticsに認証ミドルウェアを追加
- [ ] nas-dashboard-monitoringに認証ミドルウェアを追加
- [ ] document-automationに認証ミドルウェアを追加
- [ ] youtube-to-notionに認証ミドルウェアを追加

### フェーズ3: Nginx Proxy Manager

- [ ] トークン認証が正常に動作することを確認
- [ ] Basic認証を削除

---

## 📚 参考資料

- [複数ユーザー対応の難易度と実装方法](DASHBOARD_AUTH_MULTI_USER.md)
- [ダッシュボード認証統合の懸念事項](DASHBOARD_AUTH_INTEGRATION_CONCERNS.md)

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

