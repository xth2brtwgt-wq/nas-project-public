# 環境同期ガイド

## 📋 概要

ローカル環境、NAS環境、Gitリポジトリ（mainブランチ）を同じ状態に保つための手順です。

## ✅ 現在の状態

- **ローカル環境**: `main` ブランチ、最新状態
- **Gitリポジトリ**: `main` ブランチにすべての変更がマージ済み
- **NAS環境**: `feature/monitoring-fail2ban-integration` ブランチを使用している可能性があります

## 🔄 環境統一手順

### 1. NAS環境での確認と切り替え

NAS環境で以下を実行してください：

```bash
# プロジェクトルートに移動
cd ~/nas-project

# 現在のブランチを確認
git branch

# mainブランチに切り替え
git checkout main

# 最新のmainブランチを取得
git pull origin main

# ブランチの状態を確認
git log --oneline -3
```

**期待される結果**:
- 最新コミット: `88fb2db Merge feature/monitoring-fail2ban-integration: UI統一とヘッダー修正、認証リダイレクト修正`

### 2. ローカル環境での確認

ローカル環境で以下を確認してください：

```bash
cd /Users/Yoshi/nas-project

# mainブランチにいることを確認
git branch

# 最新の状態を確認
git pull origin main

# 状態を確認
git status
```

**期待される結果**:
- `On branch main`
- `Your branch is up to date with 'origin/main'`
- `nothing to commit, working tree clean`

### 3. 今後開発する場合

新しい機能開発を開始する場合：

```bash
# mainブランチから新しいfeatureブランチを作成
git checkout main
git pull origin main
git checkout -b feature/新しい機能名

# 開発・コミット・プッシュ
git add .
git commit -m "feat: 新しい機能"
git push origin feature/新しい機能名

# 完了後、mainブランチにマージ
git checkout main
git pull origin main
git merge feature/新しい機能名
git push origin main
```

## 📝 注意事項

### NAS環境でのブランチ切り替え

NAS環境で `main` ブランチに切り替えた後、各システムを再ビルドする必要はありません（コードは同じです）。

ただし、以下の場合は再ビルドが必要です：
- 新しい変更をプルした場合
- テンプレートファイルや設定ファイルが変更された場合

### ブランチの削除（オプション）

`feature/monitoring-fail2ban-integration` ブランチは既に `main` にマージ済みなので、削除しても問題ありません：

```bash
# ローカル環境
git branch -d feature/monitoring-fail2ban-integration

# リモート環境
git push origin --delete feature/monitoring-fail2ban-integration
```

## ✅ 確認チェックリスト

- [ ] ローカル環境が `main` ブランチにいる
- [ ] ローカル環境が `origin/main` と同期している
- [ ] NAS環境が `main` ブランチに切り替えた
- [ ] NAS環境が `origin/main` と同期している
- [ ] 両環境の最新コミットが同じ（`88fb2db`）

