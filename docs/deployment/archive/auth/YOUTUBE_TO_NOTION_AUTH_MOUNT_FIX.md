# ✅ YouTube to Notion 認証機能 マウント設定修正

**作成日**: 2025-11-04  
**目的**: 認証モジュールのマウント設定を確認・修正

---

## ❌ 問題

コンテナ内で`/nas-project/nas-dashboard`パスが存在しない：

```
nas-dashboardパスが存在するか: False
❌ nas-dashboardパスが見つかりません
```

---

## 🔍 原因

マウント設定が正しく反映されていない可能性があります。コンテナを再起動する必要があります。

---

## ✅ 修正手順

### ステップ1: docker-compose.ymlの確認

```bash
cd ~/nas-project/youtube-to-notion
cat docker-compose.yml | grep -A 10 "volumes:"
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

### ステップ2: コンテナを完全再起動

```bash
cd ~/nas-project/youtube-to-notion
sudo docker compose down
sudo docker compose up -d
```

### ステップ3: マウント設定を確認

```bash
sudo docker compose exec youtube-to-notion mount | grep nas-project
```

**期待される出力**:
```
/home/AdminUser/nas-project-data on /nas-project-data type ...
/home/AdminUser/nas-project/nas-dashboard on /nas-project/nas-dashboard type ...
```

### ステップ4: パスの存在を再確認

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

### ステップ5: 起動ログを確認

```bash
sudo docker compose logs youtube-to-notion | grep -i "認証\|auth"
```

**期待されるログ**:
```
認証モジュールを読み込みました
```

---

## 🔧 トラブルシューティング

### マウント設定が反映されない場合

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

3. **マウント設定を直接確認**:
   ```bash
   sudo docker inspect youtube-to-notion | grep -A 10 "Mounts"
   ```

### パスが存在しない場合

1. **ホスト側のパスを確認**:
   ```bash
   ls -la /home/AdminUser/nas-project/nas-dashboard/utils/auth_common.py
   ```

2. **マウント設定を再確認**:
   ```bash
   sudo docker compose exec youtube-to-notion ls -la /nas-project/nas-dashboard/utils/auth_common.py
   ```

---

## 📝 クイックコマンド（一括実行）

```bash
cd ~/nas-project/youtube-to-notion

# 1. 最新のコードをプル
echo "=== 最新のコードをプル ==="
git pull origin feature/monitoring-fail2ban-integration

# 2. コンテナを停止
echo ""
echo "=== コンテナを停止 ==="
sudo docker compose down

# 3. コンテナを起動
echo ""
echo "=== コンテナを起動 ==="
sudo docker compose up -d

# 4. マウント設定を確認
echo ""
echo "=== マウント設定を確認 ==="
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

