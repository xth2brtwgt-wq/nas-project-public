# NAS環境での確認とクリーンアップ手順

## 📋 概要

NAS環境で最新コードを取得し、プロジェクトフォルダ内の生成物を確認・クリーンアップします。

## 🚀 手順

### 1. NAS環境にSSH接続

```bash
ssh -p 23456 AdminUser@192.168.68.110
```

### 2. 最新コードを取得

```bash
cd ~/nas-project
git pull origin main
```

### 3. プロジェクトフォルダ内の生成物を確認

```bash
# 確認スクリプトを実行
./scripts/check-nas-project-clean.sh
```

または、手動で確認：

```bash
# ログファイルを検索
find . -type f \( -name "*.log" -o -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3" \) 2>/dev/null | grep -v ".git" | grep -v "node_modules" | grep -v "venv"

# 生成物ディレクトリを検索
find . -type d \( -name "logs" -o -name "data" -o -name "uploads" -o -name "cache" -o -name "processed" -o -name "exports" -o -name "transcripts" -o -name "outputs" -o -name "backups" -o -name "reports" \) 2>/dev/null | grep -v ".git" | grep -v "node_modules" | grep -v "venv" | sort

# 各プロジェクトの容量を確認
du -sh nas-dashboard youtube-to-notion meeting-minutes-byc document-automation amazon-analytics notion-knowledge-summaries nas-dashboard-monitoring 2>/dev/null
```

### 4. 生成物が見つかった場合のクリーンアップ

```bash
# 各プロジェクトの生成物を削除
cd ~/nas-project

# nas-dashboard
rm -rf nas-dashboard/logs nas-dashboard/data

# youtube-to-notion
rm -rf youtube-to-notion/logs youtube-to-notion/data

# meeting-minutes-byc
rm -rf meeting-minutes-byc/logs meeting-minutes-byc/uploads meeting-minutes-byc/transcripts

# document-automation
rm -rf document-automation/logs document-automation/data

# amazon-analytics
rm -rf amazon-analytics/data

# notion-knowledge-summaries
rm -rf notion-knowledge-summaries/logs notion-knowledge-summaries/data

# nas-dashboard-monitoring
rm -rf nas-dashboard-monitoring/local-data
```

### 5. 各プロジェクトを再デプロイ

```bash
# nas-dashboard
cd ~/nas-project/nas-dashboard
docker compose up -d --build

# youtube-to-notion
cd ~/nas-project/youtube-to-notion
docker compose up -d --build

# meeting-minutes-byc
cd ~/nas-project/meeting-minutes-byc
docker compose up -d --build

# document-automation
cd ~/nas-project/document-automation
docker compose up -d --build

# amazon-analytics
cd ~/nas-project/amazon-analytics
docker compose up -d --build

# notion-knowledge-summaries
cd ~/nas-project/notion-knowledge-summaries
docker compose up -d --build

# nas-dashboard-monitoring
cd ~/nas-project/nas-dashboard-monitoring
docker compose up -d --build
```

### 6. 再確認

```bash
# 再度確認スクリプトを実行
cd ~/nas-project
./scripts/check-nas-project-clean.sh

# nas-project-data配下に正しく保存されていることを確認
ls -lh ~/nas-project-data/*/logs/ 2>/dev/null
```

## 📋 チェックリスト

- [ ] NAS環境にSSH接続
- [ ] `git pull origin main` を実行
- [ ] プロジェクトフォルダ内の生成物を確認
- [ ] 生成物があれば削除
- [ ] 各プロジェクトを再デプロイ
- [ ] 再確認して生成物が作成されていないことを確認
- [ ] `nas-project-data`配下に正しく保存されていることを確認

---

**更新日**: 2025年11月7日

