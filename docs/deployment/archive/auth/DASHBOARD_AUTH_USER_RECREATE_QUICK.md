# 🔧 ダッシュボード認証 ユーザー再作成（クイックガイド）

**作成日**: 2025-11-04  
**目的**: データベース内にユーザーが存在しない場合の即座の対処

---

## ❌ 問題

データベース内にユーザーが存在しない（ユーザー数: 0）

---

## ✅ 解決方法: ユーザーを再作成

### ステップ1: 初期ユーザー作成スクリプトを実行

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

入力してください：
- **ユーザー名**: `admin`（デフォルトのままEnter）
- **パスワード**: `Tsuj!o828`

### ステップ2: ユーザーが作成されたことを確認

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

### ステップ3: ログインを試行

ブラウザで以下にアクセス：

- 外部アクセス: `https://yoshi-nas-sys.duckdns.org:8443/`
- 内部アクセス: `http://192.168.68.110:9001/`

ログイン情報：
- **ユーザー名**: `admin`
- **パスワード**: `Tsuj!o828`

---

## 🔍 トラブルシューティング

### スクリプトが動作しない場合

環境変数から直接作成：

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

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

