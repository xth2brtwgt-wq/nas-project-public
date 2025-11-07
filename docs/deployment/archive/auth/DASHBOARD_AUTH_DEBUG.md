# 🔍 ダッシュボード認証 デバッグ手順

**作成日**: 2025-11-04  
**目的**: 認証チェックが正しく動作しない場合のデバッグ手順

---

## ❌ 問題: ログインページが表示されず、直接ダッシュボードが開く

### 🔍 原因の可能性

1. **アプリケーションが再起動されていない**
   - 古いコードが実行されている可能性

2. **Cookieに既に`session_id`が保存されている**
   - 以前のセッションが残っている可能性

3. **認証チェックが正しく動作していない**
   - `get_current_user()`が例外を発生させている可能性

---

## ✅ デバッグ手順

### ステップ1: アプリケーションの再起動

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose restart nas-dashboard
```

### ステップ2: ログの確認

```bash
sudo docker compose logs nas-dashboard | tail -50
```

認証関連のログを確認：

```bash
sudo docker compose logs nas-dashboard | grep -i "認証\|auth\|session\|login"
```

### ステップ3: ブラウザのCookieをクリア

1. ブラウザの開発者ツールを開く（F12）
2. 「Application」タブ（Chrome）または「Storage」タブ（Firefox）を開く
3. 「Cookies」を選択
4. `session_id`を削除
5. ページをリロード

または、シークレットモード（プライベートモード）でアクセス

### ステップ4: 認証チェックの動作確認

コンテナ内で認証チェックをテスト：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_all_users, verify_session
from utils.auth_db import init_auth_db

# データベースを初期化
init_auth_db()
print('✅ 認証データベースを初期化しました')

# ユーザー一覧を確認
users = get_all_users()
print(f'ユーザー数: {len(users)}')
for user in users:
    print(f'  - {user[\"username\"]} (ID: {user[\"id\"]}, 状態: {\"有効\" if user[\"is_active\"] else \"無効\"})')
"
```

### ステップ5: セッションの確認

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
import sqlite3
from pathlib import Path

db_path = Path('/home/AdminUser/nas-project-data/nas-dashboard/auth.db')
if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions')
    sessions = cursor.fetchall()
    print(f'アクティブなセッション数: {len(sessions)}')
    for session in sessions:
        print(f'  - Session ID: {session[0]}, User ID: {session[1]}, Expires: {session[3]}')
    conn.close()
else:
    print('❌ データベースファイルが見つかりません')
"
```

---

## 🔧 修正方法

### 方法1: アプリケーションを再ビルドして再起動

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose build
sudo docker compose up -d
```

### 方法2: Cookieをクリアして再テスト

ブラウザのCookieをクリアしてから、再度アクセスしてください。

### 方法3: セッションをクリーンアップ

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import cleanup_expired_sessions
cleanup_expired_sessions()
print('✅ セッションをクリーンアップしました')
"
```

---

## 📝 確認項目

- [ ] アプリケーションが再起動されている
- [ ] ログに認証関連のエラーがない
- [ ] ブラウザのCookieがクリアされている
- [ ] データベースが正常に初期化されている
- [ ] ユーザーが正常に作成されている

---

## 🎯 期待される動作

1. ブラウザでアクセスすると、ログインページが表示される
2. ログインすると、ダッシュボードにリダイレクトされる
3. ログアウトすると、ログインページにリダイレクトされる

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

