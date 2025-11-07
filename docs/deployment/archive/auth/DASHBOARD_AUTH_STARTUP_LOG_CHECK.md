# 🔍 ダッシュボード認証 起動ログ確認

**作成日**: 2025-11-04  
**目的**: 認証データベースの初期化ログが表示されない問題の確認

---

## ❌ 問題

起動ログに「認証データベースを初期化しました」が表示されない：

```bash
sudo docker compose logs nas-dashboard | tail -30
# 認証データベース初期化ログが表示されない
```

---

## 🔍 確認手順

### ステップ1: 起動ログ全体を確認

```bash
cd ~/nas-project/nas-dashboard

# 起動ログ全体を確認
sudo docker compose logs nas-dashboard | grep -i "認証\|auth\|init\|start" | head -20

# エラーログを確認
sudo docker compose logs nas-dashboard | grep -i "error\|exception" | head -20
```

### ステップ2: アプリケーションの起動を確認

```bash
cd ~/nas-project/nas-dashboard

# コンテナ内でアプリケーションを直接確認
sudo docker compose exec nas-dashboard python -c "
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils.auth_db import init_auth_db
import logging

logging.basicConfig(level=logging.INFO)
init_auth_db()
print('✅ 認証データベースを初期化しました')
"
```

### ステップ3: ルートパスへのアクセスログを確認

```bash
cd ~/nas-project/nas-dashboard

# ルートパスへのアクセスログを確認
sudo docker compose logs nas-dashboard | grep -i "GET / " | tail -10

# すべてのアクセスログを確認
sudo docker compose logs nas-dashboard | grep -i "GET /" | tail -20
```

### ステップ4: リアルタイムでログを確認

```bash
cd ~/nas-project/nas-dashboard

# リアルタイムでログを確認
sudo docker compose logs -f nas-dashboard
```

別のターミナルでブラウザからアクセス：
- 外部アクセス: `https://yoshi-nas-sys.duckdns.org:8443/`
- 内部アクセス: `http://192.168.68.110:9001/`

---

## 🔧 修正方法

### 方法1: アプリケーションを再ビルドして再起動

```bash
cd ~/nas-project/nas-dashboard

# イメージを再ビルド
sudo docker compose build --no-cache

# コンテナを停止して再起動
sudo docker compose down
sudo docker compose up -d

# 起動ログを確認
sudo docker compose logs nas-dashboard | tail -30
```

### 方法2: コンテナ内で直接確認

```bash
cd ~/nas-project/nas-dashboard

# コンテナ内に入る
sudo docker compose exec nas-dashboard bash

# コンテナ内で実行
cd /nas-project/nas-dashboard
python -c "
from utils.auth_db import init_auth_db
import logging
logging.basicConfig(level=logging.INFO)
init_auth_db()
print('✅ 認証データベースを初期化しました')
"
exit
```

---

## 📝 確認項目

- [ ] 起動ログに「認証データベースを初期化しました」が表示される
- [ ] エラーログが表示されない
- [ ] ルートパス`/`へのアクセスログが表示される
- [ ] ブラウザでアクセスした後、ログに認証関連のメッセージが表示される

---

## 🎯 期待されるログ

起動時：

```
認証データベースを初期化しました
[2025-11-04 15:10:36 +0900] [1] [INFO] Starting gunicorn 21.2.0
```

アクセス時：

```
192.168.160.1 - - [04/Nov/2025:15:10:42 +0900] "GET / HTTP/1.1" 302 ...
[AUTH] セッションIDがありません
[AUTH] 認証が必要です: /
```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

