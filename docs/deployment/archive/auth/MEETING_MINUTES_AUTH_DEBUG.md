# 🔍 Meeting Minutes BYC 認証モジュール デバッグ手順

**作成日**: 2025-11-04  
**目的**: 認証モジュールが正しく読み込まれているか確認

---

## 🔍 確認手順

### ステップ1: 認証モジュールのインポート確認

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose exec meeting-minutes-byc python -c "
import sys
from pathlib import Path
import logging

# ロガーを初期化
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# パスの確認
nas_dashboard_path = Path('/nas-project/nas-dashboard')
print(f'nas-dashboardパスが存在するか: {nas_dashboard_path.exists()}')
if nas_dashboard_path.exists():
    utils_path = nas_dashboard_path / 'utils'
    print(f'utilsディレクトリが存在するか: {utils_path.exists()}')
    auth_common_path = utils_path / 'auth_common.py'
    print(f'auth_common.pyが存在するか: {auth_common_path.exists()}')
    
    # インポートを試みる
    sys.path.insert(0, str(nas_dashboard_path))
    try:
        from utils.auth_common import get_current_user_from_request, get_dashboard_login_url
        print('✅ 認証モジュールのインポートに成功しました')
        print(f'ログインページURL: {get_dashboard_login_url()}')
    except ImportError as e:
        print(f'❌ 認証モジュールのインポートに失敗しました: {e}')
        import traceback
        traceback.print_exc()
"
```

### ステップ2: アプリケーションログの確認

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose logs meeting-minutes-byc | grep -i "認証\|auth"
```

### ステップ3: 起動時のログを確認

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose logs meeting-minutes-byc | head -50
```

「認証モジュールを読み込みました」または「認証モジュールのパスが見つかりません」というログが表示されるはずです。

---

## 🔧 トラブルシューティング

### 認証モジュールが読み込まれない場合

1. **ファイルの存在確認**:
   ```bash
   sudo docker compose exec meeting-minutes-byc ls -la /nas-project/nas-dashboard/utils/auth_common.py
   ```

2. **パスの確認**:
   ```bash
   sudo docker compose exec meeting-minutes-byc ls -la /nas-project/nas-dashboard/
   ```

3. **マウント設定の確認**:
   ```bash
   cd ~/nas-project/meeting-minutes-byc
   cat docker-compose.yml | grep -A 10 "volumes"
   ```

4. **コンテナを再起動**:
   ```bash
   cd ~/nas-project/meeting-minutes-byc
   sudo docker compose restart meeting-minutes-byc
   ```

### 認証が機能しない場合

1. **環境変数の確認**:
   ```bash
   sudo docker compose exec meeting-minutes-byc env | grep -i "NAS_MODE\|EXTERNAL"
   ```

2. **データベースパスの確認**:
   ```bash
   sudo docker compose exec meeting-minutes-byc python -c "
   from pathlib import Path
   db_path = Path('/nas-project-data/nas-dashboard/auth.db')
   print(f'データベースパス: {db_path}')
   print(f'データベースファイルが存在するか: {db_path.exists()}')
   "
   ```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

