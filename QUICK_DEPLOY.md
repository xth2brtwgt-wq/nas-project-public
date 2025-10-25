# 🚀 クイックデプロイガイド

**5分でNASにデプロイ！**

---

## Step 1: プッシュ（ローカル Mac）

```bash
cd /Users/Yoshi/nas-project
git push origin main
```

---

## Step 2: NASに接続

```bash
ssh YOUR_USERNAME@[NASのIP]
```

---

## Step 3: プロジェクトを取得

```bash
# 初回
cd /volume1/docker
git clone [リポジトリURL] nas-project

# 2回目以降
cd /volume1/docker/nas-project
git pull origin main
```

---

## Step 4: 設定ファイルを作成

各プロジェクトで `.env.local` を作成：

```bash
# amazon-analytics
cd amazon-analytics
cp .env .env.local
nano .env.local  # GEMINI_API_KEY, POSTGRES_PASSWORD を設定

# document-automation
cd ../document-automation
cp .env .env.local
nano .env.local  # API keys を設定

# insta360-auto-sync
cd ../insta360-auto-sync
cp .env .env.local
nano .env.local  # MAC_PASSWORD, EMAIL_PASSWORD を設定

# meeting-minutes-byc
cd ../meeting-minutes-byc
cp .env .env.local
nano .env.local  # GEMINI_API_KEY を設定
```

---

## Step 5: データフォルダ作成

```bash
# document-automation
sudo mkdir -p /volume2/data/doc-automation/{uploads,processed,exports,cache,db}
sudo chown -R 1000:1000 /volume2/data/doc-automation

# insta360-auto-sync
sudo mkdir -p /volume2/data/insta360

# meeting-minutes-byc
sudo mkdir -p /home/YOUR_USERNAME/meeting-minutes-data/{uploads,transcripts,templates,logs}
```

---

## Step 6: 起動！

```bash
cd /volume1/docker/nas-project

# amazon-analytics
cd amazon-analytics && docker compose up -d && cd ..

# document-automation
cd document-automation && docker compose up -d && cd ..

# insta360-auto-sync
cd insta360-auto-sync && docker compose up -d && cd ..

# meeting-minutes-byc
cd meeting-minutes-byc && docker compose up -d && cd ..
```

---

## ✅ 確認

```bash
# すべてのコンテナを確認
docker ps

# ブラウザでアクセス
# http://[NASのIP]:8000  - amazon-analytics
# http://[NASのIP]:8080  - document-automation
# http://[NASのIP]:5002  - meeting-minutes-byc
```

---

## 🔧 トラブル時

```bash
# ログ確認
docker compose logs -f

# 再起動
docker compose restart

# 完全リセット
docker compose down -v && docker compose up -d
```

---

**詳細**: `docs/deployment/NAS_DEPLOYMENT_STEPS.md` を参照

