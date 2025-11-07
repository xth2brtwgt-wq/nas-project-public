# 🔍 Nginx Proxy Manager ログファイルの場所確認ガイド

**作成日**: 2025-01-27  
**対象**: Nginx Proxy Managerのログファイルの場所を確認する方法

---

## 📋 概要

Nginx Proxy Managerのログファイルの場所を確認し、アクセスログとエラーログを特定する方法を説明します。

---

## 🔍 ログファイルの場所確認

### ステップ1: ログディレクトリの存在確認

```bash
# ログディレクトリの存在確認
docker exec nginx-proxy-manager ls -ld /data/logs/

# ログディレクトリの内容を確認
docker exec nginx-proxy-manager ls -la /data/logs/

# ログディレクトリの内容を再帰的に確認
docker exec nginx-proxy-manager find /data -name "*.log" -type f
```

### ステップ2: ログファイルの場所を特定

```bash
# すべてのログファイルを検索
docker exec nginx-proxy-manager find /data -name "*.log" -type f

# アクセスログを検索
docker exec nginx-proxy-manager find /data -name "*access*.log" -type f

# エラーログを検索
docker exec nginx-proxy-manager find /data -name "*error*.log" -type f
```

### ステップ3: Nginx Proxy Managerの設定を確認

```bash
# Nginx Proxy Managerの設定ファイルを確認
docker exec nginx-proxy-manager cat /etc/nginx/nginx.conf | grep -i log

# Nginx Proxy Managerの設定ディレクトリを確認
docker exec nginx-proxy-manager ls -la /etc/nginx/conf.d/

# プロキシホストの設定を確認
docker exec nginx-proxy-manager find /data/nginx -name "*.conf" -type f
```

---

## 🔧 ログファイルが見つからない場合

### 確認事項

1. **ログディレクトリの存在確認**
   ```bash
   docker exec nginx-proxy-manager ls -ld /data/logs/
   ```

2. **Nginx Proxy Managerの設定を確認**
   - Nginx Proxy ManagerのWeb UI → Proxy Hosts → 各Proxy Hostの設定を確認
   - 「Access Log」が有効になっているか確認

3. **ログファイルの生成を確認**
   ```bash
   # 外部からアクセス
   curl -I https://yoshi-nas-sys.duckdns.org:8443/
   
   # アクセス後にログディレクトリを確認
   docker exec nginx-proxy-manager ls -la /data/logs/
   ```

4. **Nginx Proxy Managerのコンテナを再起動**
   ```bash
   docker restart nginx-proxy-manager
   
   # 再起動後にログディレクトリを確認
   docker exec nginx-proxy-manager ls -la /data/logs/
   ```

---

## 📊 ログファイルの確認方法（見つかった場合）

### アクセスログの確認

```bash
# 特定のproxy-hostのアクセスログを確認（最新100行）
docker exec nginx-proxy-manager tail -100 /data/logs/proxy-host-2_access.log

# アクセスログのサイズを確認
docker exec nginx-proxy-manager ls -lh /data/logs/proxy-host-2_access.log

# アクセス数の多いIPアドレスを確認
docker exec nginx-proxy-manager awk '{print $1}' /data/logs/proxy-host-2_access.log | sort | uniq -c | sort -rn | head -10
```

### エラーログの確認

```bash
# エラーログを確認
docker exec nginx-proxy-manager tail -100 /data/logs/proxy-host-2_error.log

# エラーログのサイズを確認
docker exec nginx-proxy-manager ls -lh /data/logs/proxy-host-2_error.log

# 404エラーの詳細を確認
docker exec nginx-proxy-manager grep " 404 " /data/logs/proxy-host-2_error.log | tail -20
```

---

## 🔧 トラブルシューティング

### ログファイルが見つからない場合

1. **Nginx Proxy Managerの設定を確認**
   - Nginx Proxy ManagerのWeb UI → Proxy Hosts → 各Proxy Hostの設定を確認
   - 「Access Log」が有効になっているか確認

2. **ログディレクトリの権限を確認**
   ```bash
   docker exec nginx-proxy-manager ls -ld /data/logs/
   ```

3. **Nginx Proxy Managerのコンテナを再起動**
   ```bash
   docker restart nginx-proxy-manager
   ```

4. **実際にアクセスしてログが生成されるか確認**
   ```bash
   # 外部からアクセス
   curl -I https://yoshi-nas-sys.duckdns.org:8443/
   
   # アクセス後にログディレクトリを確認
   docker exec nginx-proxy-manager ls -la /data/logs/
   ```

---

## 📚 参考資料

- **Nginx Proxy Managerアクセスログ確認ガイド**: `docs/deployment/NGINX_ACCESS_LOG_CHECK.md`
- **セキュリティ対策設定状況の確認結果**: `docs/deployment/SECURITY_STATUS_VERIFICATION.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

