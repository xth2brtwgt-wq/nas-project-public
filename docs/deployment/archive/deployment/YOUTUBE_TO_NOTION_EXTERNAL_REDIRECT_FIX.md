# ✅ YouTube to Notion 外部アクセス時のリダイレクトURL修正

**作成日**: 2025-11-04  
**目的**: 外部アクセス時に外部URLにリダイレクトされるように修正

---

## ❌ 問題

外部からアクセス（`https://yoshi-nas-sys.duckdns.org:8443/youtube`）すると、ローカルURL（`http://192.168.68.110:9001/login`）にリダイレクトされています。

ログを見ると、ヘッダー情報（`X-Forwarded-Host`、`Host`など）が表示されていません。これは、コンテナが古いコードを実行している可能性があります。

---

## ✅ 修正手順

### ステップ1: コンテナを完全停止

```bash
cd ~/nas-project/youtube-to-notion
sudo docker compose down
```

### ステップ2: Dockerイメージを完全再ビルド

```bash
sudo docker compose build --no-cache
```

### ステップ3: コンテナを起動

```bash
sudo docker compose up -d
```

### ステップ4: 外部からアクセス

ブラウザまたはcurlで外部URLにアクセス：

```bash
# 外部からアクセス（Nginx Proxy Manager経由）
curl -v https://yoshi-nas-sys.duckdns.org:8443/youtube
```

**期待される結果**:
```
< HTTP/2 302
< Location: https://yoshi-nas-sys.duckdns.org:8443/login
```

### ステップ5: ログを確認

```bash
# 認証関連のログを確認（ヘッダー情報が表示される）
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
[AUTH] 認証が必要です: / -> https://yoshi-nas-sys.duckdns.org:8443/login
```

---

## 📝 クイックコマンド（一括実行）

```bash
cd ~/nas-project/youtube-to-notion

# 1. コンテナを完全停止
echo "=== コンテナを完全停止 ==="
sudo docker compose down

# 2. Dockerイメージを完全再ビルド
echo ""
echo "=== Dockerイメージを完全再ビルド ==="
sudo docker compose build --no-cache

# 3. コンテナを起動
echo ""
echo "=== コンテナを起動 ==="
sudo docker compose up -d

# 4. 起動ログを確認
echo ""
echo "=== 起動ログを確認 ==="
sudo docker compose logs youtube-to-notion | grep -i "認証\|auth"

# 5. 外部からアクセス（ブラウザで https://yoshi-nas-sys.duckdns.org:8443/youtube にアクセス）

# 6. ログを確認
echo ""
echo "=== 認証関連のログを確認 ==="
sudo docker compose logs youtube-to-notion | grep -i "\[AUTH\]" | tail -20
```

---

## 🔧 トラブルシューティング

### ログにヘッダー情報が表示されない場合

1. **コンテナが古いコードを実行している可能性**:
   - 完全再ビルドを実行してください

2. **リクエストがアプリケーションに到達していない可能性**:
   - Nginx Proxy Managerの設定を確認してください

### 外部アクセス判定がFalseになる場合

1. **リクエストヘッダーを確認**:
   ```bash
   sudo docker compose logs youtube-to-notion | grep -i "\[AUTH\] Host\|X-Forwarded"
   ```

2. **Nginx Proxy Managerの設定を確認**:
   - Advancedタブで`X-Forwarded-Host`ヘッダーが設定されているか確認

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

