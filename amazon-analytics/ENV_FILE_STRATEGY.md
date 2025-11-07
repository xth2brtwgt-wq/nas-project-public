# 環境ファイル設計思想

## 📋 ファイル構成

### 1. `.env` （Gitで管理）
- **用途**: 実際に稼働時に使うファイル
- **管理**: Gitリポジトリにコミット
- **内容**: 実際のAPIキー・パスワード

### 2. `.env.restore` （Gitで管理しない）
- **用途**: GitPull時などで.envファイルが初期化された時用のバックアップ
- **管理**: `.gitignore`で除外
- **内容**: バックアップ用の設定値
- **注意**: 実行時には使用されません（`.env`のみを使用）

### 3. `env.example` （Gitで管理）
- **用途**: 設定テンプレート・ドキュメント
- **管理**: Gitリポジトリにコミット
- **内容**: 説明付きのサンプル値

---

## 🎯 設計思想

### なぜ`.env.restore`を使うのか？

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
# .env + .env.restore の場合
git pull  # 最新コードを取得
# → .envが初期化された場合
# → .env.restoreから復元（バックアップ）
# → 設定を復元可能 😊
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
2. `.env.restore`は初期化時のバックアップ用（実行時には使用しない）

---

## 🔄 ワークフロー

### 初回セットアップ
```bash
# 1. リポジトリをクローン
git clone <repository>
cd amazon-analytics

# 2. env.exampleから.envを作成
cp env.example .env

# 3. .envを編集（実際の値を設定）
nano .env
# APIキー、パスワードなどを設定

# 4. .envから.env.restoreを作成（バックアップ）
cp .env .env.restore

# 5. 起動
docker-compose up -d
```

### 通常の運用
```bash
# コードを更新
git pull

# .envが初期化された場合は.env.restoreから復元
if [ ! -f .env ] || [ ! -s .env ]; then
    if [ -f .env.restore ]; then
        echo "⚠️  .envが初期化されています。.env.restoreから復元します..."
        cp .env.restore .env
    else
        echo "⚠️  警告: .env.restoreが見つかりません。env.exampleから作成してください"
        cp env.example .env
    fi
fi

docker-compose restart
```

### チームメンバーへの共有
```bash
# .envはGitで共有される（実際の設定）
git push

# .env.restoreはバックアップ用として各自が作成
# → チームメンバーに「.env.restoreをバックアップとして作成してください」と指示
```

---

## 🔐 セキュリティ

### .gitignoreの設定
```gitignore
# 機密情報を含むファイルを除外
.env.restore
.env.production
.env.*.local
.env.backup*

# テンプレートは含める（除外しない）
# .env
# env.example
```

### 安全性
- ✅ `.env.restore` → バックアップ用設定 → Git管理外（実行時には使用しない）
- ✅ `.env` → 実際のAPIキー・パスワード → Git管理可（実際の稼働設定）
- ✅ `env.example` → 説明付きテンプレート → Git管理可

---

## 📝 ファイルの内容例

### `.env` （Gitで管理）
```env
# データベース設定（実際の値）
POSTGRES_PASSWORD=amazon_analytics_2025
DATABASE_URL=postgresql://postgres:amazon_analytics_2025@db:5432/amazon_analytics

# Gemini API（実際のキー）
GEMINI_API_KEY=AIzaSyDS_gER_ei9mfkNoGG63P2VODorlayD9dM
```

### `.env.restore` （Git管理外）
```env
# データベース設定（バックアップ値）
POSTGRES_PASSWORD=amazon_analytics_2025
DATABASE_URL=postgresql://postgres:amazon_analytics_2025@db:5432/amazon_analytics

# Gemini API（バックアップキー）
GEMINI_API_KEY=AIzaSyDS_gER_ei9mfkNoGG63P2VODorlayD9dM
```

⚠️ **注意**: `.env.restore`は実行時には使用されません。`.env`が初期化された際の復元用バックアップファイルです。

### `env.example` （Gitで管理）
```env
# Amazon Purchase Analytics System - 環境変数設定例
# このファイルをコピーして .env を作成してください
# .env.restoreはバックアップ用として保存しておくファイルです（実行時には使用しない）

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

# .env.restoreはバックアップとして作成
cp .env .env.restore
git add .env  # ← 実際の値なので稼働可能
```

---

### ❌ 間違い2: .env.restoreをGitにコミット
```bash
git add .env.restore  # ← バックアップファイルなので不要！
git commit -m "Add backup config"
```

### ✅ 正解: .env.restoreは.gitignoreで除外
```bash
# .gitignoreに含まれているので自動的に除外される
git status
# → .env.restoreは表示されない
```

---

## 🔄 他プロジェクトとの統一

### nas-projectの全プロジェクト
```
document-automation/   → .env + .env.restore 方式
insta360-auto-sync/    → .env + .env.restore 方式
meeting-minutes-byc/   → .env + .env.restore 方式
amazon-analytics/      → .env + .env.restore 方式 ✅
```

すべて同じ設計思想を採用（`.env`のみを使用、`.env.restore`はバックアップ用）。

---

## 📚 参考

### Docker Composeのenv_file
- https://docs.docker.com/compose/environment-variables/set-environment-variables/
- 複数指定時は最初のファイルが優先される

### ベストプラクティス
- `.env` - 実際の稼働設定（Git管理、実行時に使用）
- `.env.restore` - バックアップ設定（Git管理外、実行時には使用しない）
- `.env.production` - 本番設定（Git管理外）
- `env.example` - テンプレート（Git管理）

---

## ✅ チェックリスト

プロジェクトセットアップ時：
- [ ] `.env`が存在する（実際の稼働設定）
- [ ] `.env.restore`をバックアップとして作成した
- [ ] `.env`に実際の機密情報を設定した
- [ ] `.gitignore`に`.env.restore`が含まれている
- [ ] `docker-compose.yml`で`.env`のみを読み込んでいる（`.env.restore`は使用しない）

Git操作時：
- [ ] `.env`のみコミット（実際の稼働設定）
- [ ] `.env.restore`はコミットしない（バックアップファイル）
- [ ] `git pull`後も`.env.restore`が残っている

---

**この設計により、Gitプル時も設定が保持され、機密情報も安全に管理できます。** 🎉

