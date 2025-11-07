# Git履歴から.envファイルを削除する手順

## ⚠️ 警告

この操作は**破壊的**です：
- すべてのブランチの履歴が書き換えられます
- リモートにpushするには`force push`が必要です
- チームで共有している場合は全員に通知が必要です

## 📋 前提条件

### 1. バックアップの作成

```bash
# リモートリポジトリの完全バックアップを作成
cd ~
git clone --mirror https://github.com/xth2brtwgt-wq/dpx2800-nas-system.git nas-project-backup.git
```

### 2. 作業ブランチの確認

```bash
cd ~/nas-project
git branch -a
```

## 🔧 方法1: git filter-repo（推奨）

### インストール（必要な場合）

```bash
# macOS
brew install git-filter-repo

# または pip
pip install git-filter-repo
```

### 実行

```bash
cd ~/nas-project

# 履歴から.envファイルを削除
git filter-repo --path-glob '*.env' --invert-paths

# または特定のパスのみ
git filter-repo \
  --path amazon-analytics/.env \
  --path document-automation/.env \
  --path nas-dashboard/.env \
  --path insta360-auto-sync/.env \
  --path notion-knowledge-summaries/.env \
  --path youtube-to-notion/.env \
  --path docker/fail2ban/.env \
  --invert-paths
```

## 🔧 方法2: git filter-branch（標準ツール）

### 実行

```bash
cd ~/nas-project

# すべての.envファイルを履歴から削除
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch amazon-analytics/.env \
                                      document-automation/.env \
                                      nas-dashboard/.env \
                                      insta360-auto-sync/.env \
                                      notion-knowledge-summaries/.env \
                                      youtube-to-notion/.env \
                                      docker/fail2ban/.env" \
  --prune-empty --tag-name-filter cat -- --all

# 一時ファイルを削除
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

## ✅ 確認

```bash
# 履歴に.envファイルが残っていないか確認
git log --all --full-history --pretty=format: --name-only -- "*.env" | sort -u | grep -E "\.env$"

# 結果が空なら成功
```

## 🚀 リモートに反映

```bash
# ⚠️ 注意: force pushが必要です
git push origin --force --all
git push origin --force --tags
```

## 📝 注意事項

1. **全員に通知**: チームメンバーに履歴の書き換えを通知
2. **再クローン**: チームメンバーはリポジトリを再クローンする必要があります
3. **バックアップ**: 必ずバックアップを取っておくこと

