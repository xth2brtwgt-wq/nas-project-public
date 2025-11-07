# ✅ YouTube to Notion 認証機能 マウント設定適用

**作成日**: 2025-11-04  
**目的**: `docker-compose.yml`の認証関連マウント設定をコンテナに適用

---

## ✅ 現在の状況

`git pull`が成功し、`docker-compose.yml`に認証関連のマウント設定が含まれています：

```yaml
volumes:
  # NAS環境でのデータ永続化（統合データディレクトリ使用）
  - /home/AdminUser/nas-project-data/youtube-to-notion/uploads:/app/data/uploads
  - /home/AdminUser/nas-project-data/youtube-to-notion/outputs:/app/data/outputs
  - /home/AdminUser/nas-project-data/youtube-to-notion/cache:/app/data/cache
  - /home/AdminUser/nas-project-data/youtube-to-notion/logs:/app/logs
  # 認証データベースのマウント（読み取り専用）
  - /home/AdminUser/nas-project-data:/nas-project-data:ro
  # nas-dashboardのutilsディレクトリへのアクセス（認証モジュール用）
  - /home/AdminUser/nas-project/nas-dashboard:/nas-project/nas-dashboard:ro
  # 環境変数ファイル
  - ./.env:/app/.env:ro
```

---

## ✅ 適用手順

### ステップ1: コンテナを完全停止

```bash
cd ~/nas-project/youtube-to-notion
sudo docker compose down
```

### ステップ2: コンテナを再作成・起動（マウント設定を適用）

```bash
sudo docker compose up -d
```

### ステップ3: マウント設定を確認

```bash
sudo docker inspect youtube-to-notion | grep -A 30 "Mounts" | grep -E "nas-project|Source|Destination"
```

**期待される出力**:
```
"Source": "/home/AdminUser/nas-project-data",
"Destination": "/nas-project-data",
...
"Source": "/home/AdminUser/nas-project/nas-dashboard",
"Destination": "/nas-project/nas-dashboard",
```

### ステップ4: マウント設定を確認（mountコマンド）

```bash
sudo docker compose exec youtube-to-notion mount | grep nas-project
```

**期待される出力**:
```
/home/AdminUser/nas-project-data on /nas-project-data type ...
/home/AdminUser/nas-project/nas-dashboard on /nas-project/nas-dashboard type ...
```

### ステップ5: パスの存在を確認

```bash
sudo docker compose exec youtube-to-notion python -c "
from pathlib import Path

nas_dashboard_path = Path('/nas-project/nas-dashboard')
print(f'nas-dashboardパスが存在するか: {nas_dashboard_path.exists()}')

if nas_dashboard_path.exists():
    auth_common_path = nas_dashboard_path / 'utils' / 'auth_common.py'
    print(f'auth_common.pyパスが存在するか: {auth_common_path.exists()}')
    print(f'✅ 認証モジュールが見つかりました: {auth_common_path}')
else:
    print('❌ nas-dashboardパスが見つかりません')
"
```

### ステップ6: 起動ログを確認

```bash
sudo docker compose logs youtube-to-notion | grep -i "認証\|auth"
```

**期待されるログ**:
```
認証モジュールを読み込みました
```

---

## 📝 クイックコマンド（一括実行）

```bash
cd ~/nas-project/youtube-to-notion

# 1. コンテナを完全停止
echo "=== コンテナを完全停止 ==="
sudo docker compose down

# 2. コンテナを起動
echo ""
echo "=== コンテナを起動 ==="
sudo docker compose up -d

# 3. マウント設定を確認
echo ""
echo "=== マウント設定を確認 ==="
sudo docker inspect youtube-to-notion | grep -A 30 "Mounts" | grep -E "nas-project|Source|Destination"

# 4. マウント設定を確認（mountコマンド）
echo ""
echo "=== マウント設定を確認（mountコマンド） ==="
sudo docker compose exec youtube-to-notion mount | grep nas-project

# 5. パスの存在を確認
echo ""
echo "=== パスの存在を確認 ==="
sudo docker compose exec youtube-to-notion python -c "
from pathlib import Path

nas_dashboard_path = Path('/nas-project/nas-dashboard')
print(f'nas-dashboardパスが存在するか: {nas_dashboard_path.exists()}')

if nas_dashboard_path.exists():
    auth_common_path = nas_dashboard_path / 'utils' / 'auth_common.py'
    print(f'auth_common.pyパスが存在するか: {auth_common_path.exists()}')
    print(f'✅ 認証モジュールが見つかりました: {auth_common_path}')
else:
    print('❌ nas-dashboardパスが見つかりません')
"

# 6. 起動ログを確認
echo ""
echo "=== 起動ログを確認 ==="
sudo docker compose logs youtube-to-notion | grep -i "認証\|auth"
```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

