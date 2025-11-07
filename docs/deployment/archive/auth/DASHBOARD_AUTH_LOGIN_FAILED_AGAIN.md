# 🔍 ダッシュボード認証 ログイン失敗の再発対処

**作成日**: 2025-11-04  
**目的**: ログインが再度失敗する問題の解決

---

## ❌ 問題

ログイン画面で「ユーザー名またはパスワードが正しくありません」と表示される。

---

## 🔍 原因の確認

### ステップ1: データベース内のユーザー情報を確認

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_all_users

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
    print(f'✅ ユーザーが見つかりました: {user[\"username\"]}')
    print(f'パスワードハッシュ: {user[\"password_hash\"][:50]}...')
    print(f'状態: {\"有効\" if user[\"is_active\"] else \"無効\"}')
    
    # パスワード検証をテスト
    is_valid = verify_password(password, user['password_hash'])
    print(f'パスワード検証結果: {is_valid}')
    
    if not is_valid:
        print('❌ パスワード検証に失敗しました')
    else:
        print('✅ パスワード検証に成功しました')
else:
    print(f'❌ ユーザーが見つかりません: {username}')
"
```

### ステップ3: ログを確認

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose logs nas-dashboard | grep -A 5 "ログイン\|AUTH" | tail -30
```

---

## ✅ 解決方法

### 方法1: ユーザーが存在しない場合

ユーザーが存在しない場合は、再作成します：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python /nas-project/nas-dashboard/scripts/create_initial_user.py
```

### 方法2: パスワード検証に失敗する場合

パスワード検証に失敗する場合は、ユーザーを再作成します：

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
else:
    print('❌ データベースファイルが見つかりません')
"

# ユーザーを再作成
sudo docker compose exec nas-dashboard python /nas-project/nas-dashboard/scripts/create_initial_user.py
```

### 方法3: データベースファイルを確認

データベースファイルが正しい場所にあるか確認：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard ls -la /home/AdminUser/nas-project-data/nas-dashboard/
```

`auth.db`ファイルが存在することを確認してください。

### 方法4: データベースを再初期化

データベースを再初期化する場合：

```bash
cd ~/nas-project/nas-dashboard

# データベースファイルを削除（バックアップ推奨）
sudo docker compose exec nas-dashboard bash -c "
if [ -f /home/AdminUser/nas-project-data/nas-dashboard/auth.db ]; then
    cp /home/AdminUser/nas-project-data/nas-dashboard/auth.db /home/AdminUser/nas-project-data/nas-dashboard/auth.db.backup
    rm /home/AdminUser/nas-project-data/nas-dashboard/auth.db
    echo '✅ データベースファイルをバックアップして削除しました'
else
    echo 'データベースファイルが見つかりません'
fi
"

# コンテナを再起動（データベースが自動的に再初期化される）
sudo docker compose restart nas-dashboard

# ユーザーを再作成
sudo docker compose exec nas-dashboard python /nas-project/nas-dashboard/scripts/create_initial_user.py
```

---

## 🔍 トラブルシューティング

### データベースファイルのパスが間違っている場合

`utils/auth_db.py`の`get_db_path()`を確認：

```bash
cd ~/nas-project/nas-dashboard
cat utils/auth_db.py | grep -A 10 "def get_db_path"
```

NAS環境では`/home/AdminUser/nas-project-data/nas-dashboard/auth.db`が正しいパスです。

### コンテナのボリュームマウントを確認

`docker-compose.yml`のボリュームマウントを確認：

```bash
cd ~/nas-project/nas-dashboard
cat docker-compose.yml | grep -A 10 "volumes"
```

`/home/AdminUser/nas-project-data:/nas-project-data:rw`がマウントされていることを確認してください。

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

