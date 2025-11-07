# 🔧 ダッシュボード認証 データベース移行手順

**作成日**: 2025-11-04  
**目的**: データベースパス変更後のデータ移行

---

## ❌ 問題

データベースパスを変更した後、データベースファイルが見つからない。

---

## ✅ 解決方法

### ステップ1: ホスト側のデータベースファイルを確認

```bash
# ホスト側のデータベースファイルを確認
ls -la /home/AdminUser/nas-project-data/nas-dashboard/auth.db

# ディレクトリが存在するか確認
ls -la /home/AdminUser/nas-project-data/nas-dashboard/
```

### ステップ2: コンテナ内のマウントパスを確認

```bash
cd ~/nas-project/nas-dashboard

# コンテナ内でマウントされているか確認
sudo docker compose exec nas-dashboard ls -la /nas-project-data/nas-dashboard/
```

### ステップ3: データベースディレクトリを作成（必要に応じて）

```bash
# ホスト側でディレクトリを作成
mkdir -p /home/AdminUser/nas-project-data/nas-dashboard
chmod 755 /home/AdminUser/nas-project-data/nas-dashboard
```

### ステップ4: ユーザーを再作成

データベースファイルが存在しない場合は、ユーザーを再作成：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python /nas-project/nas-dashboard/scripts/create_initial_user.py
```

入力：
- **ユーザー名**: `admin`（デフォルトのままEnter）
- **パスワード**: `Tsuj!o828`

### ステップ5: データベースファイルの確認

```bash
cd ~/nas-project/nas-dashboard

# ホスト側で確認
ls -la /home/AdminUser/nas-project-data/nas-dashboard/auth.db

# コンテナ内で確認
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

### ステップ6: 再起動テスト

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

## 🔍 トラブルシューティング

### データベースファイルが作成されない場合

1. **ディレクトリの権限を確認**:
   ```bash
   ls -la /home/AdminUser/nas-project-data/nas-dashboard/
   ```

2. **ディレクトリの権限を修正**:
   ```bash
   chmod 755 /home/AdminUser/nas-project-data/nas-dashboard
   ```

3. **コンテナを再起動**:
   ```bash
   cd ~/nas-project/nas-dashboard
   sudo docker compose restart nas-dashboard
   ```

### マウントが正しく機能していない場合

`docker-compose.yml`のボリュームマウントを確認：

```bash
cd ~/nas-project/nas-dashboard
cat docker-compose.yml | grep -A 5 "volumes"
```

`/home/AdminUser/nas-project-data:/nas-project-data:rw` がマウントされていることを確認してください。

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

