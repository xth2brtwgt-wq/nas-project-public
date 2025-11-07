# ✅ 外部アクセス時のリダイレクトURL確認

**作成日**: 2025-11-04  
**目的**: 外部アクセス時に外部URLにリダイレクトされるか確認

---

## 🔍 確認手順

### ステップ1: 外部からアクセス

ブラウザまたはcurlで外部URLにアクセス：

```bash
# 外部からアクセス（Nginx Proxy Manager経由）
curl -v https://yoshi-nas-sys.duckdns.org:8443/analytics/
```

**期待される動作**:
- HTTP 307（リダイレクト）
- `Location: https://yoshi-nas-sys.duckdns.org:8443/login` ヘッダーが含まれる

### ステップ2: ログを確認

```bash
cd ~/nas-project/amazon-analytics

# 認証関連のログを確認
sudo docker compose logs web | grep -i "\[AUTH\]" | tail -20

# 最新のアクセスログを確認
sudo docker compose logs web --tail 50
```

**期待されるログ**:
```
[AUTH] X-Forwarded-Host: yoshi-nas-sys.duckdns.org:8443
[AUTH] Host: yoshi-nas-sys.duckdns.org:8443
[AUTH] X-Forwarded-Proto: https
[AUTH] ホスト名: yoshi-nas-sys.duckdns.org:8443, 外部アクセス判定: True
[AUTH] 外部アクセスを検出。ログインURL: https://yoshi-nas-sys.duckdns.org:8443/login
```

### ステップ3: 内部からアクセス（確認）

```bash
# 内部からアクセス（直接ポート）
curl -v http://192.168.68.110:8001/
```

**期待される動作**:
- HTTP 307（リダイレクト）
- `Location: http://192.168.68.110:9001/login` ヘッダーが含まれる

**期待されるログ**:
```
[AUTH] Host: 192.168.68.110:8001
[AUTH] ホスト名: 192.168.68.110:8001, 外部アクセス判定: False
[AUTH] 内部アクセスを検出。ログインURL: http://192.168.68.110:9001/login
```

---

## 🔧 トラブルシューティング

### 外部アクセス判定がFalseになる場合

1. **X-Forwarded-Hostヘッダーを確認**:
   ```bash
   sudo docker compose logs web | grep -i "X-Forwarded-Host"
   ```

2. **Nginx Proxy Managerの設定を確認**:
   - Nginx Proxy ManagerのProxy Host設定で、`X-Forwarded-Host`ヘッダーが正しく設定されているか確認
   - Advancedタブでカスタムヘッダーが設定されているか確認

3. **ホスト名の判定ロジックを確認**:
   - `yoshi-nas-sys.duckdns.org`が含まれているか
   - ポート番号が`8443`か

### ログが表示されない場合

1. **ログレベルを確認**:
   ```bash
   sudo docker compose logs web | grep -i "logging\|level"
   ```

2. **デバッグログを有効化**:
   - `auth_common.py`の`logger.debug`が実行されるように、ログレベルを`DEBUG`に設定

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

