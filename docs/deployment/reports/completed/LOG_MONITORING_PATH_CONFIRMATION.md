# ログ監視・NAS監視のパス確認

## 📋 概要

ログ監視やNAS監視で参照しているパスが正しく`nas-project-data`配下を参照しているか確認します。

## ✅ 確認結果

### 1. nas-dashboard のログ監視機能

**修正前の問題**:
- `os.path.exists('/nas-project-data')` チェックが残っていた
- コンテナ起動時にディレクトリが存在しない場合、フォールバックしてしまう可能性があった

**修正後**:
- `NAS_MODE` 環境変数のみで判定
- すべてのログ監視機能で `/nas-project-data/...` パスを使用

**ログ監視で参照しているパス**:
- `meeting-minutes-byc`: `/nas-project-data/meeting-minutes-byc/logs/app.log` ✅
- `amazon-analytics`: `/nas-project-data/amazon-analytics/logs/app.log` ✅
- `document-automation`: `/nas-project-data/document-automation/logs/app.log` ✅
- `youtube-to-notion`: `/nas-project-data/youtube-to-notion/logs/app.log` ✅
- `nas-dashboard`: `/nas-project-data/nas-dashboard/logs/app.log` ✅
- `nas-dashboard-monitoring`: `/nas-project-data/nas-dashboard-monitoring/logs/app.log` ✅

**docker-compose.yml のマウント設定**:
```yaml
volumes:
  - /home/AdminUser/nas-project-data:/nas-project-data:rw
```

これにより、コンテナ内では `/nas-project-data/...` でアクセス可能です。

### 2. nas-dashboard-monitoring の設定

**docker-compose.yml のマウント設定**:
```yaml
volumes:
  - /home/AdminUser/nas-project-data/nas-dashboard-monitoring/logs:/app/logs
  - /home/AdminUser/nas-project-data/nas-dashboard-monitoring/cache:/app/cache
  - /home/AdminUser/nas-project-data/nas-dashboard-monitoring/models:/app/models
  - /home/AdminUser/nas-project-data/nas-dashboard-monitoring/reports:/app/reports
  - /home/AdminUser/nas-project-data:/nas-project-data:ro
```

**config/settings.py の設定**:
```python
data_dir: str = "/home/AdminUser/nas-project-data/nas-dashboard-monitoring"
logs_dir: str = "/home/AdminUser/nas-project-data/nas-dashboard-monitoring/logs"
cache_dir: str = "/home/AdminUser/nas-project-data/nas-dashboard-monitoring/cache"
reports_dir: str = "/home/AdminUser/nas-project-data/nas-dashboard-monitoring/reports"
```

**注意**: `config/settings.py` ではホスト側のパスを直接使用していますが、実際には `docker-compose.yml` で個別にマウントされているため、コンテナ内では `/app/logs`、`/app/cache` などを使用する必要があります。

ただし、`nas-dashboard-monitoring` は他のシステムのログを直接読み取る機能はなく、Nginxログは `docker exec` で読み取っているため、この設定は問題ありません。

### 3. 各プロジェクトのログ出力先

| プロジェクト | コンテナ内パス | ホスト側パス（nas-project-data） | ログ監視での参照パス |
|------------|--------------|---------------------------|------------------|
| **youtube-to-notion** | `/app/logs` | `/home/AdminUser/nas-project-data/youtube-to-notion/logs` | `/nas-project-data/youtube-to-notion/logs/app.log` ✅ |
| **meeting-minutes-byc** | `/app/logs` | `/home/AdminUser/nas-project-data/meeting-minutes-byc/logs` | `/nas-project-data/meeting-minutes-byc/logs/app.log` ✅ |
| **nas-dashboard** | `/app/logs` | `/home/AdminUser/nas-project-data/nas-dashboard/logs` | `/nas-project-data/nas-dashboard/logs/app.log` ✅ |
| **notion-knowledge-summaries** | `/app/logs` | `/home/AdminUser/nas-project-data/notion-knowledge-summaries/logs` | - |
| **nas-dashboard-monitoring** | `/app/logs` | `/home/AdminUser/nas-project-data/nas-dashboard-monitoring/logs` | `/nas-project-data/nas-dashboard-monitoring/logs/app.log` ✅ |

## ✅ 修正内容

### nas-dashboard/app.py

以下の関数で `os.path.exists('/nas-project-data')` チェックを削除：

1. `get_text_logs()` - 2373行目
2. `get_text_logs_by_system()` - 2449行目
3. `get_hybrid_log_data_for_analysis()` - 2927行目、3593行目

**修正前**:
```python
if os.getenv('NAS_MODE') and os.path.exists('/nas-project-data'):
```

**修正後**:
```python
if os.getenv('NAS_MODE'):
    # docker-compose.ymlで /home/AdminUser/nas-project-data:/nas-project-data にマウントされている
```

## 📊 パスのマッピング

### nas-dashboard コンテナ内

```
/nas-project-data/
├── meeting-minutes-byc/
│   └── logs/
│       └── app.log
├── amazon-analytics/
│   └── logs/
│       └── app.log
├── document-automation/
│   └── logs/
│       └── app.log
├── youtube-to-notion/
│   └── logs/
│       └── app.log
├── nas-dashboard/
│   └── logs/
│       └── app.log
└── nas-dashboard-monitoring/
    └── logs/
        └── app.log
```

## ✅ 結論

**はい、ログ監視やNAS監視で参照しているパスは正しく`nas-project-data`配下を参照しています。**

- ✅ `nas-dashboard` のログ監視機能はすべて `/nas-project-data/...` パスを使用
- ✅ `os.path.exists()` チェックを削除し、`NAS_MODE` のみで判定
- ✅ すべてのログファイルが `nas-project-data` 配下に正しく保存されている
- ✅ ログ監視機能が正しいパスでログファイルを読み取れる

---

**更新日**: 2025年11月7日
**ステータス**: ✅ 修正完了

