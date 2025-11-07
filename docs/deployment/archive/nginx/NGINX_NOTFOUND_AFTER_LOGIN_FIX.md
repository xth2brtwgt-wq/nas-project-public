# 🔧 Nginx Proxy Manager - ログイン後NotFoundエラーの解決

**作成日**: 2025-01-27  
**対象**: ログイン後にボタンをクリックするとNotFoundエラーが表示される問題の解決

---

## 📋 概要

ファイアウォールをOFFにするとダッシュボードは表示されるが、その他の画面のボタンをクリックするとNotFoundエラーが表示される問題の解決方法を説明します。

この問題は、Nginx Proxy Managerの設定やルーティングの問題である可能性があります。

---

## 🔍 問題の原因

### 考えられる原因

1. **ルートパスへのlocationブロックが正しく設定されていない**
   - 各サービスのルートパス（/analytics, /monitoring, /meetings, /documents, /youtube）へのlocationブロックが設定されていない
   - または、locationブロックの設定が間違っている

2. **各サービスのルーティングが正しく設定されていない**
   - 静的ファイルやAPIのパスが正しく設定されていない
   - リダイレクト先のパスが間違っている

3. **Nginx Proxy Managerの設定が正しく適用されていない**
   - Custom Nginx Configurationの設定が正しく保存されていない
   - 設定の構文エラーがある

---

## ✅ 解決方法

### ステップ1: Nginx Proxy Managerの設定を確認

**Nginx Proxy ManagerのWeb UIで確認**:
1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hosts → yoshi-nas-sys.duckdns.org → Advanced → Custom Nginx Configuration**

3. **現在の設定を確認**
   - ルートパスへのlocationブロックが設定されているか確認
   - 各サービスの静的ファイル・API・WebSocket設定が設定されているか確認

---

### ステップ2: ルートパスへのlocationブロックを確認

**各サービスのルートパスへのlocationブロックが設定されているか確認**:

```nginx
# /analytics のルートパス（amazon-analytics）
location /analytics {
    proxy_pass http://192.168.68.110:8001/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /monitoring のルートパス（nas-dashboard-monitoring - Reactアプリ）
location /monitoring {
    proxy_pass http://192.168.68.110:3002/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /meetings のルートパス（meeting-minutes-byc）
location /meetings {
    proxy_pass http://192.168.68.110:5002/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /documents のルートパス（document-automation）
location /documents {
    proxy_pass http://192.168.68.110:8080/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /youtube のルートパス（youtube-to-notion）
location /youtube {
    proxy_pass http://192.168.68.110:8111/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

**確認項目**:
- 各サービスのルートパスへのlocationブロックが設定されているか
- `proxy_pass`の後にスラッシュ（`/`）が追加されているか
- 各サービスのポート番号が正しいか

---

### ステップ3: 静的ファイル・API・WebSocket設定を確認

**各サービスの静的ファイル・API・WebSocket設定が設定されているか確認**:

```nginx
# /analytics の静的ファイル修正（amazon-analytics）
location ^~ /analytics/static/ {
    rewrite ^/analytics/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /analytics のAPI修正（amazon-analytics）
location ~ ^/analytics/api/(.*)$ {
    rewrite ^/analytics/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

**確認項目**:
- 各サービスの静的ファイル設定が設定されているか
- 各サービスのAPI設定が設定されているか
- 各サービスのWebSocket設定が設定されているか（必要な場合）

---

### ステップ4: Nginx設定の構文を確認

**NAS環境で実行**:
```bash
# Nginx設定の構文を確認
docker exec nginx-proxy-manager nginx -t
```

**確認項目**:
- 設定ファイルの構文エラーがないか
- エラーメッセージが表示されていないか

---

### ステップ5: 完全な設定を適用

**`docs/deployment/NGINX_FINAL_CONFIG.md`の完全な設定を適用**:

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hosts → yoshi-nas-sys.duckdns.org → Advanced → Custom Nginx Configuration**

3. **既存の設定を削除**

4. **`docs/deployment/NGINX_FINAL_CONFIG.md`の完全な設定をコピー&ペースト**

5. **「Save」をクリック**

6. **Proxy Hostのステータスを確認**
   - 「Online」になっていることを確認

---

## 🔍 トラブルシューティング

### 問題1: ルートパスへのlocationブロックが設定されていない

**確認項目**:
1. 各サービスのルートパスへのlocationブロックが設定されているか確認

**解決方法**:
- `docs/deployment/NGINX_FINAL_CONFIG.md`の完全な設定を適用
- 各サービスのルートパスへのlocationブロックを追加

---

### 問題2: 静的ファイルやAPIが404エラーになる

**確認項目**:
1. 各サービスの静的ファイル・API設定が設定されているか確認
2. 設定の順序を確認（より具体的なパスを先に記述）

**解決方法**:
- `docs/deployment/NGINX_FINAL_CONFIG.md`の完全な設定を適用
- 各サービスの静的ファイル・API設定を追加

---

### 問題3: 特定のサービスでNotFoundエラーが発生する

**確認項目**:
1. そのサービスのルートパスへのlocationブロックが設定されているか確認
2. そのサービスの静的ファイル・API設定が設定されているか確認
3. そのサービスのポート番号が正しいか確認

**解決方法**:
- そのサービス専用のlocationブロックを追加
- そのサービスの静的ファイル・API設定を追加

---

## 📊 推奨される設定の順序

### locationブロックの順序

1. **セキュリティヘッダー設定**（最上部）
2. **重複ヘッダーの削除**
3. **静的ファイル・API・WebSocket設定**（より具体的なパス）
   - `/analytics/static/`
   - `/analytics/api/`
   - `/monitoring/static/`
   - `/monitoring/api/`
   - `/meetings/static/`
   - `/meetings/api/`
   - `/documents/static/`
   - `/documents/api/`
   - `/youtube/static/`
   - `/youtube/api/`
4. **ルートパス設定**（より一般的なパス）
   - `/analytics`
   - `/monitoring`
   - `/meetings`
   - `/documents`
   - `/youtube`
5. **タイムアウト設定**（最下部）

**重要**: より具体的なパスを先に記述することで、正しいルーティングが行われます。

---

## 📚 参考資料

- **Nginx Proxy Manager最終設定**: `docs/deployment/NGINX_FINAL_CONFIG.md`
- **Nginx Proxy Manager重複locationブロックの修正**: `docs/deployment/NGINX_DUPLICATE_LOCATION_FIX.md`
- **500エラーの修正**: `docs/deployment/NGINX_500_ERROR_FIX.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

