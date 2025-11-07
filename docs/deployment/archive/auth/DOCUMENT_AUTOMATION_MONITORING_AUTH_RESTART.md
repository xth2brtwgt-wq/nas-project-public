# 🔄 ドキュメント自動処理システム・モニタリング画面 認証再起動手順

**作成日**: 2025-11-04  
**目的**: `document-automation`と`nas-dashboard-monitoring`の認証を有効化するための完全再起動手順

---

## ❌ 問題

両方のサービスがHTTP 200を返しており、認証リダイレクトが機能していません。
認証モジュールが読み込まれていない、または`AUTH_ENABLED`が`False`になっている可能性があります。

---

## 🔍 調査手順

### ステップ1: 起動ログで認証モジュールの読み込みを確認

```bash
# document-automation
cd ~/nas-project/document-automation
sudo docker compose logs web | grep -i "認証\|auth\|AUTH\|モジュール" | tail -20

# nas-dashboard-monitoring
cd ~/nas-project/nas-dashboard-monitoring
sudo docker compose logs backend | grep -i "認証\|auth\|AUTH\|モジュール" | tail -20
```

**期待されるログ**:
```
認証モジュールを読み込みました
```

**問題の可能性**:
- ログに何も表示されない → 認証モジュールが読み込まれていない
- "認証モジュールのパスが見つかりません" → マウント設定の問題
- "認証モジュールファイルが見つかりません" → ファイルパスの問題

### ステップ2: コンテナ内でパスを確認

```bash
# document-automation
sudo docker exec doc-automation-web ls -la /nas-project/nas-dashboard/utils/auth_common.py

# nas-dashboard-monitoring
sudo docker exec nas-dashboard-monitoring-backend-1 ls -la /nas-project/nas-dashboard/utils/auth_common.py
```

**期待される結果**:
```
-rw-r--r-- 1 root root 12345 ... /nas-project/nas-dashboard/utils/auth_common.py
```

---

## ✅ 修正手順

### ステップ1: 完全再起動（推奨）

```bash
# document-automation
cd ~/nas-project/document-automation
git pull origin feature/monitoring-fail2ban-integration
sudo docker compose down
sudo docker compose up -d
sudo docker compose logs web -f | grep -i "認証\|auth" &
# 数秒待ってからCtrl+Cで停止

# nas-dashboard-monitoring
cd ~/nas-project/nas-dashboard-monitoring
git pull origin feature/monitoring-fail2ban-integration
sudo docker compose down
sudo docker compose up -d
sudo docker compose logs backend -f | grep -i "認証\|auth" &
# 数秒待ってからCtrl+Cで停止
```

### ステップ2: 認証モジュールの読み込みを確認

```bash
# document-automation
cd ~/nas-project/document-automation
sudo docker compose logs web | grep -i "認証\|auth" | tail -10

# nas-dashboard-monitoring
cd ~/nas-project/nas-dashboard-monitoring
sudo docker compose logs backend | grep -i "認証\|auth" | tail -10
```

**期待されるログ**:
```
認証モジュールを読み込みました
```

### ステップ3: 認証を確認

```bash
# document-automation
curl -v http://localhost:8080/

# nas-dashboard-monitoring
curl -v http://localhost:8002/
```

**期待される動作**:
- HTTP 307（リダイレクト）
- `Location: https://yoshi-nas-sys.duckdns.org:8443/login` ヘッダーが含まれる

### ステップ4: 完全再ビルド（必要に応じて）

再起動でも認証が機能しない場合：

```bash
# document-automation
cd ~/nas-project/document-automation
sudo docker compose down
sudo docker compose build --no-cache web
sudo docker compose up -d
sudo docker compose logs web -f | grep -i "認証\|auth" &
# 数秒待ってからCtrl+Cで停止

# nas-dashboard-monitoring
cd ~/nas-project/nas-dashboard-monitoring
sudo docker compose down
sudo docker compose build --no-cache backend
sudo docker compose up -d
sudo docker compose logs backend -f | grep -i "認証\|auth" &
# 数秒待ってからCtrl+Cで停止
```

---

## 🔧 トラブルシューティング

### 認証モジュールが読み込まれない場合

1. **マウント設定を確認**:
   ```bash
   # document-automation
   cd ~/nas-project/document-automation
   grep -A 2 "nas-dashboard" docker-compose.yml
   
   # nas-dashboard-monitoring
   cd ~/nas-project/nas-dashboard-monitoring
   grep -A 2 "nas-dashboard" docker-compose.yml
   ```

   **期待される設定**:
   ```yaml
   volumes:
     - /home/AdminUser/nas-project/nas-dashboard:/nas-project/nas-dashboard:ro
   ```

2. **コンテナ内でパスを確認**:
   ```bash
   # document-automation
   sudo docker exec doc-automation-web ls -la /nas-project/nas-dashboard/utils/
   
   # nas-dashboard-monitoring
   sudo docker exec nas-dashboard-monitoring-backend-1 ls -la /nas-project/nas-dashboard/utils/
   ```

3. **Pythonで直接インポートをテスト**:
   ```bash
   # document-automation
   sudo docker exec doc-automation-web python -c "import sys; sys.path.insert(0, '/nas-project/nas-dashboard'); from pathlib import Path; print('Path exists:', Path('/nas-project/nas-dashboard/utils/auth_common.py').exists()); import importlib.util; spec = importlib.util.spec_from_file_location('auth_common', '/nas-project/nas-dashboard/utils/auth_common.py'); print('Spec loaded:', spec is not None)"
   
   # nas-dashboard-monitoring
   sudo docker exec nas-dashboard-monitoring-backend-1 python -c "import sys; sys.path.insert(0, '/nas-project/nas-dashboard'); from pathlib import Path; print('Path exists:', Path('/nas-project/nas-dashboard/utils/auth_common.py').exists()); import importlib.util; spec = importlib.util.spec_from_file_location('auth_common', '/nas-project/nas-dashboard/utils/auth_common.py'); print('Spec loaded:', spec is not None)"
   ```

### AUTH_ENABLEDがFalseの場合

1. **起動ログを確認**:
   ```bash
   sudo docker compose logs <サービス名> | grep -i "認証\|auth" | tail -30
   ```

2. **エラーメッセージを確認**:
   - "認証モジュールのパスが見つかりません" → マウント設定の問題
   - "認証モジュールファイルが見つかりません" → ファイルパスの問題
   - "認証モジュールをインポートできませんでした" → インポートエラー

---

## 📝 確認チェックリスト

- [ ] 起動ログに「認証モジュールを読み込みました」が表示される
- [ ] `/nas-project/nas-dashboard/utils/auth_common.py`が存在する
- [ ] `docker-compose.yml`のマウント設定が正しい
- [ ] コンテナ再起動後に認証が機能する
- [ ] `curl`でHTTP 307（リダイレクト）が返される

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

