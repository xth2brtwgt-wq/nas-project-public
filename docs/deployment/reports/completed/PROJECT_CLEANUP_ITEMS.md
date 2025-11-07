# nas-projectフォルダ配下の容量を占めるファイル一覧

## 📋 概要

`nas-project`フォルダ配下で容量を占めているファイル・ディレクトリを確認し、クリーンアップが必要な項目を特定しました。

## 🔍 確認した項目

### 1. プロジェクト内のデータディレクトリ（削除・移動が必要）

#### **youtube-to-notion/data/** ⚠️
- **場所**: `/home/AdminUser/nas-project/youtube-to-notion/data/`
- **内容**: 
  - `uploads/` - 13個のmp3ファイル（YouTube音声データ）
  - `cache/`
  - `outputs/`
- **問題**: プロジェクト内にデータが保存されている
- **対応**: `nas-project-data/youtube-to-notion/`に移動済み（docker-compose.ymlでマウント済み）
- **クリーンアップ**: プロジェクト内の`data/`ディレクトリを削除

#### **meeting-minutes-byc/uploads/** ⚠️
- **場所**: `/home/AdminUser/nas-project/meeting-minutes-byc/uploads/`
- **問題**: プロジェクト内にuploadsディレクトリがある
- **対応**: `nas-project-data/meeting-minutes-byc/uploads/`に移動済み（docker-compose.ymlでマウント済み）
- **クリーンアップ**: プロジェクト内の`uploads/`ディレクトリを削除

#### **nas-dashboard/data/** ⚠️
- **場所**: `/home/AdminUser/nas-project/nas-dashboard/data/`
- **内容**: `auth.db`（認証データベース）
- **問題**: プロジェクト内にデータベースファイルがある
- **対応**: `nas-project-data/nas-dashboard/auth.db`に移動済み（docker-compose.ymlでマウント済み）
- **クリーンアップ**: プロジェクト内の`data/`ディレクトリを削除

#### **nas-dashboard/logs/** ⚠️
- **場所**: `/home/AdminUser/nas-project/nas-dashboard/logs/`
- **内容**: `app.log`, `monthly_ai_report.log`
- **問題**: プロジェクト内にログファイルがある（既に修正済み）
- **対応**: `nas-project-data/nas-dashboard/logs/`に移動済み（docker-compose.ymlでマウント済み）
- **クリーンアップ**: プロジェクト内の`logs/`ディレクトリを削除

#### **youtube-to-notion/logs/** ⚠️
- **場所**: `/home/AdminUser/nas-project/youtube-to-notion/logs/`
- **内容**: `app.log`
- **問題**: プロジェクト内にログファイルがある（既に修正済み）
- **対応**: `nas-project-data/youtube-to-notion/logs/`に移動済み（docker-compose.ymlでマウント済み）
- **クリーンアップ**: プロジェクト内の`logs/`ディレクトリを削除

### 2. Python関連のキャッシュ・生成物（削除可能）

#### **__pycache__/** ディレクトリ
- **場所**: 各プロジェクトの`__pycache__/`ディレクトリ
- **内容**: Pythonのコンパイル済みファイル（.pyc）
- **問題**: 実行時に自動生成されるため、Git管理不要
- **対応**: `.gitignore`に追加済み
- **クリーンアップ**: 全プロジェクトの`__pycache__/`を削除可能

#### **.pycファイル**
- **場所**: 各プロジェクトの`.pyc`ファイル
- **問題**: Pythonのコンパイル済みファイル
- **対応**: `.gitignore`に追加済み
- **クリーンアップ**: 全プロジェクトの`.pyc`ファイルを削除可能

### 3. 仮想環境（venv）- NAS環境では不要

#### **venv/** ディレクトリ（もしあれば）
- **場所**: 各プロジェクトの`venv/`ディレクトリ
- **問題**: NAS環境ではDockerコンテナ内で実行されるため、仮想環境は不要
- **対応**: `.gitignore`に追加済み
- **クリーンアップ**: 全プロジェクトの`venv/`ディレクトリを削除可能

### 4. ドキュメントディレクトリ（確認が必要）

#### **docs/** ディレクトリ
- **場所**: `/home/AdminUser/nas-project/docs/`
- **内容**: プロジェクトのドキュメント
- **問題**: 通常は容量を占めないが、大量のドキュメントがある場合は確認が必要
- **対応**: 必要に応じて整理

### 5. Gitリポジトリ

#### **.git/** ディレクトリ
- **場所**: `/home/AdminUser/nas-project/.git/`
- **問題**: Gitリポジトリの履歴データ（通常は必要）
- **対応**: 通常は削除しない（必要に応じて履歴をクリーンアップ）

## 🚀 クリーンアップ手順

### 1. プロジェクト内のデータディレクトリを削除

```bash
# NAS環境で実行
cd ~/nas-project

# youtube-to-notion/data を削除（既にnas-project-dataに移動済み）
rm -rf youtube-to-notion/data

# meeting-minutes-byc/uploads を削除（既にnas-project-dataに移動済み）
rm -rf meeting-minutes-byc/uploads

# nas-dashboard/data を削除（既にnas-project-dataに移動済み）
rm -rf nas-dashboard/data

# nas-dashboard/logs を削除（既にnas-project-dataに移動済み）
rm -rf nas-dashboard/logs

# youtube-to-notion/logs を削除（既にnas-project-dataに移動済み）
rm -rf youtube-to-notion/logs
```

### 2. Pythonキャッシュを削除

```bash
# 全プロジェクトの__pycache__を削除
find ~/nas-project -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 全プロジェクトの.pycファイルを削除
find ~/nas-project -type f -name "*.pyc" -delete 2>/dev/null || true

# 全プロジェクトの.pyoファイルを削除
find ~/nas-project -type f -name "*.pyo" -delete 2>/dev/null || true
```

### 3. 仮想環境を削除（もしあれば）

```bash
# 全プロジェクトのvenvを削除
find ~/nas-project -type d \( -name "venv" -o -name ".venv" -o -name "env" \) -exec rm -rf {} + 2>/dev/null || true
```

### 4. クリーンアップスクリプトの実行

```bash
# 全プロジェクトのクリーンアップスクリプトを実行
~/nas-project/scripts/cleanup-all-projects.sh
```

### 5. 容量確認

```bash
# 容量確認スクリプトを実行
~/nas-project/scripts/analyze-project-size.sh
```

## 📊 容量削減の見込み

### 削除可能な項目

1. **youtube-to-notion/data/uploads**: 13個のmp3ファイル（推定: 数MB〜数十MB）
2. **各種__pycache__**: 数MB〜数十MB
3. **各種.pycファイル**: 数MB
4. **venv（もしあれば）**: 数百MB〜数GB

### 削減後の期待値

- **プロジェクトディレクトリ**: ソースコードのみ（数MB〜数十MB）
- **データディレクトリ**: `nas-project-data`に一元管理

## ⚠️ 注意事項

### 削除前に確認

1. **データディレクトリの削除**
   - 削除前に`nas-project-data`にデータが正しく移動されていることを確認
   - 必要に応じてバックアップを取得

2. **Pythonキャッシュの削除**
   - 削除しても問題なし（実行時に自動再生成される）

3. **仮想環境の削除**
   - NAS環境ではDockerコンテナ内で実行されるため不要
   - ローカル開発環境では必要に応じて再作成

## 📋 チェックリスト

- [ ] プロジェクト内のデータディレクトリを削除
- [ ] Pythonキャッシュ（__pycache__、.pyc）を削除
- [ ] 仮想環境（venv）を削除（もしあれば）
- [ ] 容量確認スクリプトを実行
- [ ] 容量削減を確認

## 🔗 関連ドキュメント

- [データ管理ルール](../../DATA_MANAGEMENT_RULES.md)
- [全プロジェクトの生成物をプロジェクト外に保存する修正](./ALL_PROJECTS_DATA_EXTERNAL_FIX.md)
- [容量増加問題の修正](./DISK_USAGE_FIX.md)

---

**作成日**: 2025年1月27日
**対象**: 全NAS環境プロジェクト
**更新**: 必要に応じて更新

