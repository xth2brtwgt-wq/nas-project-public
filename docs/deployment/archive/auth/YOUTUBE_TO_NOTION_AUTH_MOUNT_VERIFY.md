# ✅ YouTube to Notion 認証機能 マウント設定確認

**作成日**: 2025-11-04  
**目的**: マウント設定が正しく適用されているか確認

---

## ❌ 問題

コンテナを再起動しても、`/nas-project/nas-dashboard`パスが存在しない：

```
nas-dashboardパスが存在するか: False
❌ nas-dashboardパスが見つかりません
```

---

## 🔍 確認手順

### ステップ1: コンテナのマウント設定を直接確認

```bash
cd ~/nas-project/youtube-to-notion

sudo docker inspect youtube-to-notion | grep -A 20 "Mounts"
```

### ステップ2: マウント設定を確認（mountコマンド）

```bash
sudo docker compose exec youtube-to-notion mount | grep nas-project
```

### ステップ3: docker-compose.ymlの設定を確認

```bash
cat docker-compose.yml | grep -A 10 "volumes:"
```

### ステップ4: ホスト側のパスを確認

```bash
ls -la /home/AdminUser/nas-project/nas-dashboard/utils/auth_common.py
```

### ステップ5: コンテナを完全再ビルド

```bash
cd ~/nas-project/youtube-to-notion
sudo docker compose down
sudo docker compose build --no-cache
sudo docker compose up -d
```

### ステップ6: マウント設定を再確認

```bash
sudo docker compose exec youtube-to-notion mount | grep nas-project
```

### ステップ7: パスの存在を再確認

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
    # 代替パスを確認
    alternative_paths = [
        Path('/nas-project'),
        Path('/home/AdminUser/nas-project/nas-dashboard'),
    ]
    for alt_path in alternative_paths:
        print(f'  代替パス {alt_path} が存在するか: {alt_path.exists()}')
"
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
   sudo docker inspect youtube-to-notion | grep -A 30 "Mounts"
   ```

### ホスト側のパスが存在しない場合

1. **パスを確認**:
   ```bash
   ls -la /home/AdminUser/nas-project/nas-dashboard/utils/auth_common.py
   ```

2. **パスが存在しない場合は、nas-dashboardのパスを確認**:
   ```bash
   find /home/AdminUser -name "auth_common.py" 2>/dev/null
   ```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

