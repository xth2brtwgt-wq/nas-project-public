# 🔄 ドキュメント自動処理システム・モニタリング画面 認証完全再起動

**作成日**: 2025-11-04  
**目的**: `document-automation`と`nas-dashboard-monitoring`の認証デバッグログを確認するための完全再起動

---

## ❌ 問題

`restart`コマンドでは、コンテナ内のコードは更新されません。完全再起動（`down` → `up`）が必要です。

---

## 🔄 完全再起動手順

### ステップ1: document-automationを完全再起動

```bash
cd ~/nas-project/document-automation
git pull origin feature/monitoring-fail2ban-integration
sudo docker compose down
sudo docker compose up -d
```

### ステップ2: document-automationの起動ログで[AUTH]ログを確認

```bash
cd ~/nas-project/document-automation
sudo docker compose logs web | grep "\[AUTH\]" | tail -20
```

**期待されるログ**:
```
2025-11-04 ... - app.api.main - INFO - [AUTH] 認証モジュールの読み込みを開始します
2025-11-04 ... - app.api.main - INFO - [AUTH] nas_dashboard_path: /nas-project/nas-dashboard
2025-11-04 ... - app.api.main - INFO - [AUTH] nas_dashboard_path.exists(): True
2025-11-04 ... - app.api.main - INFO - [AUTH] sys.pathに追加: /nas-project/nas-dashboard
2025-11-04 ... - app.api.main - INFO - [AUTH] auth_common_path: /nas-project/nas-dashboard/utils/auth_common.py
2025-11-04 ... - app.api.main - INFO - [AUTH] auth_common_path.exists(): True
2025-11-04 ... - app.api.main - INFO - [AUTH] 認証モジュールファイルを読み込み中...
2025-11-04 ... - app.api.main - INFO - [AUTH] 認証モジュールを読み込みました
2025-11-04 ... - app.api.main - INFO - [AUTH] AUTH_ENABLED: True
```

### ステップ3: nas-dashboard-monitoringを完全再起動

```bash
cd ~/nas-project/nas-dashboard-monitoring
git pull origin feature/monitoring-fail2ban-integration
sudo docker compose down
sudo docker compose up -d
```

### ステップ4: nas-dashboard-monitoringの起動ログで[AUTH]ログを確認

```bash
cd ~/nas-project/nas-dashboard-monitoring
sudo docker compose logs backend | grep "\[AUTH\]" | tail -20
```

**期待されるログ**:
```
2025-11-04 ... - app.main - INFO - [AUTH] 認証モジュールの読み込みを開始します
2025-11-04 ... - app.main - INFO - [AUTH] nas_dashboard_path: /nas-project/nas-dashboard
2025-11-04 ... - app.main - INFO - [AUTH] nas_dashboard_path.exists(): True
2025-11-04 ... - app.main - INFO - [AUTH] sys.pathに追加: /nas-project/nas-dashboard
2025-11-04 ... - app.main - INFO - [AUTH] auth_common_path: /nas-project/nas-dashboard/utils/auth_common.py
2025-11-04 ... - app.main - INFO - [AUTH] auth_common_path.exists(): True
2025-11-04 ... - app.main - INFO - [AUTH] 認証モジュールファイルを読み込み中...
2025-11-04 ... - app.main - INFO - [AUTH] 認証モジュールを読み込みました
2025-11-04 ... - app.main - INFO - [AUTH] AUTH_ENABLED: True
```

### ステップ5: 認証を確認

```bash
# document-automation
curl -v http://localhost:8080/

# nas-dashboard-monitoring
curl -v http://localhost:8002/
```

**期待される動作**:
- HTTP 307（リダイレクト）
- `Location: https://yoshi-nas-sys.duckdns.org:8443/login` ヘッダーが含まれる

---

## 🔧 トラブルシューティング

### ログが表示されない場合

1. **起動ログ全体を確認**:
   ```bash
   cd ~/nas-project/<サービス名>
   sudo docker compose logs <サービス名> | tail -100
   ```

2. **コンテナ内でコードを確認**:
   ```bash
   sudo docker exec <コンテナ名> cat /app/app/api/main.py | grep -A 5 "\[AUTH\]"
   ```

3. **完全再ビルド**:
   ```bash
   cd ~/nas-project/<サービス名>
   sudo docker compose down
   sudo docker compose build --no-cache <サービス名>
   sudo docker compose up -d
   ```

### AUTH_ENABLEDがFalseの場合

ログに表示されるエラーメッセージを確認：
- "認証モジュールのパスが見つかりません" → マウント設定の問題
- "認証モジュールファイルが見つかりません" → ファイルパスの問題
- "認証モジュールをインポートできませんでした" → インポートエラー

---

## 📝 確認チェックリスト

- [ ] 完全再起動（`down` → `up`）を実行
- [ ] 起動ログに`[AUTH]`ログが表示される
- [ ] `AUTH_ENABLED: True`が表示される
- [ ] `curl`でHTTP 307（リダイレクト）が返される

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

