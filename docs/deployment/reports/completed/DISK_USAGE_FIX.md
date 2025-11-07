# NAS環境の容量増加問題の修正

## 📋 問題の概要

NAS環境で`nas-dashboard`全体の容量が急激に増加している問題を確認しました。
データは`nas-project-data`に保存される想定ですが、ログファイルがプロジェクトディレクトリ内に保存されていました。

## 🔍 原因

1. **`nas-dashboard/docker-compose.yml`の設定問題**
   - `./logs:/app/logs` がプロジェクトディレクトリ内にログを保存していた
   - 本来は `/home/AdminUser/nas-project-data/nas-dashboard/logs:/app/logs` にすべき

2. **`nas-dashboard/app.py`のログ設定問題**
   - デフォルトで `./logs` を使用していた
   - NAS環境では `/nas-project-data/nas-dashboard/logs` を使用すべき

## ✅ 修正内容

### 1. `nas-dashboard/docker-compose.yml`の修正

**修正前:**
```yaml
volumes:
  # ログディレクトリ
  - ./logs:/app/logs
```

**修正後:**
```yaml
volumes:
  # ログディレクトリ
  - /home/AdminUser/nas-project-data/nas-dashboard/logs:/app/logs
```

### 2. `nas-dashboard/app.py`の修正

**修正前:**
```python
# ログ設定
log_dir = os.getenv('LOG_DIR', './logs')
os.makedirs(log_dir, exist_ok=True)
```

**修正後:**
```python
# ログ設定
# NAS環境では統合データディレクトリを使用、ローカル環境では./logsを使用
if os.getenv('NAS_MODE') and os.path.exists('/nas-project-data'):
    log_dir = os.getenv('LOG_DIR', '/nas-project-data/nas-dashboard/logs')
else:
    log_dir = os.getenv('LOG_DIR', './logs')
os.makedirs(log_dir, exist_ok=True)
```

### 3. 容量確認スクリプトの作成

`scripts/check-disk-usage.sh` を作成しました。
このスクリプトで以下を確認できます：

- プロジェクトディレクトリ（nas-project）の使用量
- データディレクトリ（nas-project-data）の使用量
- プロジェクトディレクトリ内のログファイル（不適切な場所）
- Dockerボリュームの確認
- 大きなファイル・ディレクトリの特定

## 🚀 デプロイ手順

### 1. ローカルで変更をコミット・プッシュ

```bash
# ローカル環境で実行
cd /Users/Yoshi/nas-project

# 変更を確認
git status

# 変更をコミット
git add nas-dashboard/docker-compose.yml nas-dashboard/app.py scripts/check-disk-usage.sh docs/deployment/DISK_USAGE_FIX.md
git commit -m "fix: nas-dashboardのログをnas-project-dataに保存するように修正"

# リモートにプッシュ
git push origin main
```

### 2. NAS環境で最新コードを取得

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# プロジェクトディレクトリに移動
cd ~/nas-project

# 最新のコードを取得
git pull origin main
```

### 3. 既存のログファイルの移行

```bash
# NAS環境で実行
cd /home/AdminUser/nas-project/nas-dashboard

# 既存のログファイルを確認
ls -lh logs/

# ログファイルを統合データディレクトリに移行
mkdir -p /home/AdminUser/nas-project-data/nas-dashboard/logs
mv logs/* /home/AdminUser/nas-project-data/nas-dashboard/logs/ 2>/dev/null || true

# プロジェクト内のログディレクトリを削除（空の場合のみ）
rmdir logs 2>/dev/null || true
```

### 4. コンテナの再デプロイ

```bash
# nas-dashboardの再デプロイ
cd /home/AdminUser/nas-project/nas-dashboard

# デプロイスクリプトを実行（git pullが含まれている）
./deploy.sh

# または、手動で実行する場合
# docker compose down
# docker compose up -d --build
```

**重要**: コード変更がある場合は、`docker compose up -d --build`でイメージを再ビルドする必要があります。
`docker compose restart`だけでは最新コードが反映されません。

### 5. 容量確認

```bash
# 容量確認スクリプトを実行
~/nas-project/scripts/check-disk-usage.sh
```

### 6. 残りのログファイルのクリーンアップ

```bash
# プロジェクト内の残りのログファイルをクリーンアップ
cd ~/nas-project/nas-dashboard

# build.logを削除（ビルド時に生成される一時ファイル）
rm -f build.log

# 空のlogsディレクトリを削除
rmdir logs 2>/dev/null || true

# その他のログファイルを確認
find ~/nas-project/nas-dashboard -name "*.log" -type f

# または、クリーンアップスクリプトを使用
~/nas-project/scripts/cleanup-nas-dashboard-logs.sh
```

## 📊 確認項目

### 修正後の確認

1. **ログファイルの場所確認**
   ```bash
   # プロジェクト内にログファイルがないことを確認
   find /home/AdminUser/nas-project/nas-dashboard -name "*.log" -type f
   
   # 統合データディレクトリにログファイルがあることを確認
   ls -lh /home/AdminUser/nas-project-data/nas-dashboard/logs/
   ```

2. **容量の確認**
   ```bash
   # プロジェクトディレクトリの容量
   du -sh /home/AdminUser/nas-project/nas-dashboard
   
   # データディレクトリの容量
   du -sh /home/AdminUser/nas-project-data/nas-dashboard
   ```

3. **コンテナの動作確認**
   ```bash
   # コンテナのログを確認
   docker logs nas-dashboard
   
   # ログファイルが正しく書き込まれているか確認
   tail -f /home/AdminUser/nas-project-data/nas-dashboard/logs/app.log
   ```

## ⚠️ 注意事項

### `nas-dashboard-monitoring`のDockerボリューム

`nas-dashboard-monitoring`では、PostgreSQLとRedisが名前付きボリューム（`postgres-data`、`redis-data`）を使用しています。
これらはDockerのデフォルトの場所（`/var/lib/docker/volumes/`）に保存されます。

現在の設定では、これらは名前付きボリュームとして管理されているため、通常は問題ありません。
ただし、容量増加の原因になっている可能性がある場合は、明示的に`nas-project-data`にマウントすることを検討してください。

### 既存データの移行

既存のログファイルがプロジェクトディレクトリ内に大量にある場合は、移行が必要です。
移行前にバックアップを取ることを推奨します。

## 📋 チェックリスト

- [x] `nas-dashboard/docker-compose.yml`の修正
- [x] `nas-dashboard/app.py`の修正
- [x] 容量確認スクリプトの作成
- [ ] ローカルで変更をコミット・プッシュ
- [ ] NAS環境で`git pull`を実行
- [ ] 既存ログファイルの移行（NAS環境で実行）
- [ ] コンテナの再デプロイ（`docker compose up -d --build`）
- [ ] 容量確認スクリプトの実行
- [ ] ログファイルの場所確認
- [ ] コンテナの動作確認

## 🔗 関連ドキュメント

- [データ管理ルール](../../DATA_MANAGEMENT_RULES.md)
- [NAS環境デプロイ仕様書](./NAS_DEPLOYMENT_SPECIFICATION.md)

---

**作成日**: 2025年1月27日
**対象**: NAS環境の`nas-dashboard`プロジェクト
**更新**: 必要に応じて更新

