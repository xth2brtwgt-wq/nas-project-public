# ✅ YouTube to Notion 外部アクセス時のリダイレクトURL確認

**作成日**: 2025-11-04  
**目的**: 外部アクセス時にローカルURLにリダイレクトされる問題を確認

---

## ❌ 問題

外部からアクセス（`https://yoshi-nas-sys.duckdns.org:8443/youtube`）すると、ローカルURL（`http://192.168.68.110:9001/login`）にリダイレクトされています。

**期待される動作**:
- `https://yoshi-nas-sys.duckdns.org:8443/login` にリダイレクトされる

---

## 🔍 確認手順

### ステップ1: 外部からアクセスしてログを確認

```bash
cd ~/nas-project/youtube-to-notion

# 外部からアクセス（ブラウザで https://yoshi-nas-sys.duckdns.org:8443/youtube にアクセス）

# ログを確認（認証関連のデバッグログ）
sudo docker compose logs youtube-to-notion | grep -i "\[AUTH\]" | tail -20

# 最新のアクセスログを確認
sudo docker compose logs youtube-to-notion --tail 50
```

**期待されるログ**:
```
[AUTH] X-Forwarded-Host: yoshi-nas-sys.duckdns.org:8443
[AUTH] Host: ...
[AUTH] X-Forwarded-Proto: https
[AUTH] ホスト名: yoshi-nas-sys.duckdns.org:8443, 外部アクセス判定: True
[AUTH] 外部アクセスを検出。ログインURL: https://yoshi-nas-sys.duckdns.org:8443/login
```

### ステップ2: curlで確認

```bash
# 外部からアクセス（Nginx Proxy Manager経由）
curl -v https://yoshi-nas-sys.duckdns.org:8443/youtube
```

**期待される結果**:
```
< HTTP/2 302
< Location: https://yoshi-nas-sys.duckdns.org:8443/login
```

### ステップ3: コンテナを再起動（最新コードを反映）

```bash
cd ~/nas-project/youtube-to-notion

# 最新のコードをプル
git pull origin feature/monitoring-fail2ban-integration

# コンテナを再起動
sudo docker compose restart youtube-to-notion

# ログを確認
sudo docker compose logs youtube-to-notion | grep -i "\[AUTH\]" | tail -20
```

---

## 🔧 トラブルシューティング

### ログに`[AUTH]`が表示されない場合

1. **コンテナを完全再ビルド**:
   ```bash
   sudo docker compose down
   sudo docker compose build --no-cache
   sudo docker compose up -d
   ```

2. **認証モジュールの読み込みを確認**:
   ```bash
   sudo docker compose logs youtube-to-notion | grep -i "認証モジュール"
   ```

### 外部アクセス判定がFalseになる場合

1. **リクエストヘッダーを確認**:
   ```bash
   # コンテナ内でリクエストヘッダーを確認
   sudo docker compose exec youtube-to-notion python -c "
   from flask import request
   # 実際のリクエストで確認する必要があります
   "
   ```

2. **Nginx Proxy Managerの設定を確認**:
   - `/youtube`のCustom Location設定が正しいか
   - Advancedタブで`X-Forwarded-Host`ヘッダーが設定されているか

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

