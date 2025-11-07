# 🔍 ドキュメント自動処理システム・モニタリング画面 認証デバッグ

**作成日**: 2025-11-04  
**目的**: `document-automation`と`nas-dashboard-monitoring`の認証が機能しない原因を調査

---

## ❌ 問題

両方のサービスがHTTP 200を返しており、認証リダイレクトが機能していません。

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
- "認証モジュールのパスが見つかりません" → マウント設定の問題
- "認証モジュールファイルが見つかりません" → ファイルパスの問題
- "認証モジュールをインポートできませんでした" → インポートエラー

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

### ステップ3: コンテナ内でAUTH_ENABLEDを確認

```bash
# document-automation
sudo docker exec doc-automation-web python -c "import sys; sys.path.insert(0, '/nas-project/nas-dashboard'); from pathlib import Path; print('Path exists:', Path('/nas-project/nas-dashboard/utils/auth_common.py').exists())"

# nas-dashboard-monitoring
sudo docker exec nas-dashboard-monitoring-backend-1 python -c "import sys; sys.path.insert(0, '/nas-project/nas-dashboard'); from pathlib import Path; print('Path exists:', Path('/nas-project/nas-dashboard/utils/auth_common.py').exists())"
```

### ステップ4: docker-compose.ymlのマウント設定を確認

```bash
# document-automation
cd ~/nas-project/document-automation
grep -A 5 "nas-dashboard" docker-compose.yml

# nas-dashboard-monitoring
cd ~/nas-project/nas-dashboard-monitoring
grep -A 5 "nas-dashboard" docker-compose.yml
```

**期待される設定**:
```yaml
volumes:
  - /home/AdminUser/nas-project/nas-dashboard:/nas-project/nas-dashboard:ro
```

---

## 🔧 修正方法

### パスが見つからない場合

1. **マウント設定を確認**:
   - `docker-compose.yml`で`/home/AdminUser/nas-project/nas-dashboard:/nas-project/nas-dashboard:ro`が設定されているか確認

2. **コンテナを再起動**:
   ```bash
   cd ~/nas-project/<サービス名>
   sudo docker compose down
   sudo docker compose up -d
   ```

3. **完全再ビルド**:
   ```bash
   cd ~/nas-project/<サービス名>
   sudo docker compose down
   sudo docker compose build --no-cache
   sudo docker compose up -d
   ```

### 認証モジュールが読み込まれない場合

1. **ログを確認**:
   ```bash
   sudo docker compose logs <サービス名> | grep -i "認証\|auth" | tail -30
   ```

2. **エラー内容を確認**:
   - インポートエラーの場合、依存関係を確認
   - パスエラーの場合、マウント設定を確認

---

## 📝 確認チェックリスト

- [ ] 起動ログに「認証モジュールを読み込みました」が表示される
- [ ] `/nas-project/nas-dashboard/utils/auth_common.py`が存在する
- [ ] `docker-compose.yml`のマウント設定が正しい
- [ ] コンテナ再起動後に認証が機能する

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

