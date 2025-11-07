# 🔧 Nginx Proxy Manager 500 Internal Server Error の解決

**作成日**: 2025-01-27  
**対象**: Custom Nginx Configurationで500エラーが発生する問題の解決

---

## 📋 概要

Custom Nginx Configurationにルートパスへのlocationブロックを追加した後、500 Internal Server Errorが発生する問題の解決方法を説明します。

---

## 🔍 問題の原因

### 確認結果

ルートパスのlocationブロックで、`rewrite`と`proxy_pass`の組み合わせが問題を引き起こしている可能性があります。

**問題のある設定**:
```nginx
location /analytics {
    rewrite ^/analytics(.*)$ $1 break;
    proxy_pass http://192.168.68.110:8001;
    # ... その他の設定 ...
}
```

**問題点**:
- `rewrite`で`break`を使用している場合、`proxy_pass`の後にスラッシュを追加する必要がある
- または、`rewrite`を使わずに`proxy_pass`の後にスラッシュを追加する方が安全

---

## ✅ 解決方法

### 方法1: proxy_passの後にスラッシュを追加（推奨）

`rewrite`を使わずに、`proxy_pass`の後にスラッシュを追加します。

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

**重要な変更点**:
- `rewrite ^/analytics(.*)$ $1 break;` を削除
- `proxy_pass http://192.168.68.110:8001;` → `proxy_pass http://192.168.68.110:8001/;` に変更（末尾にスラッシュを追加）

**動作説明**:
- `proxy_pass`の後にスラッシュ（`/`）がある場合、Nginxは自動的にパスをリライトします
- 例: `/analytics` → `http://192.168.68.110:8001/`
- 例: `/analytics/page` → `http://192.168.68.110:8001/page`

---

### 方法2: rewriteを使う場合（代替案）

`rewrite`を使う場合は、`proxy_pass`の後にスラッシュを追加し、`rewrite`の`break`を削除します。

```nginx
# /analytics のルートパス（amazon-analytics）
location /analytics {
    rewrite ^/analytics(.*)$ $1;
    proxy_pass http://192.168.68.110:8001/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

**注意**: 方法1の方がシンプルで推奨されます。

---

## 🚀 設定手順

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hosts → yoshi-nas-sys.duckdns.org → Advanced → Custom Nginx Configuration**

3. **ルートパスのlocationブロックを修正**
   - 方法1の設定を使用（推奨）

4. **「Save」をクリック**

5. **各サービスにアクセスして確認**
   - `/analytics`
   - `/monitoring`
   - `/meetings`
   - `/documents`
   - `/youtube`

---

## 🔍 エラーログの確認

500エラーが発生した場合、Nginx Proxy Managerのログを確認してください。

```bash
# Nginx Proxy Managerのログを確認
docker logs nginx-proxy-manager --tail 100 | grep -i error

# または、Nginxのエラーログを確認
docker exec nginx-proxy-manager tail -100 /var/log/nginx/error.log
```

---

## 📚 参考資料

- **Nginx Proxy Manager最終設定**: `docs/deployment/NGINX_FINAL_CONFIG.md`
- **Nginx Proxy Manager重複locationブロックの修正**: `docs/deployment/NGINX_DUPLICATE_LOCATION_FIX.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

