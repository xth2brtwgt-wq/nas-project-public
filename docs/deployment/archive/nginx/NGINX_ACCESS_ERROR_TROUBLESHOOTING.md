# 🚨 Nginx Proxy Manager アクセスエラー トラブルシューティング

**作成日**: 2025-01-27  
**対象**: NASシステムにアクセスできない問題の解決

---

## 📋 概要

NASシステム（`https://yoshi-nas-sys.duckdns.org:8443`）にアクセスできない問題を解決する方法を説明します。

---

## 🔍 緊急確認項目

### 1. Nginx Proxy Managerのコンテナの状態確認

```bash
# NAS環境で実行
ssh -p 23456 AdminUser@192.168.68.110

# Nginx Proxy Managerのコンテナの状態を確認
docker ps | grep nginx-proxy-manager

# Nginx Proxy Managerのコンテナのログを確認
docker logs nginx-proxy-manager --tail 100
```

### 2. Nginxの設定ファイルの構文エラー確認

```bash
# Nginx Proxy Managerコンテナ内でNginxの設定を確認
docker exec nginx-proxy-manager nginx -t
```

### 3. Nginx Proxy Managerの再起動

```bash
# Nginx Proxy Managerのコンテナを再起動
docker restart nginx-proxy-manager

# 再起動後のログを確認
docker logs nginx-proxy-manager --tail 50
```

---

## 🔧 トラブルシューティング手順

### ステップ1: Nginx Proxy Managerの状態確認

```bash
# コンテナの状態を確認
docker ps -a | grep nginx-proxy-manager

# コンテナが停止している場合は起動
docker start nginx-proxy-manager

# コンテナが再起動を繰り返している場合はログを確認
docker logs nginx-proxy-manager --tail 200
```

### ステップ2: Nginxの設定ファイルの構文エラー確認

```bash
# Nginxの設定ファイルの構文を確認
docker exec nginx-proxy-manager nginx -t
```

**エラーが表示された場合**:
- 設定ファイルに構文エラーがある可能性があります
- Custom Nginx Configurationの設定を確認してください

### ステップ3: 設定のロールバック（必要に応じて）

**方法1: Nginx Proxy ManagerのWeb UIから設定を削除**

1. **内部ネットワークからNginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hosts → yoshi-nas-sys.duckdns.org → Advanced → Custom Nginx Configuration**

3. **設定を削除または元の設定に戻す**

4. **「Save」をクリック**

**方法2: 設定ファイルを直接編集（上級者向け）**

```bash
# Nginx Proxy Managerの設定ファイルを確認
docker exec nginx-proxy-manager ls -la /data/nginx/proxy_host/

# 設定ファイルを編集（必要に応じて）
docker exec -it nginx-proxy-manager sh
# コンテナ内で設定ファイルを編集
```

---

## 🔍 よくある原因と解決方法

### 1. 設定ファイルの構文エラー

**症状**: Nginxが起動しない、またはエラーログに構文エラーが表示される

**解決方法**:
1. Custom Nginx Configurationの設定を確認
2. 構文エラーを修正
3. Nginx Proxy Managerを再起動

### 2. ポートの競合

**症状**: ポート8443が使用できない

**解決方法**:
```bash
# ポート8443が使用されているか確認
sudo netstat -tlnp | grep 8443
# または
sudo ss -tlnp | grep 8443
```

### 3. ファイアウォールの設定

**症状**: 外部からアクセスできない

**解決方法**:
1. NAS管理画面のファイアウォール設定を確認
2. ポート8443が許可されているか確認

### 4. Nginx Proxy Managerのコンテナの問題

**症状**: コンテナが停止している、または再起動を繰り返している

**解決方法**:
```bash
# コンテナを再起動
docker restart nginx-proxy-manager

# ログを確認
docker logs nginx-proxy-manager --tail 200
```

---

## 📊 確認コマンド一覧

```bash
# 1. Nginx Proxy Managerのコンテナの状態確認
docker ps | grep nginx-proxy-manager

# 2. Nginx Proxy Managerのログ確認
docker logs nginx-proxy-manager --tail 100

# 3. Nginxの設定ファイルの構文確認
docker exec nginx-proxy-manager nginx -t

# 4. ポート8443が使用されているか確認
sudo netstat -tlnp | grep 8443

# 5. Nginx Proxy Managerのコンテナを再起動
docker restart nginx-proxy-manager

# 6. 再起動後のログを確認
docker logs nginx-proxy-manager --tail 50
```

---

## 🚨 緊急対応

### 設定を元に戻す（緊急時）

1. **内部ネットワークからNginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hosts → yoshi-nas-sys.duckdns.org → Advanced → Custom Nginx Configuration**

3. **最近追加した設定（`proxy_hide_header Date;`）を削除**

4. **「Save」をクリック**

5. **アクセスできるか確認**

---

## 📚 参考資料

- **Nginx Proxy Manager最終設定**: `docs/deployment/NGINX_FINAL_CONFIG.md`
- **重複ヘッダー警告の修正ガイド**: `docs/deployment/DUPLICATE_HEADER_FIX_GUIDE.md`
- **セキュリティ対策設定状況の確認結果**: `docs/deployment/SECURITY_STATUS_VERIFICATION.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

