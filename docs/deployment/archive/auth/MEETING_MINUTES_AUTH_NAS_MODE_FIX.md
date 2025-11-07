# ✅ Meeting Minutes BYC 認証DBパス修正

**作成日**: 2025-11-04  
**目的**: `NAS_MODE`環境変数の追加

---

## ❌ 問題

ログに以下の警告が表示されていました：

```
auth_common - WARNING - 認証データベースが見つかりません: /nas-project/nas-dashboard/data/auth.db
```

ログイン後にアクセスしても、ログイン画面にリダイレクトされてしまいます。

---

## 🔍 原因

`meeting-minutes-byc/docker-compose.yml`に`NAS_MODE`環境変数が設定されていなかったため、`auth_common.py`の`get_auth_db_path()`がローカル環境用のパス（`/nas-project/nas-dashboard/data/auth.db`）を返していました。

正しいパスは、コンテナ内では `/nas-project-data/nas-dashboard/auth.db` です。

---

## ✅ 修正内容

`meeting-minutes-byc/docker-compose.yml`に`NAS_MODE=true`環境変数を追加：

```yaml
environment:
  - FLASK_ENV=production
  - FLASK_DEBUG=False
  # ... (他の環境変数) ...
  - NAS_MODE=true
```

---

## 🚀 デプロイ手順

### ステップ1: コードをプル

```bash
cd ~/nas-project/meeting-minutes-byc
git pull origin feature/monitoring-fail2ban-integration
```

### ステップ2: コンテナを再起動

```bash
sudo docker compose down
sudo docker compose up -d
```

### ステップ3: ログを確認

```bash
sudo docker compose logs -f meeting-minutes-byc
```

### ステップ4: 動作確認

1. **ダッシュボードでログイン**
2. **ログイン後に議事録システムにアクセス**
   - ダッシュボードから「議事録作成システム」をクリック
   - または直接 `https://yoshi-nas-sys.duckdns.org:8443/meetings` にアクセス

**期待される動作**:
- ✅ 議事録システムの画面が表示される
- ✅ ログに `GET / HTTP/1.1" 200` が記録される
- ✅ 認証エラーが発生しない

---

## 🔍 確認コマンド

### 環境変数を確認

```bash
sudo docker compose exec meeting-minutes-byc env | grep NAS_MODE
```

**期待される出力**:
```
NAS_MODE=true
```

### 認証DBパスを確認

```bash
sudo docker compose exec meeting-minutes-byc python -c "
import os
from pathlib import Path

if os.getenv('NAS_MODE'):
    db_path = Path('/nas-project-data/nas-dashboard/auth.db')
else:
    db_path = Path('/nas-project/nas-dashboard/data/auth.db')

print(f'認証DBパス: {db_path}')
print(f'存在するか: {db_path.exists()}')
"
```

**期待される出力**:
```
認証DBパス: /nas-project-data/nas-dashboard/auth.db
存在するか: True
```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

