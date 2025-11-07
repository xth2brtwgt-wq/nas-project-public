# 🔧 ダッシュボード認証 データベースファイル作成手順

**作成日**: 2025-11-04  
**目的**: 新しいパスにデータベースファイルを作成

---

## ✅ 手順

### ステップ1: ユーザーを再作成

データベースファイルが存在しない場合は、ユーザーを再作成して新しいパスにデータベースファイルを作成します：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python /nas-project/nas-dashboard/scripts/create_initial_user.py
```

入力：
- **ユーザー名**: `admin`（デフォルトのままEnter）
- **パスワード**: `Tsuj!o828`

### ステップ2: データベースファイルの確認

```bash
# ホスト側で確認
ls -la /home/AdminUser/nas-project-data/nas-dashboard/auth.db

# コンテナ内で確認
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard ls -la /nas-project-data/nas-dashboard/auth.db

# データベースパスを確認
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_db_path
from pathlib import Path

db_path = get_db_path()
print(f'データベースパス: {db_path}')
print(f'データベースファイルが存在するか: {db_path.exists()}')
if db_path.exists():
    print(f'データベースファイルサイズ: {db_path.stat().st_size} bytes')
"
```

### ステップ3: ユーザー情報の確認

```bash
cd ~/nas-project/nas-dashboard
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

### ステップ4: 再起動テスト

```bash
cd ~/nas-project/nas-dashboard

# コンテナを再起動
sudo docker compose restart nas-dashboard

# 再起動後、ユーザー情報が残っているか確認
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

