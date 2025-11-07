# ✅ ダッシュボード認証ユーザー存在確認

**作成日**: 2025-11-04  
**目的**: 認証データベース内にユーザーが存在するか確認

---

## ✅ 確認結果

### 環境変数とDBパス
- ✅ NAS_MODE: true
- ✅ 認証DBパス: /nas-project-data/nas-dashboard/auth.db
- ✅ 存在するか: True
- ✅ ファイルサイズ: 32768 bytes

---

## 🔍 ユーザー存在確認

### ステップ1: ユーザーの存在を直接確認

```bash
cd ~/nas-project/nas-dashboard

sudo docker compose exec nas-dashboard python -c "
import os
import sys
from pathlib import Path
import sqlite3

# DBパスを取得
if os.getenv('NAS_MODE'):
    db_path = Path('/nas-project-data/nas-dashboard/auth.db')
else:
    db_path = Path('/app/data/auth.db')

print(f'認証DBパス: {db_path}')
print(f'存在するか: {db_path.exists()}')

if db_path.exists():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # adminユーザーを検索
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    user = cursor.fetchone()
    
    if user:
        print(f'✅ ユーザーが見つかりました:')
        print(f'  - ID: {user[\"id\"]}')
        print(f'  - ユーザー名: {user[\"username\"]}')
        print(f'  - 状態: {\"有効\" if user[\"is_active\"] else \"無効\"}')
        print(f'  - 作成日時: {user[\"created_at\"]}')
        print(f'  - 更新日時: {user[\"updated_at\"]}')
    else:
        print('❌ ユーザーが見つかりません')
    
    # 全ユーザーを確認
    cursor.execute('SELECT * FROM users')
    all_users = cursor.fetchall()
    print(f'\\n全ユーザー数: {len(all_users)}')
    for u in all_users:
        print(f'  - ID: {u[\"id\"]}, ユーザー名: {u[\"username\"]}, 状態: {\"有効\" if u[\"is_active\"] else \"無効\"}')
    
    conn.close()
"
```

### ステップ2: ログイン処理のデバッグ

ログイン時にユーザーが見つからない原因を特定するため、ログイン処理を確認：

```bash
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_user_by_username

# ユーザーを検索
user = get_user_by_username('admin')
if user:
    print(f'✅ get_user_by_username でユーザーが見つかりました:')
    print(f'  - ID: {user[\"id\"]}')
    print(f'  - ユーザー名: {user[\"username\"]}')
    print(f'  - 状態: {\"有効\" if user[\"is_active\"] else \"無効\"}')
else:
    print('❌ get_user_by_username でユーザーが見つかりません')
"
```

### ステップ3: ユーザーを再作成（必要に応じて）

ユーザーが存在しない場合は、再作成：

```bash
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import init_auth_db, create_user, get_all_users

# データベースを初期化
init_auth_db()
print('✅ データベースを初期化しました')

# 既存のユーザーを確認
existing_users = get_all_users()
print(f'既存のユーザー数: {len(existing_users)}')

# 初期ユーザーを作成
username = 'admin'
password = 'Tsuj!o828'
if create_user(username, password):
    print(f'✅ ユーザー「{username}」を作成しました')
else:
    print(f'❌ ユーザー「{username}」の作成に失敗しました（既に存在する可能性があります）')
    
# 作成後のユーザーを確認
final_users = get_all_users()
print(f'\\n最終ユーザー数: {len(final_users)}')
for u in final_users:
    print(f'  - {u[\"username\"]} (ID: {u[\"id\"]}, 状態: {\"有効\" if u[\"is_active\"] else \"無効\"})')
"
```

---

## 🔧 トラブルシューティング

### ユーザーが存在しない場合

1. **データベースを初期化**:
   ```bash
   sudo docker compose exec nas-dashboard python -c "
   import sys
   sys.path.insert(0, '/nas-project/nas-dashboard')
   from utils.auth_db import init_auth_db
   init_auth_db()
   print('✅ データベースを初期化しました')
   "
   ```

2. **ユーザーを作成**:
   ```bash
   sudo docker compose exec nas-dashboard python -c "
   import sys
   sys.path.insert(0, '/nas-project/nas-dashboard')
   from utils.auth_db import create_user
   
   if create_user('admin', 'Tsuj!o828'):
       print('✅ ユーザーを作成しました')
   else:
       print('❌ ユーザーの作成に失敗しました')
   "
   ```

### get_user_by_username でユーザーが見つからない場合

`utils/auth_db.py`の`get_user_by_username`関数を確認する必要があります。DBパスが正しく解決されているか確認してください。

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

