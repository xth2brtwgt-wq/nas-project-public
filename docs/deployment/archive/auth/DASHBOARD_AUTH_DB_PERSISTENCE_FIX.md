# 🔧 ダッシュボード認証 データベース永続化の修正

**作成日**: 2025-11-04  
**目的**: 再起動時にデータベースがリセットされる問題の解決

---

## ❌ 問題

再起動のたびにデータベースがリセットされる。

---

## 🔍 原因

データベースパスがコンテナ内の正しいマウントパスと一致していない可能性があります。

現在の設定：
- `utils/auth_db.py`: `/home/AdminUser/nas-project-data/nas-dashboard/auth.db`
- `docker-compose.yml`: `/home/AdminUser/nas-project-data:/nas-project-data:rw`

コンテナ内では `/home/AdminUser` が存在しないため、正しくは `/nas-project-data/nas-dashboard/auth.db` を使用する必要があります。

---

## ✅ 解決方法

### ステップ1: データベースパスの確認

NAS環境で以下を実行して、現在のデータベースファイルの場所を確認：

```bash
cd ~/nas-project/nas-dashboard

# コンテナ内のデータベースパスを確認
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
else:
    print('データベースファイルが見つかりません')
"

# ホスト側のデータベースファイルを確認
ls -la /home/AdminUser/nas-project-data/nas-dashboard/auth.db
```

### ステップ2: データベースパスの修正

`utils/auth_db.py`の`get_db_path()`関数を修正して、コンテナ内の正しいマウントパスを使用するようにします。

修正前：
```python
DB_PATH = Path('/home/AdminUser/nas-project-data/nas-dashboard/auth.db')

def get_db_path():
    """データベースパスを取得（環境に応じて）"""
    if os.getenv('NAS_MODE'):
        return DB_PATH
    else:
        # ローカル環境ではプロジェクトディレクトリに保存
        return Path(__file__).parent.parent / 'data' / 'auth.db'
```

修正後：
```python
def get_db_path():
    """データベースパスを取得（環境に応じて）"""
    if os.getenv('NAS_MODE'):
        # コンテナ内では /nas-project-data としてマウントされている
        return Path('/nas-project-data/nas-dashboard/auth.db')
    else:
        # ローカル環境ではプロジェクトディレクトリに保存
        return Path(__file__).parent.parent / 'data' / 'auth.db'
```

### ステップ3: データベースファイルの移動（既存データがある場合）

既存のデータベースファイルがある場合、新しいパスに移動：

```bash
cd ~/nas-project/nas-dashboard

# 既存のデータベースファイルを確認
ls -la /home/AdminUser/nas-project-data/nas-dashboard/auth.db

# コンテナ内で新しいパスにデータベースファイルが存在するか確認
sudo docker compose exec nas-dashboard ls -la /nas-project-data/nas-dashboard/auth.db

# もしコンテナ内にファイルが存在しない場合、ホスト側のファイルを確認
# （マウントされているので、ホスト側のファイルがそのまま見えるはず）
```

### ステップ4: 修正を適用

1. **ローカル環境で修正**:
   - `nas-dashboard/utils/auth_db.py`を修正
   - Gitにコミット・プッシュ

2. **NAS環境で最新コードを取得**:
   ```bash
   cd ~/nas-project/nas-dashboard
   git pull origin feature/monitoring-fail2ban-integration
   ```

3. **コンテナを再起動**:
   ```bash
   sudo docker compose restart nas-dashboard
   ```

### ステップ5: 動作確認

```bash
cd ~/nas-project/nas-dashboard

# データベースパスを確認
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_db_path
from pathlib import Path

db_path = get_db_path()
print(f'データベースパス: {db_path}')
print(f'データベースファイルが存在するか: {db_path.exists()}')
"

# ユーザー情報を確認
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

### データベースファイルが存在しない場合

ユーザーを再作成：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python /nas-project/nas-dashboard/scripts/create_initial_user.py
```

### パスが正しくない場合

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

