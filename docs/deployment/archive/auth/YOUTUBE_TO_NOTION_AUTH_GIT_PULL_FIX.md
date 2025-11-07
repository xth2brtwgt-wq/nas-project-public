# ✅ YouTube to Notion 認証機能 Git Pull エラー修正

**作成日**: 2025-11-04  
**目的**: `.env`ファイルの競合で`git pull`が失敗する問題を解決

---

## ❌ 問題

`git pull`を実行すると、`.env`ファイルの競合でマージが失敗します：

```
error: Your local changes to the following files would be overwritten by merge:
        amazon-analytics/.env
        document-automation/.env
        nas-dashboard/.env
        notion-knowledge-summaries/.env
Please commit your changes or stash them before you merge.
```

また、未追跡ファイルの競合もあります：

```
error: The following untracked working tree files would be overwritten by merge:
        docker/fail2ban/data/jail.d/sshd.local
        document-automation/docker-entrypoint.sh
        document-automation/fix-permissions.sh
Please move or remove them before you merge.
```

これにより、`docker-compose.yml`の更新（認証関連のマウント設定）がプルされていません。

---

## ✅ 修正手順

### ステップ1: ローカルの.env変更を一時保存（git stash）

```bash
cd ~/nas-project

# .envファイルのローカル変更を一時保存
git stash push -m "Local .env changes before pull" \
    amazon-analytics/.env \
    document-automation/.env \
    nas-dashboard/.env \
    notion-knowledge-summaries/.env \
    youtube-to-notion/.env
```

### ステップ2: 競合している未追跡ファイルを一時的に移動

```bash
cd ~/nas-project

# 競合している未追跡ファイルを一時的に移動
if [ -f "docker/fail2ban/data/jail.d/sshd.local" ]; then
    mkdir -p /tmp/nas-project-backup/docker/fail2ban/data/jail.d/
    mv docker/fail2ban/data/jail.d/sshd.local /tmp/nas-project-backup/docker/fail2ban/data/jail.d/sshd.local
    echo "✅ docker/fail2ban/data/jail.d/sshd.localを一時退避しました"
fi

if [ -f "document-automation/docker-entrypoint.sh" ]; then
    mkdir -p /tmp/nas-project-backup/document-automation/
    mv document-automation/docker-entrypoint.sh /tmp/nas-project-backup/document-automation/docker-entrypoint.sh
    echo "✅ document-automation/docker-entrypoint.shを一時退避しました"
fi

if [ -f "document-automation/fix-permissions.sh" ]; then
    mkdir -p /tmp/nas-project-backup/document-automation/
    mv document-automation/fix-permissions.sh /tmp/nas-project-backup/document-automation/fix-permissions.sh
    echo "✅ document-automation/fix-permissions.shを一時退避しました"
fi
```

### ステップ3: Gitから最新のコードをプル

```bash
cd ~/nas-project
git pull origin feature/monitoring-fail2ban-integration
```

### ステップ4: .envファイルのローカル変更を復元（必要に応じて）

```bash
cd ~/nas-project

# 一時保存した変更を復元（競合が発生する場合は手動で解決）
git stash pop

# または、.env.restoreから設定を復元する場合
# 各プロジェクトで.env.restoreがあれば、そこから必要な設定を復元
for dir in amazon-analytics document-automation nas-dashboard notion-knowledge-summaries youtube-to-notion; do
    if [ -f "$dir/.env.restore" ]; then
        echo "⚠️  $dir/.env.restoreが存在します。必要に応じて.envに設定を反映してください"
        # 例: cp "$dir/.env.restore" "$dir/.env"  # 必要に応じてコメントアウトを外す
    fi
done
```

**注意**: `.env`はGitで管理されているため、`git pull`で更新される可能性があります。実際のAPIキー・パスワードは`.env.restore`にバックアップとして保存しておき、`.env`が初期化された場合に復元できるようにします。

### ステップ5: docker-compose.ymlの設定を確認

```bash
cd ~/nas-project/youtube-to-notion
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

### ステップ6: 認証関連のマウント設定が含まれていない場合

手動で`docker-compose.yml`に追加する必要があります。

```bash
cd ~/nas-project/youtube-to-notion

# docker-compose.ymlを編集
nano docker-compose.yml
```

`volumes:`セクション（24行目付近）に以下を追加：

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

### ステップ7: コンテナを完全再起動

```bash
cd ~/nas-project/youtube-to-notion
sudo docker compose down
sudo docker compose up -d
```

### ステップ8: マウント設定を確認

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

### ステップ9: パスの存在を確認

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

---

## 📝 クイックコマンド（一括実行）

```bash
cd ~/nas-project

# 1. ローカルの.env変更を一時保存（git stash）
echo "=== .envファイルのローカル変更を一時保存 ==="
git stash push -m "Local .env changes before pull" \
    amazon-analytics/.env \
    document-automation/.env \
    nas-dashboard/.env \
    notion-knowledge-summaries/.env \
    youtube-to-notion/.env
echo "✅ .envファイルのローカル変更を一時保存しました"

# 2. 競合している未追跡ファイルを一時的に移動
echo ""
echo "=== 競合ファイルを一時退避 ==="
mkdir -p /tmp/nas-project-backup/docker/fail2ban/data/jail.d/
mkdir -p /tmp/nas-project-backup/document-automation/

if [ -f "docker/fail2ban/data/jail.d/sshd.local" ]; then
    mv docker/fail2ban/data/jail.d/sshd.local /tmp/nas-project-backup/docker/fail2ban/data/jail.d/sshd.local
    echo "✅ docker/fail2ban/data/jail.d/sshd.localを一時退避しました"
fi

if [ -f "document-automation/docker-entrypoint.sh" ]; then
    mv document-automation/docker-entrypoint.sh /tmp/nas-project-backup/document-automation/docker-entrypoint.sh
    echo "✅ document-automation/docker-entrypoint.shを一時退避しました"
fi

if [ -f "document-automation/fix-permissions.sh" ]; then
    mv document-automation/fix-permissions.sh /tmp/nas-project-backup/document-automation/fix-permissions.sh
    echo "✅ document-automation/fix-permissions.shを一時退避しました"
fi

# 3. Gitから最新のコードをプル
echo ""
echo "=== Gitから最新のコードをプル ==="
git pull origin feature/monitoring-fail2ban-integration

# 4. .envファイルのローカル変更を復元（必要に応じて）
echo ""
echo "=== .envファイルのローカル変更を復元 ==="
git stash pop

# .env.restoreから設定を確認
echo ""
echo "=== .env.restoreの確認 ==="
for dir in amazon-analytics document-automation nas-dashboard notion-knowledge-summaries youtube-to-notion; do
    if [ -f "$dir/.env.restore" ]; then
        echo "⚠️  $dir/.env.restoreが存在します。必要に応じて.envに設定を反映してください"
    fi
done

# 5. docker-compose.ymlの設定を確認
echo ""
echo "=== docker-compose.ymlの設定を確認 ==="
cd youtube-to-notion
cat docker-compose.yml | grep -A 15 "volumes:"

# 6. 認証関連のマウント設定が含まれているか確認
echo ""
echo "=== 認証関連のマウント設定を確認 ==="
if grep -q "/nas-project-data:ro" docker-compose.yml && grep -q "/nas-project/nas-dashboard:ro" docker-compose.yml; then
    echo "✅ 認証関連のマウント設定が含まれています"
else
    echo "❌ 認証関連のマウント設定が含まれていません"
    echo "docker-compose.ymlを手動で編集する必要があります"
fi
```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

