# ✅ ダッシュボード認証ユーザーが見つからない問題の修正

**作成日**: 2025-11-04  
**目的**: ログイン時に「ユーザーが見つかりません」エラーを修正

---

## ❌ 問題

ログイン時に以下のエラーが表示されます：

```
nas-dashboard  | 2025-11-04 16:28:37,783 - app - WARNING - [AUTH] ユーザーが見つかりません: admin
nas-dashboard  | 2025-11-04 16:28:37,783 - app - WARNING - ログイン失敗: admin
```

---

## 🔍 原因

`NAS_MODE`環境変数が設定されていない、またはコンテナ内でDBパスが正しく解決されていない可能性があります。

---

## ✅ 修正手順

### ステップ1: 環境変数を確認

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard env | grep NAS_MODE
```

**期待される出力**:
```
NAS_MODE=true
```

### ステップ2: 実際のDBパスを確認

```bash
sudo docker compose exec nas-dashboard python -c "
import os
from pathlib import Path

print(f'NAS_MODE: {os.getenv(\"NAS_MODE\")}')

if os.getenv('NAS_MODE'):
    db_path = Path('/nas-project-data/nas-dashboard/auth.db')
else:
    db_path = Path('/app/data/auth.db')

print(f'認証DBパス: {db_path}')
print(f'存在するか: {db_path.exists()}')
"
```

### ステップ3: ユーザーの存在確認

```bash
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
    
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    user = cursor.fetchone()
    
    if user:
        print(f'ユーザーが見つかりました: {dict(user)}')
    else:
        print('❌ ユーザーが見つかりません')
    
    # 全ユーザーを確認
    cursor.execute('SELECT * FROM users')
    all_users = cursor.fetchall()
    print(f'全ユーザー数: {len(all_users)}')
    for u in all_users:
        print(f'  - {dict(u)}')
    
    conn.close()
"
```

### ステップ4: 環境変数を設定（必要に応じて）

`docker-compose.yml`に`NAS_MODE=true`が設定されているか確認：

```bash
cd ~/nas-project/nas-dashboard
grep -A 10 "environment:" docker-compose.yml | grep NAS_MODE
```

設定されていない場合は、`docker-compose.yml`を確認して追加してください。

### ステップ5: コンテナを再起動

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose down
sudo docker compose up -d
```

### ステップ6: ユーザーを再作成（必要に応じて）

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
"
```

---

## 🔧 トラブルシューティング

### 環境変数が設定されていない場合

1. **`docker-compose.yml`を確認**:
   ```bash
   cat docker-compose.yml | grep -A 20 "environment:"
   ```

2. **`NAS_MODE=true`を追加**（必要に応じて）:
   ```yaml
   environment:
     - TZ=Asia/Tokyo
     - FLASK_ENV=production
     - NAS_MODE=true
   ```

3. **コンテナを再起動**:
   ```bash
   sudo docker compose down
   sudo docker compose up -d
   ```

### DBパスが間違っている場合

1. **実際のDBパスを確認**:
   ```bash
   sudo docker compose exec nas-dashboard ls -la /nas-project-data/nas-dashboard/auth.db
   ```

2. **ホスト側のDBパスを確認**:
   ```bash
   ls -la /home/AdminUser/nas-project-data/nas-dashboard/auth.db
   ```

3. **マウント設定を確認**:
   ```bash
   cat docker-compose.yml | grep -A 5 "volumes:"
   ```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

