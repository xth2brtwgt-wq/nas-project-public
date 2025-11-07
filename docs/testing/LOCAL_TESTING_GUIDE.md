# ローカル環境での動作確認ガイド

## 📋 概要

このガイドでは、ローカル環境（Mac）で各システムの画面表示と遷移を確認する方法を説明します。

## 🎯 確認したい項目

- ダッシュボードからの画面遷移
- 各システムのヘッダー表示（統一スタイル）
- 戻るボタンの動作
- 同じタブでの遷移

---

## 🚀 方法1: nas-dashboardを直接起動（推奨）

### 前提条件

- Python 3.8以上がインストールされていること
- 必要なPythonパッケージがインストールされていること

### 手順

#### 1. 依存関係のインストール

```bash
cd /Users/Yoshi/nas-project/nas-dashboard

# 仮想環境を作成（推奨）
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# または
# venv\Scripts\activate  # Windows

# 依存関係をインストール
pip install -r requirements.txt
```

#### 2. 環境変数の設定

```bash
# .env ファイルを作成（ローカル用）
cp env.example .env.local

# 必要に応じて編集
# NAS_MODE=false  # ローカル環境ではfalseに設定
# SECRET_KEY=your-secret-key-here
```

#### 3. 認証データベースの初期化

```bash
# ローカル用のデータディレクトリを作成
mkdir -p ~/nas-project-data-local/nas-dashboard

# 認証データベースを初期化（初回のみ）
python3 -c "
from utils.auth_db import init_auth_db
init_auth_db()
print('認証データベースを初期化しました')
"
```

#### 4. アプリケーションの起動

```bash
# 環境変数を設定して起動
export NAS_MODE=false
export FLASK_ENV=development
export SECRET_KEY=local-secret-key-2025
export LOG_DIR=./logs

# アプリケーションを起動
python3 app.py
```

#### 5. アクセス

ブラウザで以下にアクセス：
- **ダッシュボード**: http://localhost:9000
- **ログイン**: http://localhost:9000/login

**デフォルトユーザー**:
- ユーザー名: `admin`
- パスワード: `admin123`（初回起動時）

---

## 🚀 方法2: Docker Composeを使用（簡易版）

### 前提条件

- Docker Desktopがインストールされていること

### 手順

#### 1. ローカル用のdocker-compose.ymlを作成

```bash
cd /Users/Yoshi/nas-project/nas-dashboard

# ローカル用のdocker-compose.local.ymlを作成
cat > docker-compose.local.yml << 'EOF'
services:
  nas-dashboard:
    build: .
    image: nas-dashboard:latest
    container_name: nas-dashboard-local
    ports:
      - "9001:9000"
    volumes:
      # ローカル用のデータディレクトリ
      - ~/nas-project-data-local/nas-dashboard:/app/data
      - ./logs:/app/logs
      - ./templates:/app/templates
      - ./static:/app/static
    environment:
      - TZ=Asia/Tokyo
      - FLASK_ENV=development
      - NAS_MODE=false
      - SECRET_KEY=local-secret-key-2025
    env_file:
      - .env.local
    restart: unless-stopped
EOF
```

#### 2. 起動

```bash
# コンテナを起動
docker compose -f docker-compose.local.yml up --build

# バックグラウンドで起動する場合
docker compose -f docker-compose.local.yml up -d --build
```

#### 3. アクセス

ブラウザで以下にアクセス：
- **ダッシュボード**: http://localhost:9001

---

## 🔍 各システムの画面確認方法

### 1. ダッシュボードからの遷移確認

1. **ダッシュボードにアクセス**
   - http://localhost:9000 または http://localhost:9001

2. **各システムのボタンをクリック**
   - 同じタブで開くことを確認
   - `target="_blank"`が削除されていることを確認

3. **戻るボタンの確認**
   - 各システム画面で左矢印アイコンをクリック
   - ダッシュボードに戻ることを確認

### 2. ヘッダーの統一スタイル確認

各システムのヘッダーで以下を確認：

- ✅ Bootstrap navbar (`navbar navbar-dark bg-primary`)
- ✅ 左側に戻る矢印アイコン（`fas fa-arrow-left`）
- ✅ タイトル（クリック可能でダッシュボードに戻る）
- ✅ 右側にバージョン情報

**確認対象システム**:
- 📄 ドキュメント自動処理システム
- 📊 Amazon購入分析
- 🎬 YouTube to Notion
- 🎤 Meeting Minutes BYC
- 🧠 Notion WebClipper自動要約
- 📷 Insta360自動同期

---

## ⚠️ 注意事項

### ローカル環境での制限事項

1. **外部サービスへのアクセス**
   - 一部のサービス（document-automation、amazon-analyticsなど）は、データベースや外部サービスに依存しているため、ローカル環境では完全に動作しない可能性があります

2. **認証データベース**
   - ローカル環境では、認証データベースが別途必要です
   - 初回起動時に初期化が必要です

3. **データディレクトリ**
   - NAS環境のデータディレクトリ（`/home/AdminUser/nas-project-data/`）はローカルには存在しません
   - ローカル用のデータディレクトリを作成する必要があります

4. **ポート番号**
   - ローカル環境では、各サービスが異なるポート番号で起動されます
   - ダッシュボードのサービス設定で、ローカル用のURLに変更する必要があります

---

## 🔧 トラブルシューティング

### ポートが既に使用されている

```bash
# ポート9000が使用されているか確認
lsof -i :9000

# 使用中のプロセスを終了
kill -9 <PID>
```

### 認証データベースエラー

```bash
# 認証データベースを再初期化
rm ~/nas-project-data-local/nas-dashboard/auth.db
python3 -c "
from utils.auth_db import init_auth_db
init_auth_db()
print('認証データベースを再初期化しました')
"
```

### 依存関係のエラー

```bash
# 依存関係を再インストール
pip install --upgrade -r requirements.txt
```

### テンプレートが見つからない

```bash
# テンプレートディレクトリの存在を確認
ls -la templates/

# 必要に応じて再作成
mkdir -p templates
```

---

## 📝 確認チェックリスト

### ダッシュボード

- [ ] ダッシュボードが表示される
- [ ] 各システムのボタンが表示される
- [ ] ボタンをクリックすると同じタブで開く（新規タブで開かない）

### 各システム画面

- [ ] ヘッダーが統一スタイルで表示される
- [ ] 戻るボタン（左矢印アイコン）が表示される
- [ ] 戻るボタンをクリックするとダッシュボードに戻る
- [ ] バージョン情報が右側に表示される
- [ ] タイトルがクリック可能でダッシュボードに戻る

### 画面遷移

- [ ] ダッシュボード → 各システム → ダッシュボードの遷移が正常に動作する
- [ ] ブラウザの戻るボタンでも正常に動作する

---

## 🎯 次のステップ

1. **画面表示の確認**
   - 各システムのヘッダーが統一されているか確認
   - 戻るボタンが正しく表示されているか確認

2. **遷移の確認**
   - ダッシュボードから各システムへの遷移が正常か確認
   - 各システムからダッシュボードへの遷移が正常か確認

3. **問題の報告**
   - 問題があれば、スクリーンショットとエラーメッセージを記録
   - ブラウザの開発者ツール（F12）でコンソールエラーを確認

---

**更新日**: 2025-11-06  
**作成者**: AI Assistant

