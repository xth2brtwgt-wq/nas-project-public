# 🔍 ドキュメント自動処理システム・モニタリング画面 認証ログ確認

**作成日**: 2025-11-04  
**目的**: `document-automation`と`nas-dashboard-monitoring`の認証ログを確認

---

## ❌ 問題

`[AUTH]`ログが表示されていません。起動ログ全体を確認する必要があります。

---

## 🔍 確認手順

### ステップ1: document-automationの起動ログ全体を確認

```bash
cd ~/nas-project/document-automation
sudo docker compose logs web | tail -100
```

**確認ポイント**:
- `[AUTH]`ログが表示されているか
- エラーメッセージが表示されているか
- 認証モジュールの読み込みコードが実行されているか

### ステップ2: nas-dashboard-monitoringの起動ログ全体を確認

```bash
cd ~/nas-project/nas-dashboard-monitoring
sudo docker compose logs backend | tail -100
```

**確認ポイント**:
- `[AUTH]`ログが表示されているか
- エラーメッセージが表示されているか
- 認証モジュールの読み込みコードが実行されているか

### ステップ3: コンテナ内でコードを確認

```bash
# document-automation
sudo docker exec doc-automation-web cat /app/app/api/main.py | grep -A 10 "\[AUTH\]"

# nas-dashboard-monitoring
sudo docker exec nas-dashboard-monitoring-backend-1 cat /app/app/main.py | grep -A 10 "\[AUTH\]"
```

**期待されるコード**:
```python
logger.info("[AUTH] 認証モジュールの読み込みを開始します")
nas_dashboard_path = Path('/nas-project/nas-dashboard')
logger.info(f"[AUTH] nas_dashboard_path: {nas_dashboard_path}")
...
```

### ステップ4: ログレベルを確認

```bash
# document-automation
sudo docker exec doc-automation-web python -c "import logging; print(logging.getLogger().level); print(logging.INFO); print(logging.getLogger().level <= logging.INFO)"

# nas-dashboard-monitoring
sudo docker exec nas-dashboard-monitoring-backend-1 python -c "import logging; print(logging.getLogger().level); print(logging.INFO); print(logging.getLogger().level <= logging.INFO)"
```

**期待される結果**:
```
20
20
True
```

---

## 🔧 トラブルシューティング

### ログが表示されない場合

1. **ログレベルを確認**:
   ```bash
   sudo docker exec <コンテナ名> python -c "import logging; logging.basicConfig(level=logging.DEBUG); logger = logging.getLogger(); logger.info('TEST')"
   ```

2. **標準出力を確認**:
   ```bash
   sudo docker compose logs <サービス名> 2>&1 | tail -100
   ```

3. **ファイルログを確認**:
   ```bash
   sudo docker exec <コンテナ名> cat /app/logs/app.log | tail -50
   ```

### コードが実行されていない場合

1. **コンテナ内でコードを確認**:
   ```bash
   sudo docker exec <コンテナ名> python -c "
   import sys
   sys.path.insert(0, '/app')
   from app.api.main import AUTH_ENABLED
   print(f'AUTH_ENABLED: {AUTH_ENABLED}')
   "
   ```

2. **完全再ビルド**:
   ```bash
   cd ~/nas-project/<サービス名>
   sudo docker compose down
   sudo docker compose build --no-cache <サービス名>
   sudo docker compose up -d
   ```

---

## 📝 確認チェックリスト

- [ ] 起動ログ全体を確認
- [ ] `[AUTH]`ログが表示されているか確認
- [ ] コンテナ内でコードが正しいか確認
- [ ] ログレベルが正しいか確認
- [ ] エラーメッセージがないか確認

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

