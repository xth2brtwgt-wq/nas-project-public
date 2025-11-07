# ✅ YouTube to Notion 認証機能 マウント設定が欠落している問題

**作成日**: 2025-11-04  
**目的**: docker-compose.ymlに認証関連のマウント設定が含まれていない問題を解決

---

## ❌ 問題

`docker compose down`と`docker compose up -d`を実行しても、まだ`/nas-project/nas-dashboard`のマウントが適用されていません。

`docker inspect`の結果を見ると、認証関連のマウント（`/nas-project-data`と`/nas-project/nas-dashboard`）が含まれていません。

**現在のdocker-compose.ymlのvolumes設定**:
```yaml
volumes:
  # NAS環境でのデータ永続化（統合データディレクトリ使用）
  - /home/AdminUser/nas-project-data/youtube-to-notion/uploads:/app/data/uploads
  - /home/AdminUser/nas-project-data/youtube-to-notion/outputs:/app/data/outputs
  - /home/AdminUser/nas-project-data/youtube-to-notion/cache:/app/data/cache
  - /home/AdminUser/nas-project-data/youtube-to-notion/logs:/app/logs
  # 環境変数ファイル
  - ./.env:/app/.env:ro
```

**認証関連のマウント設定が欠落しています！**

---

## 🔍 原因

NAS環境の`docker-compose.yml`が古いままか、Gitから最新のコードをプルしていない可能性があります。

---

## ✅ 修正手順

### ステップ1: Gitから最新のコードをプル

```bash
cd ~/nas-project/youtube-to-notion
git pull origin feature/monitoring-fail2ban-integration
```

### ステップ2: docker-compose.ymlの設定を確認

```bash
cat docker-compose.yml | grep -A 15 "volumes:"
```

**期待される設定**:
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

### ステップ3: 認証関連のマウント設定が含まれていない場合

手動で`docker-compose.yml`に追加する必要があります。

```bash
# docker-compose.ymlを編集
nano docker-compose.yml
```

`volumes:`セクションに以下を追加：

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

### ステップ4: コンテナを完全再起動

```bash
sudo docker compose down
sudo docker compose up -d
```

### ステップ5: マウント設定を確認

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

### ステップ6: マウント設定を確認（mountコマンド）

```bash
sudo docker compose exec youtube-to-notion mount | grep nas-project
```

**期待される出力**:
```
/home/AdminUser/nas-project-data on /nas-project-data type ...
/home/AdminUser/nas-project/nas-dashboard on /nas-project/nas-dashboard type ...
```

### ステップ7: パスの存在を確認

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

### ステップ8: 起動ログを確認

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

# 1. Gitから最新のコードをプル
echo "=== Gitから最新のコードをプル ==="
git pull origin feature/monitoring-fail2ban-integration

# 2. docker-compose.ymlの設定を確認
echo ""
echo "=== docker-compose.ymlの設定を確認 ==="
cat docker-compose.yml | grep -A 15 "volumes:"

# 3. 認証関連のマウント設定が含まれているか確認
echo ""
echo "=== 認証関連のマウント設定を確認 ==="
if grep -q "/nas-project-data:ro" docker-compose.yml && grep -q "/nas-project/nas-dashboard:ro" docker-compose.yml; then
    echo "✅ 認証関連のマウント設定が含まれています"
else
    echo "❌ 認証関連のマウント設定が含まれていません"
    echo "docker-compose.ymlを手動で編集する必要があります"
fi

# 4. コンテナを完全停止
echo ""
echo "=== コンテナを完全停止 ==="
sudo docker compose down

# 5. コンテナを起動
echo ""
echo "=== コンテナを起動 ==="
sudo docker compose up -d

# 6. マウント設定を確認
echo ""
echo "=== マウント設定を確認 ==="
sudo docker inspect youtube-to-notion | grep -A 30 "Mounts" | grep -E "nas-project|Source|Destination"

# 7. マウント設定を確認（mountコマンド）
echo ""
echo "=== マウント設定を確認（mountコマンド） ==="
sudo docker compose exec youtube-to-notion mount | grep nas-project

# 8. パスの存在を確認
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

# 9. 起動ログを確認
echo ""
echo "=== 起動ログを確認 ==="
sudo docker compose logs youtube-to-notion | grep -i "認証\|auth"
```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

