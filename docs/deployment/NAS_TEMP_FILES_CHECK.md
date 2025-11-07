# NAS環境での一時的なバックアップファイルやテスト用ファイルの確認

## 📋 概要

NAS環境で一時的なバックアップファイルやテスト用ファイルを確認します。

## 🔍 確認方法

### 1. 確認スクリプトの実行

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# 確認スクリプトを実行
cd ~/nas-project
./scripts/check-temp-files.sh
```

### 2. 手動確認コマンド

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# nas-projectフォルダに移動
cd ~/nas-project

# 一時的なバックアップファイルを検索
find . -type f \( -name "*.backup" -o -name "*.bak" -o -name "*.old" -o -name "*.tmp" -o -name "*.temp" \) 2>/dev/null | grep -v ".git" | grep -v "node_modules" | grep -v "venv"

# テスト用ファイルを検索
find . -type f -name "*test*" 2>/dev/null | grep -v ".git" | grep -v "node_modules" | grep -v "venv" | grep -v "__pycache__"

# デバッグ用ファイルを検索
find . -type f -name "*debug*" 2>/dev/null | grep -v ".git" | grep -v "node_modules" | grep -v "venv" | grep -v "__pycache__"
```

## 📋 確認対象

### 一時的なバックアップファイル

- `*.backup`
- `*.bak`
- `*.old`
- `*.tmp`
- `*.temp`
- `.env.bak`
- `.env.backup*`

### テスト用ファイル

- `*test*.py`
- `*test*.sh`
- `test_*.py`
- `*_test.py`

### デバッグ用ファイル

- `*debug*.py`
- `*debug*.sh`
- `debug_*.py`
- `*_debug.py`

## 🔧 整理方法

### 一時的なバックアップファイルの削除

```bash
# 一時的なバックアップファイルを削除
cd ~/nas-project
find . -type f \( -name "*.backup" -o -name "*.bak" -o -name "*.old" -o -name "*.tmp" -o -name "*.temp" \) 2>/dev/null | grep -v ".git" | grep -v "node_modules" | grep -v "venv" | xargs rm -f

# .env.bak, .env.backup*を削除（.env.restoreは保持）
find . -type f -name ".env.bak" -o -name ".env.backup*" 2>/dev/null | grep -v ".env.restore" | xargs rm -f
```

### テスト用ファイルの整理

テスト用ファイルは必要に応じて保持するか、`docs/testing/`に移動します。

### デバッグ用ファイルの整理

デバッグ用ファイルは必要に応じて保持するか、`docs/testing/`または`guides/troubleshooting/`に移動します。

## ✅ 期待される結果

整理後、一時的なバックアップファイルは削除され、テスト用・デバッグ用ファイルは適切に整理されます。

---

**更新日**: 2025年11月7日

