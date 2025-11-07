# 🔧 Nginx Proxy Manager 重複locationブロックの修正

**作成日**: 2025-01-27  
**対象**: 重複したlocationブロックによる問題の解決

---

## 📋 問題の原因

### 確認結果

設定ファイル（`/data/nginx/proxy_host/6.conf`）を確認したところ、**重複したlocationブロック**が存在しています：

1. **カスタム設定（580-784行目）**: 詳細なlocationブロック
   - `/analytics/static/`, `/analytics/api/`
   - `/monitoring/static/`, `/monitoring/api/`, `/monitoring/ws`
   - `/meetings/static/`, `/meetings/socket.io/`, `/meetings/api/`
   - `/documents/static/`, `/documents/api/`, `/documents/status`
   - `/youtube/static/`, `/youtube/socket.io/`, `/youtube/api/`

2. **Nginx Proxy Managerの自動生成設定（786-1016行目）**: シンプルなlocationブロック
   - `/analytics`
   - `/monitoring`
   - `/documents`
   - `/meetings`
   - `/youtube`
   - `/` (ルート)

### 問題点

- **重複したlocationブロック**が競合している可能性
- Nginxは最初にマッチしたlocationブロックを使用するため、予期しない動作が発生する可能性
- カスタム設定の詳細なlocationブロックが正しく動作しない可能性

---

## 🔧 解決方法

### 方法1: Nginx Proxy ManagerのWeb UIで各Proxy Hostを削除（推奨）

**理由**:
- Nginx Proxy Managerは、各サービスに対して個別のProxy Hostを作成する必要があります
- 1つのProxy Hostに複数のlocationブロックを設定すると、競合が発生する可能性があります

**手順**:
1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hostsタブを確認**
   - 各サービス（/analytics, /monitoring, /documents, /meetings, /youtube）に対して個別のProxy Hostが作成されているか確認

3. **重複しているProxy Hostを削除**
   - 同じドメイン（yoshi-nas-sys.duckdns.org）に対して複数のProxy Hostが存在する場合、不要なものを削除

4. **Custom Nginx Configurationの設定を確認**
   - 1つのProxy Host（yoshi-nas-sys.duckdns.org）のみにCustom Nginx Configurationを設定

---

### 方法2: Custom Nginx Configurationの設定を調整

**現在の問題**:
- Custom Nginx Configurationに詳細なlocationブロックを設定している
- Nginx Proxy Managerが自動生成するlocationブロックと競合している

**解決策**:
- Custom Nginx Configurationの設定を、locationブロックの外（serverブロックレベル）の設定のみに変更
- または、Nginx Proxy ManagerのWeb UIで各サービスのProxy Hostを個別に作成

---

## 🚀 推奨される設定方法

### オプション1: 1つのProxy HostでCustom Nginx Configurationを使用（現在の方法）

**設定内容**:
- Custom Nginx Configurationに詳細なlocationブロックを設定
- Nginx Proxy ManagerのWeb UIで各サービスのProxy Hostを**作成しない**（または削除）

**注意事項**:
- Nginx Proxy ManagerのWeb UIで各サービスを個別に設定すると、自動生成されるlocationブロックと競合します
- Custom Nginx Configurationのみを使用する場合は、Web UIでの個別設定を避ける必要があります

---

### オプション2: 各サービスを個別のProxy Hostとして作成（推奨）

**設定内容**:
- 各サービス（/analytics, /monitoring, /documents, /meetings, /youtube）に対して個別のProxy Hostを作成
- Custom Nginx Configurationは使用しない（または最小限に）

**メリット**:
- Nginx Proxy ManagerのWeb UIで管理しやすい
- 設定の競合が発生しない

---

## 🔍 現在の設定の確認

### 設定ファイルの構造

```
server {
  # ... (基本設定) ...
  
  # Custom Nginx Configuration（580-784行目）
  proxy_hide_header Date;
  location ^~ /analytics/static/ { ... }
  location ~ ^/analytics/api/(.*)$ { ... }
  # ... (他のカスタムlocationブロック) ...
  
  # Nginx Proxy Managerの自動生成設定（786-1016行目）
  location /analytics { ... }
  location /monitoring { ... }
  location /documents { ... }
  location /meetings { ... }
  location /youtube { ... }
  location / { ... }
}
```

### 問題点

- カスタム設定のlocationブロック（`^~ /analytics/static/`）と自動生成設定のlocationブロック（`/analytics`）が競合している可能性
- Nginxは最初にマッチしたlocationブロックを使用するため、予期しない動作が発生する可能性

---

## 🔧 修正手順

### ステップ1: Nginx Proxy ManagerのWeb UIで設定を確認

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hostsタブを確認**
   - yoshi-nas-sys.duckdns.org に対して複数のProxy Hostが存在するか確認
   - 各サービス（/analytics, /monitoring, /documents, /meetings, /youtube）に対して個別のProxy Hostが作成されているか確認

### ステップ2: 重複しているProxy Hostを削除

**確認方法**:
- Proxy Hostsタブで、同じドメイン（yoshi-nas-sys.duckdns.org）に対して複数のProxy Hostが存在する場合、不要なものを削除

**推奨設定**:
- 1つのProxy Host（yoshi-nas-sys.duckdns.org）のみを使用
- Custom Nginx Configurationで詳細なlocationブロックを設定
- 他のProxy Hostは削除

### ステップ3: Custom Nginx Configurationの設定を確認

**現在の設定**:
- Custom Nginx Configurationに詳細なlocationブロックが設定されている
- これは正しい設定です

**注意事項**:
- Nginx Proxy ManagerのWeb UIで各サービスを個別に設定すると、自動生成されるlocationブロックと競合します
- Custom Nginx Configurationのみを使用する場合は、Web UIでの個別設定を避ける必要があります

---

## 📊 確認コマンド

```bash
# 設定ファイルの内容を確認
docker exec nginx-proxy-manager cat /data/nginx/proxy_host/6.conf | grep -E "^  location" | head -20

# Nginxの設定ファイルの構文を確認
docker exec nginx-proxy-manager nginx -t

# Nginx Proxy Managerのログを確認
docker logs nginx-proxy-manager --tail 50
```

---

## 📚 参考資料

- **Nginx Proxy Manager最終設定**: `docs/deployment/NGINX_FINAL_CONFIG.md`
- **Nginx Proxy Manager設定復旧ガイド**: `docs/deployment/NGINX_CONFIG_RECOVERY.md`
- **Nginx Proxy Managerアクセスエラーのトラブルシューティング**: `docs/deployment/NGINX_ACCESS_ERROR_TROUBLESHOOTING.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

