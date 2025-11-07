# 🔍 ダッシュボード認証 ログイン失敗のデバッグ

**作成日**: 2025-11-04  
**目的**: ログイン失敗の原因を特定して修正

---

## ❌ 問題

ログインページは表示されるが、ログインに失敗する：

```
2025-11-04 15:20:17,779 - app - WARNING - ログイン失敗: admin
```

---

## 🔍 デバッグ手順

### ステップ1: データベース内のユーザー情報を確認

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_all_users
import json

users = get_all_users()
print(f'ユーザー数: {len(users)}')
for user in users:
    print(f'  - ID: {user[\"id\"]}')
    print(f'    ユーザー名: {user[\"username\"]}')
    print(f'    パスワードハッシュ: {user[\"password_hash\"][:50]}...')
    print(f'    状態: {\"有効\" if user[\"is_active\"] else \"無効\"}')
    print(f'    作成日時: {user[\"created_at\"]}')
    print()
"
```

### ステップ2: パスワード検証をテスト

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_user_by_username, verify_password

username = 'admin'
password = 'Tsuj!o828'

user = get_user_by_username(username)
if user:
    print(f'ユーザーが見つかりました: {user[\"username\"]}')
    print(f'パスワードハッシュ: {user[\"password_hash\"][:50]}...')
    print(f'状態: {\"有効\" if user[\"is_active\"] else \"無効\"}')
    
    # パスワード検証をテスト
    is_valid = verify_password(password, user['password_hash'])
    print(f'パスワード検証結果: {is_valid}')
else:
    print(f'ユーザーが見つかりません: {username}')
"
```

### ステップ3: ユーザーを再作成

パスワード検証に問題がある場合は、ユーザーを再作成します：

```bash
cd ~/nas-project/nas-dashboard

# 既存のユーザーを削除（データベースから直接）
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_all_users, deactivate_user
import sqlite3
from pathlib import Path
import os

db_path = Path('/home/AdminUser/nas-project-data/nas-dashboard/auth.db')
if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', ('admin',))
    cursor.execute('DELETE FROM sessions')
    conn.commit()
    conn.close()
    print('✅ 既存のユーザーとセッションを削除しました')
else:
    print('❌ データベースファイルが見つかりません')
"

# ユーザーを再作成
sudo docker compose exec nas-dashboard python /nas-project/nas-dashboard/scripts/create_initial_user.py
```

### ステップ4: パスワード検証ロジックを確認

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import hash_password, verify_password

# パスワードをハッシュ化
password = 'Tsuj!o828'
password_hash = hash_password(password)
print(f'パスワードハッシュ: {password_hash[:50]}...')

# パスワード検証をテスト
is_valid = verify_password(password, password_hash)
print(f'パスワード検証結果: {is_valid}')

# 異なるパスワードで検証
is_invalid = verify_password('wrong_password', password_hash)
print(f'間違ったパスワードでの検証結果: {is_invalid}')
"
```

---

## 🔧 修正方法

### 方法1: ユーザーを再作成

```bash
cd ~/nas-project/nas-dashboard

# 既存のユーザーを削除
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
import sqlite3
from pathlib import Path

db_path = Path('/home/AdminUser/nas-project-data/nas-dashboard/auth.db')
if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', ('admin',))
    cursor.execute('DELETE FROM sessions')
    conn.commit()
    conn.close()
    print('✅ 既存のユーザーとセッションを削除しました')
"

# ユーザーを再作成
sudo docker compose exec nas-dashboard python /nas-project/nas-dashboard/scripts/create_initial_user.py
```

### 方法2: パスワードを直接確認

環境変数から直接作成する場合：

```bash
cd ~/nas-project/nas-dashboard

sudo docker compose exec -e DASHBOARD_USERNAME=admin -e DASHBOARD_PASSWORD=Tsuj!o828 nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import init_auth_db, create_user, get_user_by_username, verify_password
import os

# データベースを初期化
init_auth_db()

# 既存のユーザーを確認
username = os.getenv('DASHBOARD_USERNAME', 'admin')
password = os.getenv('DASHBOARD_PASSWORD', 'Tsuj!o828')

existing_user = get_user_by_username(username)
if existing_user:
    print(f'既存のユーザーが見つかりました: {username}')
    # パスワード検証をテスト
    is_valid = verify_password(password, existing_user['password_hash'])
    print(f'パスワード検証結果: {is_valid}')
    
    if not is_valid:
        print('パスワードが一致しません。ユーザーを再作成します...')
        # 既存のユーザーを削除
        import sqlite3
        from pathlib import Path
        db_path = Path('/home/AdminUser/nas-project-data/nas-dashboard/auth.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        
        # ユーザーを再作成
        if create_user(username, password):
            print(f'✅ ユーザー「{username}」を再作成しました')
        else:
            print(f'❌ ユーザーの再作成に失敗しました')
    else:
        print('✅ パスワードは正しいです')
else:
    print(f'ユーザーが見つかりません。作成します...')
    if create_user(username, password):
        print(f'✅ ユーザー「{username}」を作成しました')
    else:
        print(f'❌ ユーザーの作成に失敗しました')
"
```

---

## 📝 確認項目

- [ ] データベース内にユーザーが存在する
- [ ] ユーザーの状態が「有効」になっている
- [ ] パスワード検証が正しく動作する
- [ ] ログインに成功する

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

