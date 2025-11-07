# 全プロジェクトの生成物をプロジェクト外に保存する修正

## 📋 概要

全プロジェクトで、ログファイルやその他の生成物（データ、キャッシュ、アップロードファイルなど）がプロジェクト内に保存されないように修正しました。
すべての生成物は`nas-project-data`に保存されるように統一しました。

## 🔍 修正対象プロジェクト

1. **amazon-analytics**
2. **youtube-to-notion**
3. **meeting-minutes-byc**
4. **document-automation**
5. **nas-dashboard**（既に修正済み）

## ✅ 修正内容

### 1. amazon-analytics

#### `app/api/main.py`
- ログディレクトリの設定をNAS環境対応に修正
- NAS環境では`/app/data/logs`を使用、ローカル環境では`./data/logs`を使用

#### `config/settings.py`
- `DATA_DIR`、`UPLOAD_DIR`、`PROCESSED_DIR`、`EXPORT_DIR`、`CACHE_DIR`をNAS環境対応に修正
- NAS環境では`/app/data`を使用、ローカル環境ではプロジェクト内の`data`ディレクトリを使用

### 2. youtube-to-notion

#### `app.py`
- ログディレクトリ（`LOG_DIR`）をNAS環境対応に修正
- アップロードディレクトリ（`UPLOAD_DIR`）をNAS環境対応に修正
- 出力ディレクトリ（`OUTPUT_DIR`）をNAS環境対応に修正
- キャッシュディレクトリ（`CACHE_DIR`）をNAS環境対応に修正
- NAS環境では`/app/logs`、`/app/data/uploads`などを使用、ローカル環境では相対パスを使用

### 3. meeting-minutes-byc

#### `app.py`
- ログディレクトリ（`LOG_DIR`）をNAS環境対応に修正
- アップロードディレクトリ（`UPLOAD_DIR`）をNAS環境対応に修正
- 転写データディレクトリ（`TRANSCRIPT_DIR`）をNAS環境対応に修正
- NAS環境では`/app/logs`、`/app/uploads`などを使用、ローカル環境では相対パスを使用

### 4. document-automation

#### `app/api/main.py`
- ログディレクトリの設定をNAS環境対応に修正
- NAS環境では`/app/logs`を使用、ローカル環境では`./logs`を使用

### 5. .gitignore

#### ルート`.gitignore`
以下の生成物ディレクトリ・ファイルを追加：
- `data/`、`uploads/`、`cache/`、`processed/`、`exports/`、`transcripts/`、`outputs/`、`backups/`、`reports/`、`db/`
- `*.db`、`*.sqlite`、`*.sqlite3`
- `build.log`

## 📋 修正パターン

### NAS環境判定

すべてのプロジェクトで、以下のパターンでNAS環境を判定しています：

```python
# NAS環境では統合データディレクトリを使用、ローカル環境では相対パスを使用
if os.getenv('NAS_MODE') and os.path.exists('/app/[ディレクトリ名]'):
    log_dir = os.getenv('LOG_DIR', '/app/logs')
else:
    log_dir = os.getenv('LOG_DIR', './logs')
```

### ディレクトリマウント（docker-compose.yml）

各プロジェクトの`docker-compose.yml`で、以下のようにマウントされています：

```yaml
volumes:
  - /home/AdminUser/nas-project-data/{プロジェクト名}/logs:/app/logs
  - /home/AdminUser/nas-project-data/{プロジェクト名}/uploads:/app/uploads
  - /home/AdminUser/nas-project-data/{プロジェクト名}/cache:/app/cache
  # ... その他のディレクトリ
```

## 🚀 デプロイ手順

### 1. ローカルで変更をコミット・プッシュ

```bash
cd /Users/Yoshi/nas-project
git add .
git commit -m "fix: 全プロジェクトの生成物をプロジェクト外に保存するように修正"
git push origin main
```

### 2. NAS環境で最新コードを取得

```bash
ssh -p 23456 AdminUser@192.168.68.110
cd ~/nas-project
git pull origin main
```

### 3. 既存の生成物をクリーンアップ

```bash
# 全プロジェクトのクリーンアップスクリプトを実行
~/nas-project/scripts/cleanup-all-projects.sh

# または、個別にクリーンアップ
# amazon-analytics
cd ~/nas-project/amazon-analytics
rm -rf data/ logs/ 2>/dev/null || true

# youtube-to-notion
cd ~/nas-project/youtube-to-notion
rm -rf data/ logs/ 2>/dev/null || true

# meeting-minutes-byc
cd ~/nas-project/meeting-minutes-byc
rm -rf logs/ uploads/ transcripts/ 2>/dev/null || true

# document-automation
cd ~/nas-project/document-automation
rm -rf logs/ 2>/dev/null || true
```

### 4. 各プロジェクトを再デプロイ

```bash
# amazon-analytics
cd ~/nas-project/amazon-analytics
docker compose down
docker compose up -d --build

# youtube-to-notion
cd ~/nas-project/youtube-to-notion
docker compose down
docker compose up -d --build

# meeting-minutes-byc
cd ~/nas-project/meeting-minutes-byc
docker compose down
docker compose up -d --build

# document-automation
cd ~/nas-project/document-automation
docker compose down
docker compose up -d --build
```

### 5. 容量確認

```bash
~/nas-project/scripts/check-disk-usage.sh
```

## 📊 確認項目

### 修正後の確認

1. **プロジェクト内に生成物がないことを確認**
   ```bash
   # 各プロジェクトで確認
   find ~/nas-project/amazon-analytics -name "*.log" -o -name "*.db" -o -type d -name "data" -o -type d -name "logs"
   find ~/nas-project/youtube-to-notion -name "*.log" -o -type d -name "data" -o -type d -name "logs"
   find ~/nas-project/meeting-minutes-byc -name "*.log" -o -type d -name "logs" -o -type d -name "uploads"
   find ~/nas-project/document-automation -name "*.log" -o -type d -name "logs"
   ```

2. **統合データディレクトリに正しく保存されていることを確認**
   ```bash
   ls -lh /home/AdminUser/nas-project-data/amazon-analytics/
   ls -lh /home/AdminUser/nas-project-data/youtube-to-notion/
   ls -lh /home/AdminUser/nas-project-data/meeting-minutes-byc/
   ls -lh /home/AdminUser/nas-project-data/document-automation/
   ```

3. **コンテナのログを確認**
   ```bash
   docker logs amazon-analytics-web
   docker logs youtube-to-notion
   docker logs meeting-minutes-byc
   docker logs doc-automation-web
   ```

## 📋 チェックリスト

- [x] amazon-analytics/app/api/main.py の修正
- [x] amazon-analytics/config/settings.py の修正
- [x] youtube-to-notion/app.py の修正
- [x] meeting-minutes-byc/app.py の修正
- [x] document-automation/app/api/main.py の修正
- [x] .gitignore の更新
- [x] 全プロジェクトのクリーンアップスクリプトの作成
- [x] ローカルで変更をコミット・プッシュ
- [x] NAS環境で`git pull`を実行（完了）
- [x] 各プロジェクトの再デプロイ（完了）
- [x] コード修正の確認（完了 - 修正が反映されている）
- [ ] 既存生成物のクリーンアップ
- [ ] デプロイ後の確認スクリプトを実行（git pull後に実行）
- [ ] 容量確認スクリプトの実行
- [ ] プロジェクト内に生成物がないことを確認
- [ ] 統合データディレクトリに正しく保存されていることを確認

## 🔗 関連ドキュメント

- [データ管理ルール](../../DATA_MANAGEMENT_RULES.md)
- [NAS環境デプロイ仕様書](./NAS_DEPLOYMENT_SPECIFICATION.md)
- [nas-dashboard容量増加問題の修正](./DISK_USAGE_FIX.md)

---

**作成日**: 2025年1月27日
**対象**: 全NAS環境プロジェクト
**更新**: 必要に応じて更新

