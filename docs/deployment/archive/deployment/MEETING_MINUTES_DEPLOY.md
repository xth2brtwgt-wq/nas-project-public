# meeting-minutes-byc デプロイ手順

**最新版（Gemini 2.5-flash）のデプロイ**

---

## 🚀 NASで実行するコマンド

### Step 1: ディレクトリに移動

```bash
cd ~/nas-project/meeting-minutes-byc
pwd  # 確認
```

---

### Step 2: 環境ファイルを作成

```bash
# .env をコピーして .env.restore を作成
cp .env .env.restore

# 編集
nano .env.restore
```

---

### Step 3: .env.restore の設定内容

**必須項目:**

```env
# Gemini API (必須)
GEMINI_API_KEY=your_actual_gemini_api_key_here

# ポート設定（デフォルトのまま）
PORT=5000

# アップロード設定
MAX_CONTENT_LENGTH=500
ALLOWED_EXTENSIONS=mp3,wav,m4a,mp4,mpeg,mpga,webm

# Gemini設定
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_TEMPERATURE=0.2
GEMINI_MAX_TOKENS=8192
```

**オプション項目（メール送信する場合）:**

```env
# メール設定（オプション）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
```

**オプション項目（Notion連携する場合）:**

```env
# Notion設定（オプション）
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
```

---

### Step 4: 保存して終了

nano エディタでの操作:
1. **Ctrl + X** (終了)
2. **Y** (保存確認)
3. **Enter** (ファイル名確認)

---

### Step 5: データフォルダを作成

```bash
# データフォルダを作成
sudo mkdir -p /home/AdminUser/meeting-minutes-data/{uploads,transcripts,templates,logs}

# 権限を設定
sudo chown -R AdminUser:users /home/AdminUser/meeting-minutes-data
sudo chmod -R 755 /home/AdminUser/meeting-minutes-data

# 確認
ls -la /home/AdminUser/meeting-minutes-data/
```

---

### Step 6: Docker起動

```bash
# meeting-minutes-byc ディレクトリにいることを確認
pwd
# 出力: /var/services/homes/AdminUser/nas-project/meeting-minutes-byc

# Docker起動
docker-compose up -d

# 起動確認
docker-compose ps
```

---

### Step 7: ログ確認

```bash
# リアルタイムログを表示
docker-compose logs -f

# Ctrl+C で終了できます
```

**期待されるログ:**
```
meeting-minutes-byc | * Running on http://0.0.0.0:5000
meeting-minutes-byc | * Environment: production
```

---

### Step 8: 動作確認

#### A. コマンドラインから

```bash
# ヘルスチェック
curl http://localhost:5002/health

# 期待される出力:
# {"status":"healthy"}
```

#### B. ブラウザから

ブラウザで以下のURLにアクセス:
```
http://[NASのIPアドレス]:5002
```

または
```
http://nas.local:5002
```

**議事録生成画面が表示されればOK！** ✅

---

## 🎯 使い方

1. ブラウザで `http://[NASのIP]:5002` にアクセス
2. 音声ファイルをアップロード（mp3, wav, m4a など）
3. 「議事録を生成」ボタンをクリック
4. Gemini 2.5-flash が自動で文字起こし＆議事録生成
5. Markdown形式でダウンロード可能

---

## 🔧 トラブルシューティング

### コンテナが起動しない

```bash
# ログを確認
docker-compose logs

# 再起動
docker-compose restart

# 完全リセット
docker-compose down
docker-compose up -d
```

### ポート5002が使用中

```bash
# ポートを確認
sudo netstat -tulpn | grep :5002

# 他のコンテナを確認
docker ps | grep 5002
```

### APIキーエラー

```bash
# .env.restore を再確認
cat .env.restore | grep GEMINI_API_KEY

# 再編集
nano .env.restore

# 再起動
docker-compose restart
```

---

## 🛑 停止方法

```bash
cd ~/nas-project/meeting-minutes-byc

# 停止
docker-compose down

# 停止してデータも削除
docker-compose down -v
```

---

## 🔄 更新方法

```bash
cd ~/nas-project

# 最新版を取得
git pull origin main

cd meeting-minutes-byc

# 再ビルド＆再起動
docker-compose up -d --build
```

---

**デプロイ完了！** 🎉

