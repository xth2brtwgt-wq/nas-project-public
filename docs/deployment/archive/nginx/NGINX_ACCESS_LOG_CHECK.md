# 🔍 Nginx Proxy Manager アクセスログ確認ガイド

**作成日**: 2025-01-27  
**対象**: Nginx Proxy Managerのアクセスログを確認する方法

---

## 📋 概要

Nginx Proxy Managerのアクセスログを確認する方法と、どのproxy-hostが実際に使用されているかを特定する方法を説明します。

---

## 🔍 ログファイルの確認方法

### ステップ1: ログファイルの存在確認

```bash
# Nginx Proxy Managerコンテナ内のログファイル一覧を確認
docker exec nginx-proxy-manager ls -lh /data/logs/

# ログファイルのサイズを確認
docker exec nginx-proxy-manager du -h /data/logs/*.log
```

### ステップ2: 使用されているproxy-hostの特定

```bash
# どのproxy-hostが実際に使用されているか確認
# ログファイルのサイズが大きいものが使用されている可能性が高い
docker exec nginx-proxy-manager ls -lhS /data/logs/*_access.log

# 最新のアクセスログを確認（サイズが大きいファイルから）
docker exec nginx-proxy-manager tail -50 /data/logs/proxy-host-2_access.log
docker exec nginx-proxy-manager tail -50 /data/logs/proxy-host-1_access.log
docker exec nginx-proxy-manager tail -50 /data/logs/proxy-host-3_access.log
```

### ステップ3: アクセスログの内容確認

```bash
# 特定のproxy-hostのアクセスログを確認（最新100行）
docker exec nginx-proxy-manager tail -100 /data/logs/proxy-host-2_access.log

# エラーログを確認
docker exec nginx-proxy-manager tail -100 /data/logs/proxy-host-2_error.log

# 不正アクセスのパターンを確認
docker exec nginx-proxy-manager grep -i "401\|403\|404" /data/logs/proxy-host-2_access.log | tail -50

# 特定のIPアドレスからのアクセスを確認
docker exec nginx-proxy-manager grep "192.168.68.110" /data/logs/proxy-host-2_access.log | tail -20
```

---

## 🔍 ログファイルが空の場合

### 確認事項

1. **ログファイルが存在するか確認**
   ```bash
   docker exec nginx-proxy-manager ls -lh /data/logs/proxy-host-2_access.log
   ```

2. **ログファイルのサイズを確認**
   ```bash
   docker exec nginx-proxy-manager du -h /data/logs/proxy-host-2_access.log
   ```

3. **Nginx Proxy Managerの設定を確認**
   - Nginx Proxy ManagerのWeb UI → Proxy Hosts → 各Proxy Hostの設定を確認
   - 「Access Log」が有効になっているか確認

4. **実際にアクセスしてログが生成されるか確認**
   ```bash
   # 外部からアクセス
   curl -I https://yoshi-nas-sys.duckdns.org:8443/
   
   # アクセス後にログを確認
   docker exec nginx-proxy-manager tail -10 /data/logs/proxy-host-2_access.log
   ```

---

## 📊 ログファイルの分析

### アクセスログの形式

Nginx Proxy Managerのアクセスログは、通常のNginxアクセスログ形式です：

```
192.168.68.100 - - [07/Nov/2025:10:44:00 +0000] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0..."
```

### ログの分析例

```bash
# アクセス数の多いIPアドレスを確認
docker exec nginx-proxy-manager awk '{print $1}' /data/logs/proxy-host-2_access.log | sort | uniq -c | sort -rn | head -10

# ステータスコード別のアクセス数を確認
docker exec nginx-proxy-manager awk '{print $9}' /data/logs/proxy-host-2_access.log | sort | uniq -c | sort -rn

# 404エラーの詳細を確認
docker exec nginx-proxy-manager grep " 404 " /data/logs/proxy-host-2_access.log | tail -20

# 401/403エラーの詳細を確認
docker exec nginx-proxy-manager grep -E " 401 | 403 " /data/logs/proxy-host-2_access.log | tail -20
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

### ログファイルが空の場合

1. **実際にアクセスしてログが生成されるか確認**
   ```bash
   # 外部からアクセス
   curl -I https://yoshi-nas-sys.duckdns.org:8443/
   
   # アクセス後にログを確認
   docker exec nginx-proxy-manager tail -10 /data/logs/proxy-host-2_access.log
   ```

2. **Nginx Proxy Managerの設定を確認**
   - Nginx Proxy ManagerのWeb UI → Proxy Hosts → 各Proxy Hostの設定を確認
   - 「Access Log」が有効になっているか確認

---

## 📚 参考資料

- **セキュリティ対策設定状況の確認結果**: `docs/deployment/SECURITY_STATUS_VERIFICATION.md`
- **外部アクセス時のセキュリティ対策ガイド**: `docs/deployment/EXTERNAL_ACCESS_SECURITY.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

