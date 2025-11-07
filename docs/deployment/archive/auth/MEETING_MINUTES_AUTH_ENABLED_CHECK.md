# 🔍 Meeting Minutes BYC AUTH_ENABLED 確認手順

**作成日**: 2025-11-04  
**目的**: AUTH_ENABLEDの状態を確認

---

## 🔍 確認手順

### ステップ1: AUTH_ENABLEDの状態を確認

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose exec meeting-minutes-byc python -c "
import sys
sys.path.insert(0, '/nas-project/meeting-minutes-byc')

# アプリケーションをインポート（モジュールとして）
import importlib.util
spec = importlib.util.spec_from_file_location('app', '/nas-project/meeting-minutes-byc/app.py')
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)

print(f'AUTH_ENABLED: {app_module.AUTH_ENABLED}')
print(f'認証モジュールが読み込まれているか: {hasattr(app_module, \"get_current_user_from_request\")}')
print(f'認証デコレータが存在するか: {hasattr(app_module, \"require_auth\")}')
"
```

### ステップ2: 起動ログを確認

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose logs meeting-minutes-byc | grep -i "認証\|auth\|AUTH_ENABLED" | head -20
```

### ステップ3: 実際のリクエストログを確認

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose logs -f meeting-minutes-byc
```

ブラウザでアクセスして、以下のようなログが表示されるか確認：
```
[AUTH] 認証が必要です: / -> http://192.168.68.110:9001/login
```

---

## 🔧 トラブルシューティング

### AUTH_ENABLEDがFalseの場合

1. **認証モジュールのインポートエラーを確認**:
   ```bash
   sudo docker compose exec meeting-minutes-byc python -c "
   import sys
   from pathlib import Path
   import logging
   
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   
   nas_dashboard_path = Path('/nas-project/nas-dashboard')
   print(f'nas-dashboardパスが存在するか: {nas_dashboard_path.exists()}')
   
   if nas_dashboard_path.exists():
       sys.path.insert(0, str(nas_dashboard_path))
       try:
           from utils.auth_common import get_current_user_from_request, get_dashboard_login_url
           print('✅ 認証モジュールのインポートに成功しました')
       except ImportError as e:
           print(f'❌ 認証モジュールのインポートに失敗しました: {e}')
           import traceback
           traceback.print_exc()
   "
   ```

2. **マウント設定を確認**:
   ```bash
   cd ~/nas-project/meeting-minutes-byc
   cat docker-compose.yml | grep -A 10 "volumes"
   ```

3. **コンテナを再起動**:
   ```bash
   cd ~/nas-project/meeting-minutes-byc
   sudo docker compose restart meeting-minutes-byc
   ```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

