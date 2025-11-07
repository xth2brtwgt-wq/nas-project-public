# 🔧 ダッシュボード認証 スクリプト実行エラー修正

**作成日**: 2025-11-04  
**目的**: 初期ユーザー作成スクリプトの実行エラー修正

---

## ❌ エラー内容

```bash
python: can't open file '/app/scripts/create_initial_user.py': [Errno 2] No such file or directory
```

## 🔍 原因

スクリプトファイルがコンテナ内にコピーされていない、またはパスが間違っている可能性があります。

## ✅ 解決方法

### 方法1: プロジェクトディレクトリから実行（推奨）

NAS環境では、プロジェクトディレクトリがマウントされているため、直接実行できます：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python /nas-project/nas-dashboard/scripts/create_initial_user.py
```

### 方法2: コンテナ内で直接実行

コンテナ内に入って実行：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard bash
```

コンテナ内で：

```bash
cd /nas-project/nas-dashboard
python scripts/create_initial_user.py
exit
```

### 方法3: Pythonコマンドで直接実行

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from scripts.create_initial_user import main
main()
"
```

### 方法4: 環境変数から直接作成（最も簡単）

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import init_auth_db, create_user
import os

# データベースを初期化
init_auth_db()
print('認証データベースを初期化しました')

# 初期ユーザーを作成
username = os.getenv('DASHBOARD_USERNAME', 'admin')
password = os.getenv('DASHBOARD_PASSWORD', 'admin123')

if create_user(username, password):
    print(f'初期ユーザー「{username}」を作成しました')
else:
    print(f'ユーザー「{username}」の作成に失敗しました（既に存在する可能性があります）')
"
```

または、環境変数を設定してから実行：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec -e DASHBOARD_USERNAME=admin -e DASHBOARD_PASSWORD=your-password nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import init_auth_db, create_user
import os

init_auth_db()
username = os.getenv('DASHBOARD_USERNAME', 'admin')
password = os.getenv('DASHBOARD_PASSWORD', 'admin123')

if create_user(username, password):
    print(f'初期ユーザー「{username}」を作成しました')
else:
    print(f'ユーザー「{username}」の作成に失敗しました')
"
```

---

## 📝 推奨手順

最も簡単な方法は、方法4（環境変数から直接作成）です：

```bash
cd ~/nas-project/nas-dashboard

# 環境変数を設定して初期ユーザーを作成
sudo docker compose exec -e DASHBOARD_USERNAME=admin -e DASHBOARD_PASSWORD=your-password nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import init_auth_db, create_user
import os

init_auth_db()
username = os.getenv('DASHBOARD_USERNAME', 'admin')
password = os.getenv('DASHBOARD_PASSWORD', 'admin123')

if create_user(username, password):
    print(f'✅ 初期ユーザー「{username}」を作成しました')
else:
    print(f'❌ ユーザー「{username}」の作成に失敗しました（既に存在する可能性があります）')
"
```

**`your-password`を実際のパスワードに置き換えてください。**

---

## ✅ 動作確認

初期ユーザー作成後、ログを確認：

```bash
sudo docker compose logs nas-dashboard | grep -i "認証"
```

ブラウザでアクセスしてログインできることを確認：

- **内部アクセス**: `http://192.168.68.110:9001/`
- **外部アクセス**: `https://yoshi-nas-sys.duckdns.org:8443/`

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

