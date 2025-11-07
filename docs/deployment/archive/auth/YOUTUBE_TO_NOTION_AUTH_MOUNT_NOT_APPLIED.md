# ✅ YouTube to Notion 認証機能 マウント設定が適用されていない問題

**作成日**: 2025-11-04  
**目的**: マウント設定がコンテナに反映されていない問題を解決

---

## ❌ 問題

`docker inspect`でマウント設定を確認すると、`/nas-project/nas-dashboard`のマウントが表示されていません：

```
"Mounts": [
    {
        "Type": "bind",
        "Source": "/home/AdminUser/nas-project-data/youtube-to-notion/logs",
        "Destination": "/app/logs",
        ...
    },
    {
        "Type": "bind",
        "Source": "/home/AdminUser/nas-project/youtube-to-notion/.env",
        "Destination": "/app/.env",
        ...
    },
    ...
]
```

`/nas-project-data`や`/nas-project/nas-dashboard`のマウントが含まれていません。

---

## 🔍 原因

`docker-compose.yml`を変更した後、コンテナを完全に再起動していない可能性があります。マウント設定は、コンテナ作成時に適用されるため、既存のコンテナを再起動してもマウント設定は変更されません。

---

## ✅ 修正手順

### ステップ1: docker-compose.ymlの設定を確認

```bash
cd ~/nas-project/youtube-to-notion
cat docker-compose.yml | grep -A 12 "volumes:"
```

**期待される設定**:
```yaml
volumes:
  # ... (他のvolumes) ...
  # 認証データベースのマウント（読み取り専用）
  - /home/AdminUser/nas-project-data:/nas-project-data:ro
  # nas-dashboardのutilsディレクトリへのアクセス（認証モジュール用）
  - /home/AdminUser/nas-project/nas-dashboard:/nas-project/nas-dashboard:ro
```

### ステップ2: コンテナを完全に停止

```bash
sudo docker compose down
```

### ステップ3: コンテナを再起動（マウント設定を再適用）

```bash
sudo docker compose up -d
```

### ステップ4: マウント設定を確認

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

### ステップ5: マウント設定を確認（mountコマンド）

```bash
sudo docker compose exec youtube-to-notion mount | grep nas-project
```

**期待される出力**:
```
/home/AdminUser/nas-project-data on /nas-project-data type ...
/home/AdminUser/nas-project/nas-dashboard on /nas-project/nas-dashboard type ...
```

### ステップ6: パスの存在を確認

```bash
sudo docker compose exec youtube-to-notion python -c "
from pathlib import Path

nas_dashboard_path = Path('/nas-project/nas-dashboard')
print(f'nas-dashboardパスが存在するか: {nas_dashboard_path.exists()}')

if nas_dashboard_path.exists():
    auth_common_path = nas_dashboard_path / 'utils' / 'auth_common.py'
    print(f'auth_common.pyパスが存在するか: {auth_common_path.exists()}')
    print(f'auth_common.pyフルパス: {auth_common_path}')
else:
    print('❌ nas-dashboardパスが見つかりません')
"
```

### ステップ7: 起動ログを確認

```bash
sudo docker compose logs youtube-to-notion | grep -i "認証\|auth"
```

**期待されるログ**:
```
認証モジュールを読み込みました
```

---

## 🔧 トラブルシューティング

### マウント設定が表示されない場合

1. **docker-compose.ymlを再確認**:
   ```bash
   cat docker-compose.yml | grep -A 15 "volumes:"
   ```

2. **コンテナを完全再ビルド**:
   ```bash
   sudo docker compose down
   sudo docker compose build --no-cache
   sudo docker compose up -d
   ```

3. **コンテナの詳細情報を確認**:
   ```bash
   sudo docker inspect youtube-to-notion | grep -A 50 "Mounts"
   ```

### docker-compose.ymlが正しくない場合

1. **最新のコードをプル**:
   ```bash
   git pull origin feature/monitoring-fail2ban-integration
   ```

2. **docker-compose.ymlを確認**:
   ```bash
   cat docker-compose.yml | grep -A 15 "volumes:"
   ```

---

## 📝 クイックコマンド（一括実行）

```bash
cd ~/nas-project/youtube-to-notion

# 1. docker-compose.ymlの設定を確認
echo "=== docker-compose.ymlの設定を確認 ==="
cat docker-compose.yml | grep -A 12 "volumes:"

# 2. コンテナを完全停止
echo ""
echo "=== コンテナを完全停止 ==="
sudo docker compose down

# 3. コンテナを起動
echo ""
echo "=== コンテナを起動 ==="
sudo docker compose up -d

# 4. マウント設定を確認
echo ""
echo "=== マウント設定を確認 ==="
sudo docker inspect youtube-to-notion | grep -A 30 "Mounts" | grep -E "nas-project|Source|Destination"

# 5. マウント設定を確認（mountコマンド）
echo ""
echo "=== マウント設定を確認（mountコマンド） ==="
sudo docker compose exec youtube-to-notion mount | grep nas-project

# 6. パスの存在を確認
echo ""
echo "=== パスの存在を確認 ==="
sudo docker compose exec youtube-to-notion python -c "
from pathlib import Path

nas_dashboard_path = Path('/nas-project/nas-dashboard')
print(f'nas-dashboardパスが存在するか: {nas_dashboard_path.exists()}')

if nas_dashboard_path.exists():
    auth_common_path = nas_dashboard_path / 'utils' / 'auth_common.py'
    print(f'auth_common.pyパスが存在するか: {auth_common_path.exists()}')
else:
    print('❌ nas-dashboardパスが見つかりません')
"

# 7. 起動ログを確認
echo ""
echo "=== 起動ログを確認 ==="
sudo docker compose logs youtube-to-notion | grep -i "認証\|auth"
```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

