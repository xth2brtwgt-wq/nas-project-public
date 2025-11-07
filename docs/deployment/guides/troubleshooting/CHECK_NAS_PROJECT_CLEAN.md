# NAS環境でのnas-projectフォルダ内の生成物確認

## 📋 概要

NAS環境で`nas-project`フォルダ内に生成物（ログ、データ、キャッシュなど）が残っていないか、新たに作成されていないかを確認します。

## 🔍 確認方法

### 1. 確認スクリプトの実行

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# 確認スクリプトを実行
cd ~/nas-project
./scripts/check-nas-project-clean.sh
```

### 2. 手動確認コマンド

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# 各プロジェクトの生成物を確認
cd ~/nas-project

# ログファイルを検索
find . -type f -name "*.log" -o -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3" 2>/dev/null | grep -v ".git" | grep -v "node_modules"

# 生成物ディレクトリを検索
find . -type d \( -name "logs" -o -name "data" -o -name "uploads" -o -name "cache" -o -name "processed" -o -name "exports" -o -name "transcripts" -o -name "outputs" -o -name "backups" -o -name "reports" \) 2>/dev/null | grep -v ".git" | grep -v "node_modules" | sort

# 各プロジェクトの容量を確認
du -sh nas-dashboard youtube-to-notion meeting-minutes-byc document-automation amazon-analytics notion-knowledge-summaries nas-dashboard-monitoring 2>/dev/null
```

## ✅ 確認対象

### 確認対象のプロジェクト

- `nas-dashboard`
- `youtube-to-notion`
- `meeting-minutes-byc`
- `document-automation`
- `amazon-analytics`
- `notion-knowledge-summaries`
- `nas-dashboard-monitoring`

### 確認対象の生成物

- **ログファイル**: `logs/`, `*.log`
- **データファイル**: `data/`, `*.db`, `*.sqlite`, `*.sqlite3`
- **アップロードファイル**: `uploads/`
- **キャッシュ**: `cache/`
- **処理済みファイル**: `processed/`
- **エクスポートファイル**: `exports/`
- **転写ファイル**: `transcripts/`
- **出力ファイル**: `outputs/`
- **バックアップ**: `backups/`
- **レポート**: `reports/`

## 📊 期待される結果

### ✅ 正常な状態

各プロジェクトフォルダ内に生成物が存在しない状態：

```
📁 nas-dashboard:
  ✅ 生成物なし

📁 youtube-to-notion:
  ✅ 生成物なし

📁 meeting-minutes-byc:
  ✅ 生成物なし

📁 document-automation:
  ✅ 生成物なし

📁 amazon-analytics:
  ✅ 生成物なし

📁 notion-knowledge-summaries:
  ✅ 生成物なし

📁 nas-dashboard-monitoring:
  ✅ 生成物なし
```

### ❌ 問題がある状態

生成物が残っている場合：

```
📁 nas-dashboard:
  ❌ logs/: 28K
  ❌ data/: 1.2M

📁 youtube-to-notion:
  ❌ logs/: 2.1M
  ❌ data/: 150M
```

## 🔧 問題が見つかった場合の対処

### 1. 生成物の削除

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

### 2. コンテナの再デプロイ

生成物を削除した後、各プロジェクトを再デプロイして、正しい場所（`nas-project-data`）に生成物が保存されることを確認します。

```bash
# 各プロジェクトを再デプロイ
cd ~/nas-project/nas-dashboard
docker compose up -d --build

cd ~/nas-project/youtube-to-notion
docker compose up -d --build

cd ~/nas-project/meeting-minutes-byc
docker compose up -d --build

# ... 他のプロジェクトも同様に
```

### 3. 確認

再デプロイ後、再度確認スクリプトを実行して、生成物が作成されていないことを確認します。

## 📋 チェックリスト

- [ ] 確認スクリプトを実行
- [ ] 各プロジェクトに生成物がないことを確認
- [ ] もし生成物があれば削除
- [ ] 各プロジェクトを再デプロイ
- [ ] 再確認して生成物が作成されていないことを確認
- [ ] `nas-project-data`配下に正しく保存されていることを確認

---

**更新日**: 2025年11月7日
**ステータス**: 確認スクリプト作成完了

