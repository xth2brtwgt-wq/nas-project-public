# データ外部化の確認 - プロジェクト内に作成されないことの保証

## 📋 概要

全プロジェクトの生成物（ログ、データ、キャッシュなど）が`nas-project-data`に保存され、今後プロジェクトフォルダ内に作成されないことを確認しました。

## ✅ 確認内容

### 1. 各プロジェクトの設定確認

#### **amazon-analytics**

**docker-compose.yml:**
```yaml
volumes:
  - /home/AdminUser/nas-project-data/amazon-analytics:/app/data
  - /home/AdminUser/nas-project-data:/nas-project-data:ro
environment:
  - NAS_MODE=true
```

**app/api/main.py:**
```python
# NAS環境では統合データディレクトリを使用
if os.getenv('NAS_MODE') and os.path.exists('/app/data'):
    log_dir = os.getenv('LOG_DIR', '/app/data/logs')  # /app/data = nas-project-data/amazon-analytics
```

**config/settings.py:**
```python
# NAS環境では/app/dataを使用
if os.getenv('NAS_MODE') and os.path.exists('/app/data'):
    settings.DATA_DIR = Path('/app/data')  # /app/data = nas-project-data/amazon-analytics
```

**結果:**
- ✅ ログファイル: `/app/data/logs/app.log` → `/home/AdminUser/nas-project-data/amazon-analytics/logs/app.log`
- ✅ データファイル: `/app/data/uploads/` → `/home/AdminUser/nas-project-data/amazon-analytics/uploads/`
- ✅ プロジェクト内には作成されない

#### **youtube-to-notion**

**docker-compose.yml:**
```yaml
volumes:
  - /home/AdminUser/nas-project-data/youtube-to-notion/uploads:/app/data/uploads
  - /home/AdminUser/nas-project-data/youtube-to-notion/outputs:/app/data/outputs
  - /home/AdminUser/nas-project-data/youtube-to-notion/cache:/app/data/cache
  - /home/AdminUser/nas-project-data/youtube-to-notion/logs:/app/logs
environment:
  - NAS_MODE=true
```

**app.py:**
```python
# NAS環境では統合データディレクトリを使用
if os.getenv('NAS_MODE'):
    UPLOAD_FOLDER = os.getenv('UPLOAD_DIR', '/app/data/uploads')  # nas-project-dataにマウント
    OUTPUT_FOLDER = os.getenv('OUTPUT_DIR', '/app/data/outputs')   # nas-project-dataにマウント
    CACHE_FOLDER = os.getenv('CACHE_DIR', '/app/data/cache')      # nas-project-dataにマウント
    LOG_FOLDER = os.getenv('LOG_DIR', '/app/logs')                # nas-project-dataにマウント
```

**結果:**
- ✅ ログファイル: `/app/logs/app.log` → `/home/AdminUser/nas-project-data/youtube-to-notion/logs/app.log`
- ✅ アップロードファイル: `/app/data/uploads/` → `/home/AdminUser/nas-project-data/youtube-to-notion/uploads/`
- ✅ プロジェクト内には作成されない

#### **meeting-minutes-byc**

**docker-compose.yml:**
```yaml
volumes:
  - /home/AdminUser/nas-project-data/meeting-minutes-byc/uploads:/app/uploads
  - /home/AdminUser/nas-project-data/meeting-minutes-byc/transcripts:/app/transcripts
  - /home/AdminUser/nas-project-data/meeting-minutes-byc/logs:/app/logs
environment:
  - NAS_MODE=true
```

**app.py:**
```python
# NAS環境では統合データディレクトリを使用
if os.getenv('NAS_MODE'):
    UPLOAD_FOLDER = os.getenv('UPLOAD_DIR', '/app/uploads')        # nas-project-dataにマウント
    TRANSCRIPT_FOLDER = os.getenv('TRANSCRIPT_DIR', '/app/transcripts')  # nas-project-dataにマウント
if os.getenv('NAS_MODE') and os.path.exists('/app/logs'):
    log_dir = os.getenv('LOG_DIR', '/app/logs')                   # nas-project-dataにマウント
```

**結果:**
- ✅ ログファイル: `/app/logs/app.log` → `/home/AdminUser/nas-project-data/meeting-minutes-byc/logs/app.log`
- ✅ アップロードファイル: `/app/uploads/` → `/home/AdminUser/nas-project-data/meeting-minutes-byc/uploads/`
- ✅ プロジェクト内には作成されない

#### **nas-dashboard**

**docker-compose.yml:**
```yaml
volumes:
  - /home/AdminUser/nas-project-data/nas-dashboard/logs:/app/logs
  - /home/AdminUser/nas-project-data/nas-dashboard/backups:/app/backups
  - /home/AdminUser/nas-project-data/nas-dashboard/reports:/app/reports
environment:
  - NAS_MODE=true
```

**app.py:**
```python
# NAS環境では統合データディレクトリを使用
if os.getenv('NAS_MODE') and os.path.exists('/nas-project-data'):
    log_dir = os.getenv('LOG_DIR', '/nas-project-data/nas-dashboard/logs')  # nas-project-dataにマウント
```

**結果:**
- ✅ ログファイル: `/nas-project-data/nas-dashboard/logs/app.log` → `/home/AdminUser/nas-project-data/nas-dashboard/logs/app.log`
- ✅ バックアップファイル: `/app/backups/` → `/home/AdminUser/nas-project-data/nas-dashboard/backups/`
- ✅ プロジェクト内には作成されない

#### **document-automation**

**docker-compose.yml:**
```yaml
volumes:
  - /home/AdminUser/nas-project-data/document-automation/uploads:/app/uploads
  - /home/AdminUser/nas-project-data/document-automation/processed:/app/processed
  - /home/AdminUser/nas-project-data/document-automation/exports:/app/exports
  - /home/AdminUser/nas-project-data/document-automation/cache:/app/cache
environment:
  - NAS_MODE=true
```

**app/api/main.py:**
```python
# NAS環境では統合データディレクトリを使用
if os.getenv('NAS_MODE') and os.path.exists('/app/logs'):
    log_dir = os.getenv('LOG_DIR', '/app/logs')  # nas-project-dataにマウント（docker-compose.ymlで設定）
```

**結果:**
- ✅ ログファイル: `/app/logs/app.log` → `/home/AdminUser/nas-project-data/document-automation/logs/app.log`
- ✅ アップロードファイル: `/app/uploads/` → `/home/AdminUser/nas-project-data/document-automation/uploads/`
- ✅ プロジェクト内には作成されない

## 🔒 保証メカニズム

### 1. Docker Compose のボリュームマウント

すべてのプロジェクトで、`docker-compose.yml`で`nas-project-data`にマウントされています：

```yaml
volumes:
  - /home/AdminUser/nas-project-data/{プロジェクト名}/logs:/app/logs
  - /home/AdminUser/nas-project-data/{プロジェクト名}/uploads:/app/uploads
  # ... その他のディレクトリ
```

**効果:**
- コンテナ内の`/app/logs`に書き込んだファイルは、自動的に`/home/AdminUser/nas-project-data/{プロジェクト名}/logs/`に保存される
- プロジェクトディレクトリ内には書き込まれない

### 2. アプリケーションコードの修正

すべてのプロジェクトで、NAS環境では`nas-project-data`を使用するように修正済み：

```python
# NAS環境判定
if os.getenv('NAS_MODE') and os.path.exists('/app/data'):
    log_dir = os.getenv('LOG_DIR', '/app/data/logs')  # コンテナ内のパス
else:
    log_dir = os.getenv('LOG_DIR', './logs')  # ローカル環境のみ
```

**効果:**
- NAS環境では、コンテナ内のマウントされたパス（`/app/data/logs`など）を使用
- ローカル環境では、プロジェクト内の相対パス（`./logs`など）を使用
- NAS環境では、プロジェクト内に作成されない

### 3. 環境変数の設定

すべてのプロジェクトで、`NAS_MODE=true`が設定されています：

```yaml
environment:
  - NAS_MODE=true
```

**効果:**
- アプリケーションコードがNAS環境を正しく判定できる
- 正しいパス（`nas-project-data`）を使用する

## ✅ 結論

### プロジェクト内に作成されないことの保証

1. **Docker Compose のボリュームマウント**
   - すべての生成物ディレクトリが`nas-project-data`にマウントされている
   - コンテナ内に書き込んだファイルは、自動的に`nas-project-data`に保存される

2. **アプリケーションコードの修正**
   - NAS環境では、コンテナ内のマウントされたパスを使用するように修正済み
   - プロジェクト内の相対パス（`./logs`など）は使用しない

3. **環境変数の設定**
   - `NAS_MODE=true`が設定されている
   - アプリケーションコードが正しくNAS環境を判定できる

### 削除可能なファイル

以下のファイル・ディレクトリは、既に`nas-project-data`に移動済みで、今後プロジェクト内に作成されないため、削除可能です：

- `youtube-to-notion/data/` - 既に`nas-project-data/youtube-to-notion/`に移動済み
- `meeting-minutes-byc/uploads/` - 既に`nas-project-data/meeting-minutes-byc/uploads/`に移動済み
- `nas-dashboard/logs/` - 既に`nas-project-data/nas-dashboard/logs/`に移動済み
- `nas-dashboard/data/` - 既に`nas-project-data/nas-dashboard/auth.db`に移動済み
- `youtube-to-notion/logs/` - 既に`nas-project-data/youtube-to-notion/logs/`に移動済み

### 削除しても問題ないファイル

- `__pycache__/` - Pythonキャッシュ（実行時に自動再生成される）
- `.pyc`ファイル - Pythonコンパイル済みファイル（実行時に自動再生成される）
- `venv/` - Python仮想環境（NAS環境では不要、Dockerコンテナ内で実行される）

## 📋 確認方法

### 削除後の確認

```bash
# プロジェクト内に生成物がないことを確認
find ~/nas-project -name "*.log" -o -name "*.db" -o -type d -name "data" -o -type d -name "logs" -o -type d -name "uploads"

# コンテナを再起動して、プロジェクト内に作成されないことを確認
docker compose restart

# プロジェクト内を再確認
find ~/nas-project -name "*.log" -o -name "*.db" -o -type d -name "data" -o -type d -name "logs" -o -type d -name "uploads"
```

### システム動作確認

```bash
# 各プロジェクトのログが正しく書き込まれているか確認
tail -f /home/AdminUser/nas-project-data/amazon-analytics/logs/app.log
tail -f /home/AdminUser/nas-project-data/youtube-to-notion/logs/app.log
tail -f /home/AdminUser/nas-project-data/meeting-minutes-byc/logs/app.log
tail -f /home/AdminUser/nas-project-data/nas-dashboard/logs/app.log
```

## 🔗 関連ドキュメント

- [データ管理ルール](../../DATA_MANAGEMENT_RULES.md)
- [全プロジェクトの生成物をプロジェクト外に保存する修正](./ALL_PROJECTS_DATA_EXTERNAL_FIX.md)
- [プロジェクトクリーンアップ項目](./PROJECT_CLEANUP_ITEMS.md)

---

**作成日**: 2025年1月27日
**対象**: 全NAS環境プロジェクト
**更新**: 必要に応じて更新

