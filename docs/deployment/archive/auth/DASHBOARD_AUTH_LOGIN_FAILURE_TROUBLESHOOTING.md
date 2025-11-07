# ✅ ダッシュボード認証ログイン失敗のトラブルシューティング

**作成日**: 2025-11-04  
**目的**: ログイン失敗の原因を特定し、修正する

---

## ✅ 確認結果

- ✅ 認証DBファイルは存在する（32KB）
- ✅ ユーザーは存在する（`admin`, ID: 1, 状態: 有効）

それでも「ユーザー名またはパスワードが正しくありません」と表示される場合、以下の可能性があります：

---

## 🔍 トラブルシューティング手順

### ステップ1: ダッシュボードコンテナを再起動

最新のコード（`path='/'`の設定を含む）を反映させるため、コンテナを再起動：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose down
sudo docker compose up -d
```

### ステップ2: パスワードを再設定

パスワードハッシュが正しく保存されていない可能性があるため、パスワードを再設定：

```bash
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_user_by_username, update_user, verify_password

# ユーザーを取得
user = get_user_by_username('admin')
if user:
    print(f'ユーザーが見つかりました: {user[\"username\"]} (ID: {user[\"id\"]})')
    
    # パスワードを再設定
    new_password = 'Tsuj!o828'
    if update_user(user['id'], password=new_password):
        print(f'✅ パスワードを再設定しました')
    else:
        print(f'❌ パスワードの再設定に失敗しました')
else:
    print(f'❌ ユーザーが見つかりません')
"
```

### ステップ3: パスワード検証をテスト

```bash
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_user_by_username, verify_password

# ユーザーを取得
user = get_user_by_username('admin')
if user:
    print(f'ユーザー: {user[\"username\"]}')
    print(f'パスワードハッシュ: {user[\"password_hash\"][:50]}...')
    
    # パスワード検証をテスト
    test_password = 'Tsuj!o828'
    is_valid = verify_password(test_password, user['password_hash'])
    print(f'パスワード検証結果: {\"✅ 正しい\" if is_valid else \"❌ 間違っている\"}')
else:
    print(f'❌ ユーザーが見つかりません')
"
```

### ステップ4: ブラウザのCookieをクリア

1. ブラウザの開発者ツール（F12）を開く
2. **Application**タブを開く
3. **Cookies**を選択
4. **`yoshi-nas-sys.duckdns.org`**を選択
5. すべてのCookieを削除
6. ページを再読み込み

または、シークレットモード（プライベートモード）でアクセス

### ステップ5: ログインを再試行

1. `https://yoshi-nas-sys.duckdns.org:8443` にアクセス
2. ユーザー名: `admin`
3. パスワード: `Tsuj!o828`
4. ログインを試行

---

## 🔧 パスワードが正しくない場合

### ユーザーを再作成

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

## 📝 クイックコマンド（一括実行）

```bash
cd ~/nas-project/nas-dashboard

# 1. コンテナを再起動
echo "=== コンテナを再起動 ==="
sudo docker compose down
sudo docker compose up -d

# 2. パスワードを再設定
echo ""
echo "=== パスワードを再設定 ==="
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_user_by_username, update_user

user = get_user_by_username('admin')
if user:
    if update_user(user['id'], password='Tsuj!o828'):
        print('✅ パスワードを再設定しました')
    else:
        print('❌ パスワードの再設定に失敗しました')
else:
    print('❌ ユーザーが見つかりません')
"

# 3. パスワード検証をテスト
echo ""
echo "=== パスワード検証をテスト ==="
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import get_user_by_username, verify_password

user = get_user_by_username('admin')
if user:
    is_valid = verify_password('Tsuj!o828', user['password_hash'])
    print(f'パスワード検証結果: {\"✅ 正しい\" if is_valid else \"❌ 間違っている\"}')
else:
    print('❌ ユーザーが見つかりません')
"
```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

