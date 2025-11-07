# 🔧 ダッシュボード認証 ユーザー再作成手順

**作成日**: 2025-11-04  
**目的**: データベース内にユーザーが存在しない場合の再作成手順

---

## ❌ 問題

データベース内にユーザーが存在しない：

```
ユーザー数: 0
ユーザーが見つかりません: admin
```

---

## ✅ 解決方法: ユーザーを再作成

### 方法1: 初期ユーザー作成スクリプトを使用（推奨）

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python /nas-project/nas-dashboard/scripts/create_initial_user.py
```

スクリプトが対話形式でユーザー名とパスワードを尋ねます：

```
認証データベースを初期化しています...
認証データベースを初期化しました

初期ユーザー情報を入力してください
ユーザー名 (デフォルト: admin): 
パスワード: 
```

### 方法2: 環境変数から直接作成

```bash
cd ~/nas-project/nas-dashboard

sudo docker compose exec -e DASHBOARD_USERNAME=admin -e DASHBOARD_PASSWORD=Tsuj!o828 nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import init_auth_db, create_user
import os

# データベースを初期化
init_auth_db()

# ユーザーを作成
username = os.getenv('DASHBOARD_USERNAME', 'admin')
password = os.getenv('DASHBOARD_PASSWORD', 'Tsuj!o828')

if create_user(username, password):
    print(f'✅ ユーザー「{username}」を作成しました')
else:
    print(f'❌ ユーザー「{username}」の作成に失敗しました（既に存在する可能性があります）')
"
```

### 方法3: 既存のユーザーを削除して再作成

```bash
cd ~/nas-project/nas-dashboard

# 既存のユーザーとセッションを削除
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
import sqlite3
from pathlib import Path

db_path = Path('/home/AdminUser/nas-project-data/nas-dashboard/auth.db')
if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users')
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

---

## ✅ 動作確認

### ステップ1: ユーザーが作成されたことを確認

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
    is_valid = verify_password(password, user['password_hash'])
    print(f'パスワード検証結果: {is_valid}')
    if is_valid:
        print('✅ パスワードは正しいです')
    else:
        print('❌ パスワードが一致しません')
else:
    print(f'❌ ユーザーが見つかりません: {username}')
"
```

### ステップ3: ブラウザでログイン

1. ブラウザでアクセス：
   - 外部アクセス: `https://yoshi-nas-sys.duckdns.org:8443/`
   - 内部アクセス: `http://192.168.68.110:9001/`

2. ログインページでログイン：
   - ユーザー名: `admin`
   - パスワード: `Tsuj!o828`

3. ダッシュボードにリダイレクトされることを確認

---

## 📝 確認項目

- [ ] ユーザーが作成されている
- [ ] パスワード検証が成功する
- [ ] ブラウザでログインできる
- [ ] ダッシュボードにリダイレクトされる

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

