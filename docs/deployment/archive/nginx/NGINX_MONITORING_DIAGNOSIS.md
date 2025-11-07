# 🔍 Nginxアクセスログ監視の診断手順

**作成日**: 2025-01-27  
**対象**: Nginxアクセスログ監視機能の診断

---

## 📋 診断手順

### ステップ1: Nginx Proxy Managerコンテナ名の確認 ✅

```bash
docker ps | grep nginx-proxy-manager
```

**結果**: コンテナ名は`nginx-proxy-manager`で、コード内の設定と一致しています。

---

### ステップ2: ログファイルの存在確認

```bash
# ログディレクトリの内容を確認
docker exec nginx-proxy-manager ls -lh /data/logs/

# ログファイルの内容を確認（最新10行）
docker exec nginx-proxy-manager tail -10 /data/logs/proxy-host-6_access.log 2>&1
```

---

### ステップ3: 監視サービスのログ確認

```bash
# 監視サービスのログを確認（エラーがないか確認）
docker compose logs backend --tail 100 | grep -i "nginx\|error"
```

---

### ステップ4: Dockerソケットのマウント確認

```bash
# Dockerソケットがマウントされているか確認
docker compose exec backend ls -la /var/run/docker.sock 2>&1
```

---

### ステップ5: 手動でログファイルを読み取るテスト

```bash
# 監視サービスから直接ログファイルを読み取れるかテスト
docker compose exec backend docker exec nginx-proxy-manager tail -10 /data/logs/proxy-host-6_access.log 2>&1
```

---

## 🔧 問題の特定

### 問題1: ログファイルが存在しない

**症状**: `ls -lh /data/logs/`でログファイルが見つからない

**解決方法**:
1. Nginx Proxy Managerの設定でアクセスログが有効になっているか確認
2. 実際にアクセスしてログが生成されるか確認
3. ログファイルのパスを確認

### 問題2: ログファイルにアクセスできない

**症状**: `tail`コマンドでエラーが発生する

**解決方法**:
1. Dockerソケットがマウントされているか確認
2. コンテナ間の通信が可能か確認
3. 権限の問題がないか確認

### 問題3: 監視サービスのログにエラーが表示される

**症状**: ログに`Nginxログ監視エラー`や`Nginxログチェックエラー`が表示される

**解決方法**:
1. エラーメッセージの内容を確認
2. コンテナ名やログファイルのパスが正しいか確認
3. Dockerソケットのマウントを確認

---

## ✅ 期待される結果

### 正常な場合

1. **ログファイルの存在確認**
   ```
   -rw-r--r-- 1 root root 5.0M Nov  7 04:00 proxy-host-6_access.log
   ```

2. **ログファイルの内容確認**
   ```
   192.168.68.100 - - [07/Nov/2025:04:00:00 +0000] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0..."
   ```

3. **監視サービスのログ**
   ```
   🔍 Nginxアクセスログ監視を開始しました
   ```

4. **Dockerソケットのマウント確認**
   ```
   srw-rw---- 1 root docker 0 Nov  7 04:00 /var/run/docker.sock
   ```

---

## 📚 関連ドキュメント

- [NGINX_MONITORING_TROUBLESHOOTING.md](NGINX_MONITORING_TROUBLESHOOTING.md) - トラブルシューティングガイド
- [NGINX_ACCESS_LOG_MONITORING.md](NGINX_ACCESS_LOG_MONITORING.md) - 監視機能の設定方法

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

