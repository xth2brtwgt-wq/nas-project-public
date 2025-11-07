# 自動バージョン管理システム

## 📋 概要

nas-project内の全プロジェクトで、Gitコミット時に自動的にバージョン番号を更新する仕組みです。

## 🎯 対応プロジェクト

以下のプロジェクトで自動バージョンアップが有効です：

- ✅ **amazon-analytics** - `config/version.py` (VERSION形式)
- ✅ **document-automation** - `config/version.py` (VERSION形式)
- ✅ **meeting-minutes-byc** - `config/version.py` (APP_VERSION形式)
- ✅ **nas-dashboard** - `version.py` (__version__形式)
- ✅ **nas-dashboard-monitoring** - `config/version.py` (APP_VERSION形式)
- ✅ **youtube-to-notion** - `config/version.py` (APP_VERSION形式)

## 🔧 セットアップ

### ローカル環境（各プロジェクトが個別Gitリポジトリ）

```bash
cd /Users/Yoshi/nas-project
./scripts/setup-hooks-all-projects.sh
```

### NAS環境（ルートリポジトリで管理）

NAS環境では、全プロジェクトが親リポジトリ（nas-project）のサブディレクトリとして管理されているため、ルートレベルのhooksを設定します：

```bash
cd ~/nas-project
./scripts/setup-hooks-root-level.sh
```

### 個別プロジェクトのセットアップ

各プロジェクトが個別のGitリポジトリとして管理されている場合：

```bash
cd /path/to/project
./scripts/setup-hooks.sh  # プロジェクト固有のセットアップスクリプトがあれば
```

## 📝 使用方法

### 自動バージョンアップ

通常通りコミットするだけで、自動的にバージョンが更新されます：

```bash
git add .
git commit -m "feat: 新機能を追加"
# → 自動的にマイナーバージョンアップ（例: 1.5.0 → 1.6.0）
```

### バージョンアップタイプの判定

コミットメッセージから自動判定されます：

- **`feat:` または `feature`** → マイナーバージョンアップ（1.5.0 → 1.6.0）
- **`fix:` または `修正`** → パッチバージョンアップ（1.5.0 → 1.5.1）
- **`breaking` または `破壊的変更`** → メジャーバージョンアップ（1.5.0 → 2.0.0）
- **その他** → パッチバージョンアップ（1.5.0 → 1.5.1）

### 手動でバージョンタイプを指定

```bash
# マイナーバージョンアップを強制
python3 scripts/auto_version_update_universal.py minor

# メジャーバージョンアップを強制
python3 scripts/auto_version_update_universal.py major
```

## 🔍 仕組み

### 1. コミット前フック（pre-commit）

`.git/hooks/pre-commit`が自動的に実行されます：

1. バージョンファイルが既に変更されている場合はスキップ
2. `scripts/auto_version_update_universal.py`を実行
3. バージョンファイルが更新された場合は自動的にステージングに追加

### 2. 汎用スクリプト

`scripts/auto_version_update_universal.py`が以下を実行：

1. プロジェクト内のバージョンファイルを検出
2. バージョン形式（APP_VERSION / VERSION / __version__）を自動判定
3. VERSION_HISTORY形式（辞書 / リスト）を自動判定
4. コミットメッセージからバージョンアップタイプを判定
5. バージョンを更新し、履歴に追加

## 📂 ファイル構成

```
nas-project/
├── scripts/
│   ├── auto_version_update_universal.py  # 汎用自動バージョンアップスクリプト
│   └── setup-hooks-all-projects.sh      # 全プロジェクトhooksセットアップスクリプト
├── meeting-minutes-byc/
│   ├── hooks/
│   │   └── pre-commit                    # テンプレート（参考用）
│   └── .git/hooks/pre-commit             # 実際のフック（自動生成）
└── ...
```

## ⚠️ 注意事項

### Git hooksは自動でコピーされない

Git hooks（`.git/hooks/`）はGitで管理されないため、新しい環境でリポジトリをクローンした場合、手動でセットアップが必要です：

```bash
# NAS環境など、新しい環境で
cd ~/nas-project
./scripts/setup-hooks-all-projects.sh
```

### バージョンファイルが既に変更されている場合

バージョンファイルが既にステージングされている場合、自動バージョンアップはスキップされます。これは、手動でバージョンを更新した場合を考慮しています。

### コミットメッセージの形式

推奨されるコミットメッセージ形式：

```
feat: 新機能を追加
fix: バグを修正
chore: 設定を更新
docs: ドキュメントを更新
```

プレフィックス（`feat:`, `fix:`など）があると、バージョンアップタイプが正確に判定されます。

## 🚨 トラブルシューティング

### バージョンファイルがコミットされていない場合

#### 問題の症状

- ローカルには新しいバージョン（例：1.7.3）があるが、NAS環境には古いバージョン（例：1.6.0）が表示される
- 画面のバージョン表示が更新されない

#### 原因

pre-commitフックでバージョンが自動更新され、ステージングに追加されたが、コミットに含まれなかった場合に発生します。

#### 確認方法

```bash
# 1. 未コミットのバージョンファイルを確認
git status meeting-minutes-byc/config/version.py

# 2. 最新のコミットにバージョンファイルが含まれているか確認
git show HEAD --name-only | grep version

# 3. ローカルとリモートのバージョンを比較
git show HEAD:meeting-minutes-byc/config/version.py | grep APP_VERSION
cat meeting-minutes-byc/config/version.py | grep APP_VERSION
```

#### 対処法

**方法1: バージョンファイルを明示的にコミット**

```bash
# 1. バージョンファイルをステージング
git add meeting-minutes-byc/config/version.py

# 2. コミット
git commit -m "chore: バージョンを1.7.3に更新"

# 3. プッシュ
git push origin main

# 4. NAS環境で最新を取得
ssh -p 23456 AdminUser@192.168.68.110 "cd ~/nas-project/meeting-minutes-byc && git pull origin main && docker compose restart meeting-minutes-byc"
```

**方法2: コミット履歴を確認して修正**

```bash
# 1. バージョンファイルのコミット履歴を確認
git log --oneline --all meeting-minutes-byc/config/version.py

# 2. 最新のコミットにバージョンファイルが含まれているか確認
git show HEAD --name-only | grep version

# 3. 含まれていない場合、明示的にコミット
git add meeting-minutes-byc/config/version.py
git commit -m "chore: バージョンを更新"
git push origin main
```

#### 予防策

コミット前に必ず以下を確認：

```bash
# コミット前にステージングされているファイルを確認
git status

# バージョンファイルが含まれているか確認
git diff --cached meeting-minutes-byc/config/version.py
```

### 次回の修正時にバージョンがどうなるか

バージョンファイルがコミットされていない場合、次回の修正時には以下のようになります：

1. **ローカルのバージョン（例：1.7.3）からさらにインクリメント**
   - pre-commitフックが現在のバージョン（1.7.3）を読み取り、さらにインクリメント（1.7.4）
   - リモートのバージョン（1.6.0）はスキップされる

2. **`git pull`した場合**
   - リモートの古いバージョン（1.6.0）とローカルの新しいバージョン（1.7.3）が競合する可能性がある
   - 手動で競合を解決する必要がある

**推奨**: バージョンファイルがコミットされていない場合は、次回の修正前に明示的にコミットしてください。

## 🔄 他の環境への展開

### NAS環境でのセットアップ

NAS環境では、ルートレベルのhooksを使用します：

```bash
# NASにSSH接続後
cd ~/nas-project
git pull origin main  # 最新のスクリプトを取得
./scripts/setup-hooks-root-level.sh
```

**注意**: NAS環境では、各プロジェクトがサブディレクトリとして管理されているため、`setup-hooks-root-level.sh`を使用します。

### 新しい開発マシンでのセットアップ

```bash
# リポジトリをクローン後
git clone <repository-url> nas-project
cd nas-project
./scripts/setup-hooks-all-projects.sh
```

## 📚 関連ドキュメント

- [VERSION_MANAGEMENT.md](../../VERSION_MANAGEMENT.md) - バージョン管理の詳細
- [DEPLOYMENT_RULES.md](../../DEPLOYMENT_RULES.md) - デプロイメントルール

