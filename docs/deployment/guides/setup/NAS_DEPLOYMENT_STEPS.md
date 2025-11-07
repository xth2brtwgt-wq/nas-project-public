# NASデプロイメント手順

**対象**: nas-project の全プロジェクト  
**作成日**: 2025-10-21

---

## 📋 前提条件

### NAS環境
- ✅ Docker / Docker Compose インストール済み
- ✅ Git インストール済み
- ✅ 必要なポートが開放済み

### 必要なポート
- **amazon-analytics**: 8000
- **document-automation**: 8080
- **insta360-auto-sync**: なし（バックグラウンド処理）
- **meeting-minutes-byc**: 5002

---

## 🚀 デプロイ手順

### Step 1: ローカルの変更をリモートにプッシュ

```bash
# ローカル（Mac）で実行
cd /Users/Yoshi/nas-project

# リモートにプッシュ
git push origin main
```

---

### Step 2: NASにSSH接続

```bash
# ローカル（Mac）から実行
ssh -p 23456 AdminUser@[NASのIPアドレス]

# または（ポート指定あり）
ssh -p 23456 AdminUser@192.168.68.110

# または（ポート23456が設定済みの場合）
ssh AdminUser@nas.local
```

---

### Step 3: プロジェクトをクローンまたはプル

#### 初回（クローン）:
```bash
# NAS上で実行
cd /volume1/docker/  # または適切なディレクトリ

git clone [リポジトリURL] nas-project
cd nas-project
```

#### 2回目以降（プル）:
```bash
# NAS上で実行
cd /volume1/docker/nas-project  # 既存のプロジェクトディレクトリ

# 最新を取得
git pull origin main
```

---

### Step 4: 各プロジェクトの設定

各プロジェクトで `.env` ファイルを作成し、実際の値を設定します。`.env.restore`はバックアップファイルとして保存しておくだけです（実行時には使用しない）。

#### 4-1. amazon-analytics

```bash
cd /volume1/docker/nas-project/amazon-analytics

# .env を作成（または復元）
if [ -f .env.restore ]; then
    cp .env.restore .env
    echo "✅ .env.restoreから復元しました"
else
    cp env.example .env
fi
nano .env

# .env.restoreをバックアップとして作成（推奨）
cp .env .env.restore
```

**設定内容:**
```env
# データベース
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://postgres:your_secure_password_here@db:5432/amazon_analytics

# Gemini API
GEMINI_API_KEY=your_actual_gemini_api_key

# または OpenAI
AI_PROVIDER=gemini
OPENAI_API_KEY=your_openai_key_if_using_openai
```

#### 4-2. document-automation

```bash
cd /volume1/docker/nas-project/document-automation

# .env を作成（または復元）
if [ -f .env.restore ]; then
    cp .env.restore .env
    echo "✅ .env.restoreから復元しました"
else
    cp env.example .env
fi
nano .env

# .env.restoreをバックアップとして作成（推奨）
cp .env .env.restore
```

**設定内容:**
```env
# Google Cloud Vision API
GOOGLE_CLOUD_VISION_API_KEY=your_vision_api_key

# または Gemini
GEMINI_API_KEY=your_gemini_api_key

# データベース
POSTGRES_PASSWORD=docpass
```

#### 4-3. insta360-auto-sync

```bash
cd /volume1/docker/nas-project/insta360-auto-sync

# .env を作成（または復元）
if [ -f .env.restore ]; then
    cp .env.restore .env
    echo "✅ .env.restoreから復元しました"
else
    cp env.example .env
fi
nano .env

# .env.restoreをバックアップとして作成（推奨）
cp .env .env.restore
```

**設定内容:**
```env
# Mac接続設定
MAC_IP=192.168.68.88
MAC_USERNAME=Admin
MAC_PASSWORD=your_mac_password
MAC_SHARE=Insta360

# メール設定
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
TO_EMAIL=notification@example.com

# 同期設定
SYNC_SCHEDULE=0 0 * * *
SOURCE_PATH=/source
DESTINATION_PATH=/volume2/data/insta360
```

#### 4-4. meeting-minutes-byc

```bash
cd /volume1/docker/nas-project/meeting-minutes-byc

# .env を作成（または復元）
if [ -f .env.restore ]; then
    cp .env.restore .env
    echo "✅ .env.restoreから復元しました"
else
    cp env.example .env
fi
nano .env

# .env.restoreをバックアップとして作成（推奨）
cp .env .env.restore
```

**設定内容:**
```env
# Gemini API
GEMINI_API_KEY=your_actual_gemini_api_key

# メール設定（オプション）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com

# Notion設定（オプション）
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
```

---

### Step 5: 各プロジェクトをデプロイ

#### 5-1. amazon-analytics

```bash
cd /volume1/docker/nas-project/amazon-analytics

# データベースボリュームを初回作成
docker-compose up -d

# ログを確認
docker-compose logs -f web

# 動作確認
curl http://localhost:8000/health

# ブラウザでアクセス
# http://[NASのIP]:8000
```

#### 5-2. document-automation

```bash
cd /volume1/docker/nas-project/document-automation

# データフォルダを作成（NAS固有）
sudo mkdir -p /home/AdminUser/nas-project-data/document-automation/{uploads,processed,exports,cache,db}
sudo chown -R AdminUser:admin /home/AdminUser/nas-project-data/document-automation

# 起動
docker-compose up -d

# ログを確認
docker-compose logs -f web

# ブラウザでアクセス
# http://[NASのIP]:8080
```

#### 5-3. insta360-auto-sync

```bash
cd /volume1/docker/nas-project/insta360-auto-sync

# Mac共有フォルダをマウント（事前に設定が必要）
# Control Panel -> File Services -> SMB/AFP/NFS

# データフォルダを作成
sudo mkdir -p /volume2/data/insta360

# 起動
docker-compose up -d

# ログを確認
docker-compose logs -f

# 手動同期テスト
docker-compose exec insta360-auto-sync python scripts/sync.py
```

#### 5-4. meeting-minutes-byc

```bash
cd /volume1/docker/nas-project/meeting-minutes-byc

# データフォルダを作成
sudo mkdir -p /home/AdminUser/meeting-minutes-data/{uploads,transcripts,templates,logs}

# 起動
docker-compose up -d

# ログを確認
docker-compose logs -f

# ブラウザでアクセス
# http://[NASのIP]:5002
```

---

## ✅ 動作確認

### 1. コンテナの状態確認

```bash
# 各プロジェクトで実行
docker-compose ps

# すべてのコンテナを確認
docker ps

# ネットワークを確認
docker network ls
```

### 2. ログ確認

```bash
# リアルタイムログ
docker-compose logs -f

# 最新100行
docker-compose logs --tail=100

# 特定のサービス
docker-compose logs -f web
```

### 3. ヘルスチェック

```bash
# amazon-analytics
curl http://localhost:8000/health

# document-automation
curl http://localhost:8080/

# meeting-minutes-byc
curl http://localhost:5002/health
```

---

## 🔧 トラブルシューティング

### ポートが使用中の場合

```bash
# ポートを確認
sudo netstat -tulpn | grep :8000

# 既存のコンテナを停止
docker-compose down
```

### パーミッションエラー

```bash
# データフォルダの権限を修正
sudo chown -R 1000:1000 /volume2/data/doc-automation
sudo chmod -R 755 /volume2/data/doc-automation
```

### データベース接続エラー

```bash
# データベースボリュームをリセット
docker-compose down -v
docker-compose up -d
```

### ログが見れない場合

```bash
# Docker ログドライバーを確認
docker inspect [container_id] | grep LogPath

# ログファイルを直接確認
sudo tail -f /var/lib/docker/containers/[container_id]/[container_id]-json.log
```

---

## 📊 管理コマンド

### 起動・停止

```bash
# すべて起動
docker-compose up -d

# すべて停止
docker-compose down

# 停止してボリュームも削除
docker-compose down -v

# 再起動
docker-compose restart

# 特定のサービスのみ再起動
docker-compose restart web
```

### 更新

```bash
# コードを更新
git pull origin main

# イメージを再ビルド
docker-compose build

# 再起動
docker-compose up -d

# または一括
git pull && docker-compose up -d --build
```

### クリーンアップ

```bash
# 未使用のコンテナ・イメージ・ボリュームを削除
docker system prune -a

# 未使用のボリュームのみ削除
docker volume prune
```

---

## 🔐 セキュリティ

### ファイアウォール設定

```bash
# 必要なポートのみ開放
sudo ufw allow 8000/tcp  # amazon-analytics
sudo ufw allow 8080/tcp  # document-automation
sudo ufw allow 5002/tcp  # meeting-minutes-byc

# ファイアウォール有効化
sudo ufw enable
```

### .env.restore の保護

```bash
# .env.restore のパーミッションを制限
chmod 600 */.env.restore

# 所有者のみ読み書き可能
ls -la */.env.restore
```

---

## 📱 アクセスURL

デプロイ後、以下のURLでアクセス可能：

- **amazon-analytics**: `http://[NASのIP]:8000`
- **document-automation**: `http://[NASのIP]:8080`
- **meeting-minutes-byc**: `http://[NASのIP]:5002`
- **insta360-auto-sync**: バックグラウンド動作（UI なし）

---

## 🔄 自動起動設定

NAS再起動時に自動起動するよう設定：

```bash
# docker-compose.yml に restart: unless-stopped が設定済み
# 確認：
grep "restart:" */docker-compose.yml

# すべて unless-stopped または always になっているはず
```

---

## 📝 チェックリスト

デプロイ前の確認：

- [ ] ローカルの変更をプッシュ済み
- [ ] NASにSSH接続可能
- [ ] Git リポジトリをクローン/プル済み
- [ ] 各プロジェクトの .env 作成済み（.env.restoreはバックアップとして保存）
- [ ] 必要なAPIキーを取得済み
- [ ] データフォルダを作成済み
- [ ] ポートが開放済み

デプロイ後の確認：

- [ ] すべてのコンテナが起動中
- [ ] ログにエラーがない
- [ ] ブラウザでアクセス可能
- [ ] 各機能が正常動作

---

## 📚 関連ドキュメント

- `docs/deployment/NAS_DEPLOYMENT_GUIDE.md` - 詳細なNASデプロイメントガイド
- `docs/deployment/DEPLOYMENT_TROUBLESHOOTING.md` - トラブルシューティング
- `docs/testing/PROJECT_TEST_RESULTS.md` - テスト結果

---

**作成日**: 2025-10-21  
**更新日**: 2025-10-21

