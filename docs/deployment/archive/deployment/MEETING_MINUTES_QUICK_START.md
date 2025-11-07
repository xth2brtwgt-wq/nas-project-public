# meeting-minutes-byc クイックスタート

**NASでの実行コマンド（コピペ用）**

---

## 🚀 コマンド一覧

以下をNASのターミナルで順番に実行してください：

```bash
# ========================================
# Step 1: ディレクトリに移動
# ========================================
cd ~/nas-project/meeting-minutes-byc
pwd


# ========================================
# Step 2: 環境ファイルを作成
# ========================================
# .env.restoreが既にあるか確認
ls -la .env*

# なければ作成
cp .env .env.restore


# ========================================
# Step 3: Gemini APIキーを設定
# ========================================
nano .env.restore

# ↓ 以下の行を探して編集
# GEMINI_API_KEY=your_gemini_api_key_here
# → 実際のAPIキーに置き換える
#
# 保存: Ctrl+X → Y → Enter


# ========================================
# Step 4: データフォルダを作成
# ========================================
sudo mkdir -p /home/AdminUser/meeting-minutes-data/{uploads,transcripts,templates,logs}
sudo chown -R AdminUser:users /home/AdminUser/meeting-minutes-data
ls -la /home/AdminUser/ | grep meeting


# ========================================
# Step 5: nas-networkが存在するか確認
# ========================================
docker network ls | grep nas-network

# なければ作成
docker network create nas-network


# ========================================
# Step 6: Docker起動
# ========================================
docker-compose up -d


# ========================================
# Step 7: 起動確認
# ========================================
docker-compose ps
docker-compose logs --tail=50


# ========================================
# Step 8: 動作確認
# ========================================
curl http://localhost:5002/health

# 期待される出力: {"status":"healthy"}
```

---

## 🌐 ブラウザでアクセス

```
http://[NASのIPアドレス]:5002
```

または

```
http://nas.local:5002
```

---

## ✅ 成功の確認

- ✅ docker-compose ps で State が "Up" になっている
- ✅ curl コマンドで {"status":"healthy"} が返ってくる
- ✅ ブラウザで議事録生成画面が表示される

---

## 🔧 トラブル時

```bash
# ログを確認
docker-compose logs -f

# 再起動
docker-compose restart

# 完全リセット
docker-compose down
docker-compose up -d
```

---

## 🛑 停止

```bash
cd ~/nas-project/meeting-minutes-byc
docker-compose down
```

