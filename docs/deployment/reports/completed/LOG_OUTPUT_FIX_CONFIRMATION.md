# ログ出力先修正の確認

## 📋 概要

各プロジェクトのログ出力先が`nas-project-data`の各システム用フォルダ配下に正しく設定されているか確認します。

## ✅ 修正内容の確認

### 1. youtube-to-notion

**app.py**:
```python
if os.getenv('NAS_MODE'):
    log_dir = os.getenv('LOG_DIR', '/app/logs')
else:
    log_dir = os.getenv('LOG_DIR', './logs')
```

**docker-compose.yml**:
```yaml
volumes:
  - /home/AdminUser/nas-project-data/youtube-to-notion/logs:/app/logs
```

**結果**: ✅ 正しく設定されています
- NAS環境では `/app/logs` を使用（コンテナ内）
- ホスト側では `/home/AdminUser/nas-project-data/youtube-to-notion/logs` にマウント

### 2. meeting-minutes-byc

**app.py**:
```python
if os.getenv('NAS_MODE'):
    log_dir = os.getenv('LOG_DIR', '/app/logs')
else:
    log_dir = os.getenv('LOG_DIR', './logs')
```

**docker-compose.yml**:
```yaml
volumes:
  - /home/AdminUser/nas-project-data/meeting-minutes-byc/logs:/app/logs
```

**結果**: ✅ 正しく設定されています
- NAS環境では `/app/logs` を使用（コンテナ内）
- ホスト側では `/home/AdminUser/nas-project-data/meeting-minutes-byc/logs` にマウント

### 3. nas-dashboard

**app.py**:
```python
if os.getenv('NAS_MODE'):
    log_dir = os.getenv('LOG_DIR', '/app/logs')
else:
    log_dir = os.getenv('LOG_DIR', './logs')
```

**docker-compose.yml**:
```yaml
volumes:
  - /home/AdminUser/nas-project-data/nas-dashboard/logs:/app/logs
```

**結果**: ✅ 正しく設定されています
- NAS環境では `/app/logs` を使用（コンテナ内）
- ホスト側では `/home/AdminUser/nas-project-data/nas-dashboard/logs` にマウント

### 4. notion-knowledge-summaries

**config/settings.py**:
```python
log_file: str = os.getenv('LOG_FILE', "/app/logs/summaries.log" if os.getenv('NAS_MODE') else "./logs/summaries.log")
```

**docker-compose.yml**:
```yaml
volumes:
  - /home/AdminUser/nas-project-data/notion-knowledge-summaries/logs:/app/logs
environment:
  - NAS_MODE=true
  - LOG_FILE=/app/logs/summaries.log
```

**結果**: ✅ 正しく設定されています
- NAS環境では `/app/logs/summaries.log` を使用（コンテナ内）
- ホスト側では `/home/AdminUser/nas-project-data/notion-knowledge-summaries/logs` にマウント

## 📊 ログ出力先のマッピング

| プロジェクト | コンテナ内パス | ホスト側パス |
|------------|--------------|-------------|
| youtube-to-notion | `/app/logs` | `/home/AdminUser/nas-project-data/youtube-to-notion/logs` |
| meeting-minutes-byc | `/app/logs` | `/home/AdminUser/nas-project-data/meeting-minutes-byc/logs` |
| nas-dashboard | `/app/logs` | `/home/AdminUser/nas-project-data/nas-dashboard/logs` |
| notion-knowledge-summaries | `/app/logs` | `/home/AdminUser/nas-project-data/notion-knowledge-summaries/logs` |

## 🔧 修正内容

### 問題点

以前のコードでは、`os.path.exists('/app/logs')` や `os.path.exists('/nas-project-data')` のチェックを行っていましたが、コンテナ起動時にディレクトリが存在しない場合、`./logs` にフォールバックしてしまい、プロジェクトフォルダ内にログが出力されていました。

### 修正方法

1. **`os.path.exists()` チェックを削除**: `NAS_MODE` 環境変数が設定されている場合は、常に `/app/logs` を使用するように変更
2. **一貫性の確保**: すべてのプロジェクトで同じロジックを使用するように統一

## ✅ 確認結果

**はい、すべてのプロジェクトで `nas-project-data` の各システム用フォルダ配下のログ出力先に修正されています。**

- ✅ `youtube-to-notion`: `/home/AdminUser/nas-project-data/youtube-to-notion/logs`
- ✅ `meeting-minutes-byc`: `/home/AdminUser/nas-project-data/meeting-minutes-byc/logs`
- ✅ `nas-dashboard`: `/home/AdminUser/nas-project-data/nas-dashboard/logs`
- ✅ `notion-knowledge-summaries`: `/home/AdminUser/nas-project-data/notion-knowledge-summaries/logs`

## 📋 次のステップ

1. 変更をコミット・プッシュ
2. NAS環境で `git pull` を実行
3. 各プロジェクトを再デプロイ
4. プロジェクトフォルダ内の既存ログファイルを削除
5. ログが正しい場所に出力されていることを確認

---

**更新日**: 2025年11月7日
**ステータス**: ✅ 修正完了

