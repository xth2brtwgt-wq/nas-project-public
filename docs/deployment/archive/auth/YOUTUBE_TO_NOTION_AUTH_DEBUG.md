# ✅ YouTube to Notion 認証機能 デバッグ

**作成日**: 2025-11-04  
**目的**: 認証モジュールが読み込まれない問題を解決

---

## ❌ 問題

ログに「認証モジュールを読み込みました」が表示されず、直接アクセスしても画面が表示されてしまいます。

---

## 🔍 デバッグ手順

### ステップ1: コンテナ内でパスの存在を確認

```bash
cd ~/nas-project/youtube-to-notion

sudo docker compose exec youtube-to-notion python -c "
import sys
from pathlib import Path

# パスの確認
nas_dashboard_path = Path('/nas-project/nas-dashboard')
print(f'nas-dashboardパスが存在するか: {nas_dashboard_path.exists()}')

if nas_dashboard_path.exists():
    auth_common_path = nas_dashboard_path / 'utils' / 'auth_common.py'
    print(f'auth_common.pyパスが存在するか: {auth_common_path.exists()}')
    print(f'auth_common.pyフルパス: {auth_common_path}')
else:
    print('❌ nas-dashboardパスが見つかりません')
    print(f'現在のパス: {Path.cwd()}')
    print(f'ルートディレクトリの内容: {list(Path(\"/\").iterdir())}')
"
```

### ステップ2: マウント設定を確認

```bash
sudo docker compose exec youtube-to-notion mount | grep nas-project
```

### ステップ3: 環境変数を確認

```bash
sudo docker compose exec youtube-to-notion env | grep NAS_MODE
```

### ステップ4: 認証モジュールのインポートをテスト

```bash
sudo docker compose exec youtube-to-notion python -c "
import sys
import importlib.util
from pathlib import Path

# パスの確認
nas_dashboard_path = Path('/nas-project/nas-dashboard')
print(f'nas-dashboardパスが存在するか: {nas_dashboard_path.exists()}')

if nas_dashboard_path.exists():
    sys.path.insert(0, str(nas_dashboard_path))
    try:
        auth_common_path = nas_dashboard_path / 'utils' / 'auth_common.py'
        if auth_common_path.exists():
            spec = importlib.util.spec_from_file_location('auth_common', str(auth_common_path))
            auth_common = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(auth_common)
            print('✅ 認証モジュールのインポートに成功しました')
            print(f'get_current_user_from_request: {hasattr(auth_common, \"get_current_user_from_request\")}')
            print(f'get_dashboard_login_url: {hasattr(auth_common, \"get_dashboard_login_url\")}')
        else:
            print(f'❌ 認証モジュールファイルが見つかりません: {auth_common_path}')
    except Exception as e:
        print(f'❌ 認証モジュールのインポートに失敗しました: {e}')
        import traceback
        traceback.print_exc()
else:
    print('❌ nas-dashboardパスが見つかりません')
"
```

---

## 🔧 トラブルシューティング

### パスが存在しない場合

1. **docker-compose.ymlのマウント設定を確認**:
   ```bash
   cat docker-compose.yml | grep -A 5 "volumes:"
   ```

2. **コンテナを再起動**:
   ```bash
   sudo docker compose down
   sudo docker compose up -d
   ```

### 認証モジュールのインポートに失敗する場合

1. **ログを確認**:
   ```bash
   sudo docker compose logs youtube-to-notion | grep -i "認証\|auth"
   ```

2. **コンテナを完全再ビルド**:
   ```bash
   sudo docker compose down
   sudo docker compose build --no-cache
   sudo docker compose up -d
   ```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

