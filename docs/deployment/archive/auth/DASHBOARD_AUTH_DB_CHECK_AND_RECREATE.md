# ✅ ダッシュボード認証DB確認と再作成

**作成日**: 2025-11-04  
**目的**: 認証データベースの状態を確認し、必要に応じてユーザーを再作成

---

## 🔍 確認手順

### ステップ1: 認証DBファイルの存在確認

```bash
# ホスト側で確認
ls -la /home/AdminUser/nas-project-data/nas-dashboard/auth.db

# または、コンテナ内で確認
sudo docker compose exec nas-dashboard ls -la /nas-project-data/nas-dashboard/auth.db
```

### ステップ2: 認証DBのパス確認

```bash
sudo docker compose exec nas-dashboard python -c "
import os
from pathlib import Path

if os.getenv('NAS_MODE'):
    db_path = Path('/nas-project-data/nas-dashboard/auth.db')
else:
    db_path = Path('/app/data/auth.db')

print(f'認証DBパス: {db_path}')
print(f'存在するか: {db_path.exists()}')
"
```

### ステップ3: ユーザー数の確認

```bash
sudo docker compose exec nas-dashboard python -c "
import sys
from pathlib import Path

# パスを設定
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_all_users

users = get_all_users()
print(f'ユーザー数: {len(users)}')
for user in users:
    print(f'  - {user[\"username\"]} (ID: {user[\"id\"]}, 状態: {\"有効\" if user[\"is_active\"] else \"無効\"})')
"
```

### ステップ4: ユーザーが存在しない場合

ユーザーが存在しない場合、初期ユーザーを作成します：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python /nas-project/nas-dashboard/scripts/create_initial_user.py
```

または、環境変数を使用：

```bash
sudo docker compose exec nas-dashboard bash -c "DASHBOARD_USERNAME=admin DASHBOARD_PASSWORD='Tsuj!o828' python /nas-project/nas-dashboard/scripts/create_initial_user.py"
```

---

## 🔧 トラブルシューティング

### データベースファイルが存在しない場合

1. **データベースを初期化**:
   ```bash
   sudo docker compose exec nas-dashboard python -c "
   import sys
   sys.path.insert(0, '/nas-project/nas-dashboard')
   from utils.auth_db import init_auth_db
   init_auth_db()
   print('✅ 認証データベースを初期化しました')
   "
   ```

2. **初期ユーザーを作成**:
   ```bash
   sudo docker compose exec nas-dashboard python /nas-project/nas-dashboard/scripts/create_initial_user.py
   ```

### データベースファイルのパスが間違っている場合

1. **正しいパスを確認**:
   ```bash
   sudo docker compose exec nas-dashboard python -c "
   import os
   from pathlib import Path
   
   if os.getenv('NAS_MODE'):
       db_path = Path('/nas-project-data/nas-dashboard/auth.db')
   else:
       db_path = Path('/app/data/auth.db')
   
   print(f'認証DBパス: {db_path}')
   print(f'NAS_MODE: {os.getenv(\"NAS_MODE\")}')
   "
   ```

2. **環境変数を確認**:
   ```bash
   sudo docker compose exec nas-dashboard env | grep NAS_MODE
   ```

### データベースファイルの権限問題

1. **ファイルの権限を確認**:
   ```bash
   ls -la /home/AdminUser/nas-project-data/nas-dashboard/auth.db
   ```

2. **権限を修正**:
   ```bash
   sudo chmod 644 /home/AdminUser/nas-project-data/nas-dashboard/auth.db
   sudo chown AdminUser:AdminUser /home/AdminUser/nas-project-data/nas-dashboard/auth.db
   ```

---

## 📝 クイックコマンド

### 認証DBの状態を一括確認

```bash
cd ~/nas-project/nas-dashboard
echo "=== 認証DBパス確認 ==="
sudo docker compose exec nas-dashboard python -c "
import os
from pathlib import Path

if os.getenv('NAS_MODE'):
    db_path = Path('/nas-project-data/nas-dashboard/auth.db')
else:
    db_path = Path('/app/data/auth.db')

print(f'認証DBパス: {db_path}')
print(f'存在するか: {db_path.exists()}')
if db_path.exists():
    print(f'ファイルサイズ: {db_path.stat().st_size} bytes')
"

echo ""
echo "=== ユーザー数確認 ==="
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_all_users

users = get_all_users()
print(f'ユーザー数: {len(users)}')
for user in users:
    print(f'  - {user[\"username\"]} (ID: {user[\"id\"]}, 状態: {\"有効\" if user[\"is_active\"] else \"無効\"})')
"
```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

