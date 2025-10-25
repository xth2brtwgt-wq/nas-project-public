# 環境ファイル設計思想

## 📋 ファイル構成

### 1. `.env` （Gitで管理）
- **用途**: 実際に稼働時に使うファイル
- **管理**: Gitリポジトリにコミット
- **内容**: 実際のAPIキー・パスワード

### 2. `.env.local` （Gitで管理しない）
- **用途**: GitPull時などで.envファイルが初期化された時用のバックアップ
- **管理**: `.gitignore`で除外
- **内容**: バックアップ用の設定値

### 3. `env.example` （Gitで管理）
- **用途**: 設定テンプレート・ドキュメント
- **管理**: Gitリポジトリにコミット
- **内容**: 説明付きのサンプル値

---

## 🎯 設計思想

### なぜ`.env.local`を使うのか？

#### 問題
```bash
# .envのみの場合の問題点
git pull  # 最新コードを取得
# → .envが上書きされる
# → APIキー・パスワードが消える
# → 再設定が必要 😱
```

#### 解決策
```bash
# .env + .env.local の場合
git pull  # 最新コードを取得
# → .envは更新される（テンプレート）
# → .env.localは残る（実際の設定）
# → 設定は保持される 😊
```

---

## 📊 ファイルの優先順位

### Docker Composeの読み込み順
```yaml
env_file:
  - .env        # 実際の値（稼働時に使用）
```

### 動作
1. `.env`が存在 → その値を使用（実際の稼働設定）
2. `.env.local`は初期化時のバックアップ用

---

## 🔄 ワークフロー

### 初回セットアップ
```bash
# 1. リポジトリをクローン
git clone <repository>
cd amazon-analytics

# 2. .envを編集（実際の値を設定）
nano .env
# APIキー、パスワードなどを設定

# 3. .env.localをバックアップとして作成
cp .env .env.local

# 4. 起動
docker-compose up -d
```

### 通常の運用
```bash
# コードを更新
git pull

# .envが初期化された場合は.env.localから復元
cp .env.local .env

docker-compose restart
```

### チームメンバーへの共有
```bash
# .envはGitで共有される（実際の設定）
git push

# .env.localはバックアップ用として各自が作成
# → チームメンバーに「.env.localをバックアップとして作成してください」と指示
```

---

## 🔐 セキュリティ

### .gitignoreの設定
```gitignore
# 機密情報を含むファイルを除外
.env.local
.env.production
.env.*.local
.env.backup*

# テンプレートは含める（除外しない）
# .env
# env.example
```

### 安全性
- ✅ `.env.local` → バックアップ用設定 → Git管理外
- ✅ `.env` → 実際のAPIキー・パスワード → Git管理可
- ✅ `env.example` → 説明付きテンプレート → Git管理可

---

## 📝 ファイルの内容例

### `.env` （Gitで管理）
```env
# データベース設定（実際の値）
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://postgres:your_secure_password_here@db:5432/amazon_analytics

# Gemini API（実際のキー）
GEMINI_API_KEY=your_gemini_api_key_here
```

### `.env.local` （Git管理外）
```env
# データベース設定（バックアップ値）
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://postgres:your_secure_password_here@db:5432/amazon_analytics

# Gemini API（バックアップキー）
GEMINI_API_KEY=your_gemini_api_key_here
```

### `env.example` （Gitで管理）
```env
# Amazon Purchase Analytics System - 環境変数設定例
# このファイルをコピーして .env.local を作成してください

# データベース設定
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://postgres:your_secure_password_here@db:5432/amazon_analytics

# Redis
REDIS_URL=redis://redis:6379/0

# AI Provider (gemini or openai)
AI_PROVIDER=gemini

# Gemini API (Google AI)
# 取得方法: https://aistudio.google.com/apikey
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

---

## 🚨 よくある間違い

### ❌ 間違い1: .envにサンプル値を書く
```bash
# .envにサンプル値を書いてGitにコミット
git add .env
git commit -m "Add sample values"  # ← 稼働時に使えない！
```

### ✅ 正解: .envに実際の値を書く
```bash
# .envに実際のAPIキーを書く
nano .env

# .env.localはバックアップとして作成
cp .env .env.local
git add .env  # ← 実際の値なので稼働可能
```

---

### ❌ 間違い2: .env.localをGitにコミット
```bash
git add .env.local  # ← バックアップファイルなので不要！
git commit -m "Add backup config"
```

### ✅ 正解: .env.localは.gitignoreで除外
```bash
# .gitignoreに含まれているので自動的に除外される
git status
# → .env.localは表示されない
```

---

## 🔄 他プロジェクトとの統一

### nas-projectの全プロジェクト
```
document-automation/   → .env + .env.local 方式
insta360-auto-sync/    → .env + .env.local 方式
meeting-minutes-byc/   → .env + .env.local 方式
amazon-analytics/      → .env + .env.local 方式 ✅
```

すべて同じ設計思想を採用。

---

## 📚 参考

### Docker Composeのenv_file
- https://docs.docker.com/compose/environment-variables/set-environment-variables/
- 複数指定時は最初のファイルが優先される

### ベストプラクティス
- `.env` - 実際の稼働設定（Git管理）
- `.env.local` - バックアップ設定（Git管理外）
- `.env.production` - 本番設定（Git管理外）
- `env.example` - テンプレート（Git管理）

---

## ✅ チェックリスト

プロジェクトセットアップ時：
- [ ] `.env`が存在する（実際の稼働設定）
- [ ] `.env.local`をバックアップとして作成した
- [ ] `.env`に実際の機密情報を設定した
- [ ] `.gitignore`に`.env.local`が含まれている
- [ ] `docker-compose.yml`で`.env`のみを読み込んでいる

Git操作時：
- [ ] `.env`のみコミット（実際の稼働設定）
- [ ] `.env.local`はコミットしない（バックアップファイル）
- [ ] `git pull`後も`.env.local`が残っている

---

**この設計により、Gitプル時も設定が保持され、機密情報も安全に管理できます。** 🎉

