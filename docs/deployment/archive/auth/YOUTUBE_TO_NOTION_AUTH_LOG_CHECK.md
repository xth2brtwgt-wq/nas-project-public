# ✅ YouTube to Notion 認証機能 ログ確認

**作成日**: 2025-11-04  
**目的**: 認証モジュールの読み込みログが表示されない問題を確認

---

## ❌ 問題

起動ログに認証関連のメッセージが表示されていません：

```
youtube-to-notion  | 2025-11-04 17:10:59,344 - __main__ - INFO - [INIT] SUBFOLDER_PATH from env: /youtube
youtube-to-notion  | 2025-11-04 17:10:59,345 - __main__ - INFO - [INIT] APPLICATION_ROOT set to: /youtube
youtube-to-notion  | 2025-11-04 17:10:59,345 - __main__ - INFO - [INIT] SESSION_COOKIE_PATH set to: /youtube
```

**期待されるログ**:
```
認証モジュールを読み込みました
```

または

```
認証モジュールのパスが見つかりません（認証機能は無効化されます）
```

---

## ✅ 確認手順

### ステップ1: コンテナ内で認証モジュールのパスを確認

```bash
cd ~/nas-project/youtube-to-notion

sudo docker compose exec youtube-to-notion python -c "
import sys
from pathlib import Path

# パスの確認
nas_dashboard_path = Path('/nas-project/nas-dashboard')
print(f'1. nas-dashboardパスが存在するか: {nas_dashboard_path.exists()}')

if nas_dashboard_path.exists():
    auth_common_path = nas_dashboard_path / 'utils' / 'auth_common.py'
    print(f'2. auth_common.pyパスが存在するか: {auth_common_path.exists()}')
    print(f'3. auth_common.pyフルパス: {auth_common_path}')
    
    # ファイルの内容を確認（最初の数行）
    if auth_common_path.exists():
        with open(auth_common_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:5]
            print(f'4. auth_common.pyの最初の5行:')
            for i, line in enumerate(lines, 1):
                print(f'   {i}: {line.strip()}')
else:
    print('❌ nas-dashboardパスが見つかりません')
    
    # 代替パスを確認
    alternative_paths = [
        Path('/nas-project'),
        Path('/home/AdminUser/nas-project/nas-dashboard'),
    ]
    for alt_path in alternative_paths:
        print(f'  代替パス {alt_path} が存在するか: {alt_path.exists()}')
"
```

### ステップ2: 認証モジュールのインポートをテスト

```bash
sudo docker compose exec youtube-to-notion python -c "
import sys
import importlib.util
from pathlib import Path

nas_dashboard_path = Path('/nas-project/nas-dashboard')
auth_common_path = nas_dashboard_path / 'utils' / 'auth_common.py'

if auth_common_path.exists():
    try:
        # 認証モジュールをインポート
        spec = importlib.util.spec_from_file_location('auth_common', str(auth_common_path))
        auth_common = importlib.util.module_from_spec(spec)
        
        # sys.pathに追加
        sys.path.insert(0, str(nas_dashboard_path))
        
        # モジュールを実行
        spec.loader.exec_module(auth_common)
        
        print('✅ 認証モジュールのインポートに成功しました')
        print(f'   get_current_user_from_request: {hasattr(auth_common, \"get_current_user_from_request\")}')
        print(f'   get_dashboard_login_url: {hasattr(auth_common, \"get_dashboard_login_url\")}')
    except Exception as e:
        print(f'❌ 認証モジュールのインポートに失敗しました: {e}')
        import traceback
        traceback.print_exc()
else:
    print('❌ auth_common.pyが見つかりません')
"
```

### ステップ3: アプリケーションの起動ログ全体を確認

```bash
sudo docker compose logs youtube-to-notion --tail 100 | grep -E "認証|auth|AUTH|警告|WARNING|エラー|ERROR"
```

### ステップ4: 直接アクセスして認証を確認

```bash
# ヘルスチェック（認証不要）
curl http://localhost:8111/health

# ルートエンドポイント（認証必要）
curl -v http://localhost:8111/
```

**期待される動作**:
- ヘルスチェックは正常に応答する（認証不要）
- ルートエンドポイントはログインページにリダイレクトされる（認証必要）

---

## 🔧 トラブルシューティング

### 認証モジュールが見つからない場合

1. **マウント設定を再確認**:
   ```bash
   sudo docker inspect youtube-to-notion | grep -A 30 "Mounts" | grep -E "nas-project|Source|Destination"
   ```

2. **コンテナを完全再起動**:
   ```bash
   sudo docker compose down
   sudo docker compose up -d
   ```

### 認証モジュールのインポートに失敗する場合

1. **エラーログを確認**:
   ```bash
   sudo docker compose logs youtube-to-notion | grep -i "error\|exception\|traceback"
   ```

2. **認証モジュールの依存関係を確認**:
   ```bash
   sudo docker compose exec youtube-to-notion python -c "
   import sys
   sys.path.insert(0, '/nas-project/nas-dashboard')
   try:
       from utils.auth_db import verify_session
       print('✅ auth_dbモジュールのインポートに成功しました')
   except Exception as e:
       print(f'❌ auth_dbモジュールのインポートに失敗しました: {e}')
   "
   ```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

