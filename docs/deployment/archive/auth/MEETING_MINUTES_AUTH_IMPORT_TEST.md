# 🔍 Meeting Minutes BYC 認証モジュール インポートテスト

**作成日**: 2025-11-04  
**目的**: 認証モジュールが正しくインポートされているか確認

---

## 🔍 確認手順

### ステップ1: 起動ログを確認

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose logs meeting-minutes-byc | grep -i "認証\|auth\|AUTH_ENABLED\|読み込み" | head -20
```

### ステップ2: 実際にインポートをテスト

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
    sys.path.insert(0, str(nas_dashboard_path))
    try:
        from utils.auth_common import get_current_user_from_request, get_dashboard_login_url
        print('✅ 認証モジュールのインポートに成功しました')
        print(f'ログインページURL: {get_dashboard_login_url()}')
    except ImportError as e:
        print(f'❌ 認証モジュールのインポートに失敗しました: {e}')
        import traceback
        traceback.print_exc()
else:
    print('❌ nas-dashboardパスが見つかりません')
"
```

### ステップ3: 実際のリクエストログを確認

別ターミナルで以下を実行：

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose logs -f meeting-minutes-byc
```

ブラウザで直接アクセスして、以下のようなログが表示されるか確認：

```
[AUTH] 認証が必要です: / -> http://192.168.68.110:9001/login
```

---

## 🔧 トラブルシューティング

### 認証モジュールがインポートできない場合

1. **auth_common.pyの依存関係を確認**:
   ```bash
   sudo docker compose exec meeting-minutes-byc python -c "
   import sys
   sys.path.insert(0, '/nas-project/nas-dashboard')
   import utils.auth_common
   "
   ```

2. **コンテナを再起動**:
   ```bash
   cd ~/nas-project/meeting-minutes-byc
   sudo docker compose restart meeting-minutes-byc
   ```

3. **完全な再ビルド**:
   ```bash
   cd ~/nas-project/meeting-minutes-byc
   sudo docker compose down
   sudo docker compose build --no-cache
   sudo docker compose up -d
   ```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

