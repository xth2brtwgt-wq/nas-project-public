# 🔍 ドキュメント自動処理システム・モニタリング画面 認証パス確認

**作成日**: 2025-11-04  
**目的**: `document-automation`と`nas-dashboard-monitoring`の認証モジュールパスを確認

---

## ❌ 問題

完全再起動後も両方のサービスがHTTP 200を返しており、認証リダイレクトが機能していません。
起動ログに「認証モジュールを読み込みました」というログが表示されていません。

---

## 🔍 確認手順

### ステップ1: 起動ログ全体を確認

```bash
# document-automation
cd ~/nas-project/document-automation
sudo docker compose logs web | tail -50

# nas-dashboard-monitoring
cd ~/nas-project/nas-dashboard-monitoring
sudo docker compose logs backend | tail -50
```

**確認ポイント**:
- "認証モジュールを読み込みました" が表示されているか
- "認証モジュールのパスが見つかりません" という警告が出ているか
- "認証モジュールファイルが見つかりません" という警告が出ているか
- "認証モジュールをインポートできませんでした" というエラーが出ているか

### ステップ2: コンテナ内でパスを確認

```bash
# document-automation
sudo docker exec doc-automation-web ls -la /nas-project/nas-dashboard/utils/auth_common.py

# nas-dashboard-monitoring
sudo docker exec nas-dashboard-monitoring-backend-1 ls -la /nas-project/nas-dashboard/utils/auth_common.py
```

**期待される結果**:
```
-rw-r--r-- 1 root root 12345 ... /nas-project/nas-dashboard/utils/auth_common.py
```

**問題の可能性**:
- `ls: cannot access ...` というエラー → マウント設定の問題
- ファイルが存在しない → マウント設定の問題

### ステップ3: マウント設定を確認

```bash
# document-automation
cd ~/nas-project/document-automation
sudo docker inspect doc-automation-web | grep -A 10 "Mounts"

# nas-dashboard-monitoring
cd ~/nas-project/nas-dashboard-monitoring
sudo docker inspect nas-dashboard-monitoring-backend-1 | grep -A 10 "Mounts"
```

**期待される設定**:
```json
{
  "Source": "/home/AdminUser/nas-project/nas-dashboard",
  "Destination": "/nas-project/nas-dashboard",
  ...
}
```

### ステップ4: Pythonで直接インポートをテスト

```bash
# document-automation
sudo docker exec doc-automation-web python -c "
import sys
from pathlib import Path

# パスを確認
nas_dashboard_path = Path('/nas-project/nas-dashboard')
print(f'nas_dashboard_path exists: {nas_dashboard_path.exists()}')
print(f'nas_dashboard_path is_dir: {nas_dashboard_path.is_dir()}')

auth_common_path = nas_dashboard_path / 'utils' / 'auth_common.py'
print(f'auth_common_path exists: {auth_common_path.exists()}')

if auth_common_path.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location('auth_common', str(auth_common_path))
    print(f'spec loaded: {spec is not None}')
    if spec:
        auth_common = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auth_common)
        print(f'auth_common loaded: {auth_common is not None}')
        print(f'get_current_user_from_request: {hasattr(auth_common, \"get_current_user_from_request\")}')
        print(f'get_dashboard_login_url: {hasattr(auth_common, \"get_dashboard_login_url\")}')
"

# nas-dashboard-monitoring
sudo docker exec nas-dashboard-monitoring-backend-1 python -c "
import sys
from pathlib import Path

# パスを確認
nas_dashboard_path = Path('/nas-project/nas-dashboard')
print(f'nas_dashboard_path exists: {nas_dashboard_path.exists()}')
print(f'nas_dashboard_path is_dir: {nas_dashboard_path.is_dir()}')

auth_common_path = nas_dashboard_path / 'utils' / 'auth_common.py'
print(f'auth_common_path exists: {auth_common_path.exists()}')

if auth_common_path.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location('auth_common', str(auth_common_path))
    print(f'spec loaded: {spec is not None}')
    if spec:
        auth_common = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auth_common)
        print(f'auth_common loaded: {auth_common is not None}')
        print(f'get_current_user_from_request: {hasattr(auth_common, \"get_current_user_from_request\")}')
        print(f'get_dashboard_login_url: {hasattr(auth_common, \"get_dashboard_login_url\")}')
"
```

---

## 🔧 修正方法

### パスが見つからない場合

1. **マウント設定を確認**:
   ```bash
   # document-automation
   cd ~/nas-project/document-automation
   grep -A 2 "nas-dashboard" docker-compose.yml
   
   # nas-dashboard-monitoring
   cd ~/nas-project/nas-dashboard-monitoring
   grep -A 2 "nas-dashboard" docker-compose.yml
   ```

2. **ホスト側のパスを確認**:
   ```bash
   ls -la /home/AdminUser/nas-project/nas-dashboard/utils/auth_common.py
   ```

3. **コンテナを完全再起動**:
   ```bash
   cd ~/nas-project/<サービス名>
   sudo docker compose down
   sudo docker compose up -d
   ```

### 認証モジュールが読み込まれない場合

1. **起動ログを確認**:
   ```bash
   sudo docker compose logs <サービス名> | grep -i "認証\|auth" | tail -30
   ```

2. **エラーメッセージを確認**:
   - インポートエラーの場合、依存関係を確認
   - パスエラーの場合、マウント設定を確認

3. **完全再ビルド**:
   ```bash
   cd ~/nas-project/<サービス名>
   sudo docker compose down
   sudo docker compose build --no-cache <サービス名>
   sudo docker compose up -d
   ```

---

## 📝 確認チェックリスト

- [ ] `/nas-project/nas-dashboard/utils/auth_common.py`が存在する
- [ ] `docker inspect`でマウント設定が正しい
- [ ] Pythonで直接インポートが成功する
- [ ] 起動ログに「認証モジュールを読み込みました」が表示される
- [ ] `curl`でHTTP 307（リダイレクト）が返される

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

