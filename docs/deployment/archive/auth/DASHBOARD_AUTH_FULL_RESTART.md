# 🔄 ダッシュボード認証 完全再起動手順

**作成日**: 2025-11-04  
**目的**: 認証機能が正しく動作するように、アプリケーションを完全に再起動

---

## 📋 完全再起動手順

### ステップ1: 最新コードのプル

```bash
cd ~/nas-project/nas-dashboard
git pull origin feature/monitoring-fail2ban-integration
```

### ステップ2: コンテナの完全停止と再起動

```bash
cd ~/nas-project/nas-dashboard

# コンテナを停止
sudo docker compose down

# コンテナを再起動
sudo docker compose up -d
```

### ステップ3: 起動ログの確認

```bash
cd ~/nas-project/nas-dashboard

# 起動ログを確認
sudo docker compose logs nas-dashboard | tail -30
```

以下のようなログが表示されれば正常です：

```
認証データベースを初期化しました
[2025-11-04 15:08:52 +0900] [1] [INFO] Starting gunicorn 21.2.0
[2025-11-04 15:08:52 +0900] [1] [INFO] Listening at: http://0.0.0.0:9000 (1)
[2025-11-04 15:08:52 +0900] [1] [INFO] Using worker: sync
[2025-11-04 15:08:52 +0900] [2] [INFO] Booting worker with pid: 2
[2025-11-04 15:08:52 +0900] [3] [INFO] Booting worker with pid: 3
```

### ステップ4: ブラウザでアクセスしてログを確認

1. **シークレットモード（プライベートモード）でアクセス**：
   - 外部アクセス: `https://yoshi-nas-sys.duckdns.org:8443/`
   - 内部アクセス: `http://192.168.68.110:9001/`

2. **リアルタイムでログを確認**（別ターミナルで実行）：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose logs -f nas-dashboard
```

ブラウザからアクセスした後、以下のようなログが表示されるはずです：

```
[AUTH] セッションIDがありません
[AUTH] 認証が必要です: /
```

### ステップ5: ログインページの確認

- シークレットモードでアクセスした場合、ログインページが表示されるはずです
- ログインページが表示されない場合は、ブラウザのキャッシュをクリアしてください

---

## 🔍 トラブルシューティング

### エラー: 認証データベース初期化ログが表示されない

**原因**: アプリケーションが古いコードで実行されている可能性

**解決方法**:

1. コンテナを完全に停止：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose down
```

2. イメージを再ビルド：

```bash
sudo docker compose build --no-cache
sudo docker compose up -d
```

### エラー: ログインページが表示されない

**原因**: ブラウザのキャッシュやCookieが残っている可能性

**解決方法**:

1. シークレットモード（プライベートモード）でアクセス
2. または、ブラウザのキャッシュとCookieをクリア

### エラー: ログに認証関連のメッセージが表示されない

**原因**: ログレベルが低い可能性

**解決方法**:

1. `.env`ファイルに以下を追加：

```bash
LOG_LEVEL=DEBUG
```

2. アプリケーションを再起動：

```bash
sudo docker compose restart nas-dashboard
```

---

## 📝 確認項目

- [ ] 最新コードがプルされている
- [ ] コンテナが完全に再起動されている
- [ ] 起動ログに「認証データベースを初期化しました」が表示される
- [ ] ブラウザでアクセスした後、ログに認証関連のメッセージが表示される
- [ ] シークレットモードでアクセスした場合、ログインページが表示される

---

## 🎯 期待される動作

1. シークレットモードでアクセス
2. ログに `[AUTH] セッションIDがありません` と `[AUTH] 認証が必要です: /` が表示される
3. ログインページが表示される
4. 初期ユーザー（`admin`）でログイン
5. ダッシュボードにリダイレクトされる

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

