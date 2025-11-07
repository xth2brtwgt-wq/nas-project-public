# 🔒 Nginx Proxy Manager - セキュリティヘッダー設定（レート制限なし）

**作成日**: 2025-01-27  
**対象**: Nginx Proxy Managerでセキュリティヘッダーを設定する際にProxy Hostがオフラインになる問題の解決

---

## 📋 概要

セキュリティヘッダーを設定するとProxy Hostがオフラインになる問題の解決方法を説明します。

**原因**: `limit_req_zone`は`http`コンテキストでしか使用できません。Nginx Proxy ManagerのCustom Nginx Configurationは`server`コンテキスト内に配置されるため、`limit_req_zone`を使用すると構文エラーになります。

**解決方法**: セキュリティヘッダーのみを追加し、レート制限は削除します。

---

## ⚠️ 問題の原因

### `limit_req_zone`が使用できない理由

`limit_req_zone`は`http`コンテキストでしか使用できません。Nginx Proxy ManagerのCustom Nginx Configurationは`server`コンテキスト内に配置されるため、以下の設定は構文エラーになります：

```nginx
# ❌ これはエラーになる（serverコンテキストでは使用できない）
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req zone=general burst=20 nodelay;
```

**エラーメッセージ**:
```
nginx: [emerg] "limit_req_zone" directive is not allowed here
```

---

## ✅ 解決方法

### セキュリティヘッダーのみを追加（レート制限は削除）

既存のNginx設定の先頭に、以下のセキュリティヘッダーのみを追加します：

```nginx
# ==========================================
# セキュリティヘッダー設定
# ==========================================
# グローバルに適用（すべてのlocationブロックの前に記述）

# HSTS（HTTP Strict Transport Security）
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# XSS保護
add_header X-XSS-Protection "1; mode=block" always;

# クリックジャッキング対策
add_header X-Frame-Options "SAMEORIGIN" always;

# MIMEタイプスニッフィング対策
add_header X-Content-Type-Options "nosniff" always;

# リファラーポリシー
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Content Security Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.socket.io; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' data: https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; connect-src 'self' wss: ws: http: https:; form-action 'self'; frame-ancestors 'self';" always;

# ==========================================
# 重複ヘッダーの削除
# ==========================================
# バックエンドから送信されるDateヘッダーを削除（Nginxが自動的に設定するため）
proxy_hide_header Date;

# ==========================================
# 静的ファイル・API・WebSocket設定
# 順序が重要：より具体的なパスを先に記述
# ==========================================
# ... (既存の設定を続ける) ...
```

**重要**: `limit_req_zone`と`limit_req`は削除してください。

---

## 🚀 設定手順

### ステップ1: Nginx Proxy ManagerのWeb UIにアクセス

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブを開く**

3. **yoshi-nas-sys.duckdns.orgのProxy Hostを編集**

4. **「Advanced」タブを開く**

5. **Custom Nginx Configurationを確認**
   - 既存の設定を確認

---

### ステップ2: セキュリティヘッダーを追加

既存の設定の先頭に、以下のセキュリティヘッダーを追加します：

```nginx
# ==========================================
# セキュリティヘッダー設定
# ==========================================

# HSTS（HTTP Strict Transport Security）
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# XSS保護
add_header X-XSS-Protection "1; mode=block" always;

# クリックジャッキング対策
add_header X-Frame-Options "SAMEORIGIN" always;

# MIMEタイプスニッフィング対策
add_header X-Content-Type-Options "nosniff" always;

# リファラーポリシー
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Content Security Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.socket.io; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' data: https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; connect-src 'self' wss: ws: http: https:; form-action 'self'; frame-ancestors 'self';" always;
```

**重要**: 
- 既存の設定の先頭に追加してください
- `limit_req_zone`と`limit_req`は追加しないでください

---

### ステップ3: 設定を保存

1. **「Save」をクリック**

2. **Proxy Hostのステータスを確認**
   - 「Online」になっていることを確認

3. **設定が正しく適用されたか確認**
   ```bash
   # Nginx設定の構文チェック
   docker exec nginx-proxy-manager nginx -t
   ```

---

## 🔍 セキュリティヘッダーの説明

### 1. Strict-Transport-Security (HSTS)
- **効果**: HTTPS接続を強制し、中間者攻撃を防止
- **設定**: 2年間（63072000秒）有効

### 2. X-XSS-Protection
- **効果**: XSS（クロスサイトスクリプティング）攻撃を防止
- **設定**: ブラウザのXSS保護を有効化

### 3. X-Frame-Options
- **効果**: クリックジャッキング攻撃を防止
- **設定**: 同一オリジンからのみフレーム表示を許可

### 4. X-Content-Type-Options
- **効果**: MIMEタイプスニッフィングを防止
- **設定**: コンテンツタイプの推測を無効化

### 5. Referrer-Policy
- **効果**: リファラー情報の漏洩を防止
- **設定**: 同一オリジンまたはHTTPS接続時のみリファラーを送信

### 6. Content-Security-Policy
- **効果**: XSS攻撃やデータインジェクション攻撃を防止
- **設定**: スクリプト、スタイル、画像、フォント、接続のソースを制限
- **CDN許可**: Bootstrap、Font Awesome、Socket.IOなどの外部CDNを許可

---

## ⚠️ レート制限について

### レート制限が使用できない理由

`limit_req_zone`は`http`コンテキストでしか使用できません。Nginx Proxy ManagerのCustom Nginx Configurationは`server`コンテキスト内に配置されるため、レート制限は使用できません。

### 代替手段

レート制限が必要な場合、以下の代替手段を検討してください：

1. **Nginx Proxy ManagerのAccess Lists機能を使用**
   - Nginx Proxy ManagerのWeb UI → Access Lists → 新しいアクセスリストを作成
   - IPアドレスベースの制限を設定

2. **アプリケーションレベルでレート制限を実装**
   - 各アプリケーション（Flask、FastAPIなど）でレート制限を実装

3. **Fail2banを使用**
   - 既にFail2banが稼働中なので、これで十分な保護が提供されています

---

## ✅ 設定後の確認

### 1. セキュリティヘッダーの確認

```bash
# 外部からHTTPSでアクセスしてヘッダーを確認
curl -I https://yoshi-nas-sys.duckdns.org:8443/

# セキュリティヘッダーが含まれていることを確認
# 以下のヘッダーが表示されることを確認：
# - Strict-Transport-Security
# - X-Frame-Options
# - X-Content-Type-Options
# - X-XSS-Protection
# - Referrer-Policy
# - Content-Security-Policy
```

### 2. 動作確認

各サービスにアクセスして、正常に動作することを確認：

- `https://yoshi-nas-sys.duckdns.org:8443/analytics/`
- `https://yoshi-nas-sys.duckdns.org:8443/monitoring/`
- `https://yoshi-nas-sys.duckdns.org:8443/meetings/`
- `https://yoshi-nas-sys.duckdns.org:8443/documents/`
- `https://yoshi-nas-sys.duckdns.org:8443/youtube/`

---

## 🔍 トラブルシューティング

### 問題1: 設定を追加してもProxy Hostがオフラインになる

**確認項目**:
1. 設定の構文エラーがないか確認
2. `limit_req_zone`や`limit_req`が含まれていないか確認

**解決方法**:
- `limit_req_zone`と`limit_req`を削除
- Nginx設定の構文チェックを実行: `docker exec nginx-proxy-manager nginx -t`

---

### 問題2: セキュリティヘッダーが表示されない

**確認項目**:
1. 設定が正しく保存されているか確認
2. Nginx Proxy Managerが再起動されているか確認

**解決方法**:
- Nginx Proxy Managerを再起動: `docker restart nginx-proxy-manager`
- ブラウザのキャッシュをクリア

---

## 📚 参考資料

- **Nginx Proxy Manager最終設定**: `docs/deployment/NGINX_FINAL_CONFIG.md`
- **セキュリティヘッダー完全設定ガイド**: `docs/deployment/NGINX_SECURITY_HEADERS_COMPLETE.md`
- **セキュリティ対策の残課題まとめ**: `docs/deployment/REMAINING_TASKS_SUMMARY.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

