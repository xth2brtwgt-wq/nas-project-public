# 🔧 Nginxアクセスログ監視のトラブルシューティング

**作成日**: 2025-01-27  
**対象**: Nginxアクセスログ監視機能のトラブルシューティング

---

## 📋 概要

Nginxアクセスログ監視機能が正常に動作しない場合のトラブルシューティングガイドです。

---

## 🔍 問題の診断

### 問題1: `total_ips_monitored: 0` と `last_check_time: null` のまま

**症状**: APIエンドポイントで監視状況を確認すると、`total_ips_monitored: 0`と`last_check_time: null`のままです。

**原因**: ログファイルにアクセスできていない可能性があります。

**確認手順**:

1. **Nginx Proxy Managerコンテナ名を確認**
   ```bash
   docker ps | grep nginx-proxy-manager
   ```

2. **ログファイルの存在を確認**
   ```bash
   # Nginx Proxy Managerコンテナ内のログファイルを確認
   docker exec nginx-proxy-manager ls -lh /data/logs/
   ```

3. **監視サービスのログを確認**
   ```bash
   # エラーログを確認
   docker compose logs backend --tail 100 | grep -i "nginx\|error"
   ```

---

## 🔧 解決方法

### 解決方法1: Nginx Proxy Managerコンテナ名の確認と修正

**手順**:

1. **Nginx Proxy Managerコンテナ名を確認**
   ```bash
   docker ps | grep nginx-proxy-manager
   ```

2. **コンテナ名が異なる場合は、`nginx_log_monitor.py`を修正**
   
   ファイル: `nas-dashboard-monitoring/app/services/nginx_log_monitor.py`
   
   約150行目付近:
   ```python
   result = subprocess.run(
       ['docker', 'exec', 'nginx-proxy-manager', 'tail', '-1000', log_path],
       # ↑ コンテナ名を実際の名前に変更
   )
   ```

3. **コンテナを再ビルド**
   ```bash
   docker compose up -d --build backend
   ```

### 解決方法2: ログファイルのパスの確認と修正

**手順**:

1. **Nginx Proxy Managerコンテナ内のログファイルを確認**
   ```bash
   docker exec nginx-proxy-manager ls -lh /data/logs/
   ```

2. **ログファイルのパスが異なる場合は、`nginx_log_monitor.py`を修正**
   
   ファイル: `nas-dashboard-monitoring/app/services/nginx_log_monitor.py`
   
   約20行目付近:
   ```python
   self.nginx_log_paths = [
       "/data/logs/proxy-host-6_access.log",  # 実際のパスに変更
   ]
   ```

3. **コンテナを再ビルド**
   ```bash
   docker compose up -d --build backend
   ```

### 解決方法3: Dockerソケットのマウント確認

**手順**:

1. **docker-compose.ymlでDockerソケットがマウントされているか確認**
   
   ファイル: `nas-dashboard-monitoring/docker-compose.yml`
   
   ```yaml
   volumes:
     - /var/run/docker.sock:/var/run/docker.sock:ro
   ```

2. **マウントされていない場合は追加**
   ```yaml
   backend:
     volumes:
       - /var/run/docker.sock:/var/run/docker.sock:ro
   ```

3. **コンテナを再起動**
   ```bash
   docker compose restart backend
   ```

---

## ✅ 動作確認

### 1. ログを確認

```bash
# 監視サービスのログを確認（エラーがないか確認）
docker compose logs backend --tail 100 | grep -i nginx

# 期待される出力:
# 🔍 Nginxアクセスログ監視を開始しました
```

### 2. APIエンドポイントで確認

```bash
# 監視状況を取得
curl http://localhost:8002/api/v1/security/nginx-monitoring/status | python3 -m json.tool

# 期待される出力:
# {
#     "status": "active",
#     "monitored_logs": [...],
#     "thresholds": {...},
#     "total_ips_monitored": 0,  # 初期状態
#     "last_check_time": null    # 初期状態
# }
```

### 3. 数分後に再度確認

```bash
# 数分後に再度確認（ログが分析されているか確認）
curl http://localhost:8002/api/v1/security/nginx-monitoring/status | python3 -m json.tool

# 期待される出力（ログが分析されている場合）:
# {
#     "status": "active",
#     "monitored_logs": [...],
#     "thresholds": {...},
#     "total_ips_monitored": 5,  # 監視中のIP数
#     "last_check_time": "2025-01-27T12:00:00"  # 最後のチェック時刻
# }
```

---

## 🔍 詳細な診断

### 診断スクリプト

以下のコマンドで詳細な診断を行います：

```bash
# 1. Nginx Proxy Managerコンテナ名を確認
echo "=== Nginx Proxy Managerコンテナ名 ==="
docker ps | grep nginx-proxy-manager

# 2. ログファイルの存在を確認
echo "=== ログファイルの存在確認 ==="
docker exec nginx-proxy-manager ls -lh /data/logs/ 2>&1

# 3. ログファイルの内容を確認（最新10行）
echo "=== ログファイルの内容（最新10行） ==="
docker exec nginx-proxy-manager tail -10 /data/logs/proxy-host-6_access.log 2>&1

# 4. 監視サービスのログを確認
echo "=== 監視サービスのログ ==="
docker compose logs backend --tail 50 | grep -i nginx

# 5. Dockerソケットのマウント確認
echo "=== Dockerソケットのマウント確認 ==="
docker compose exec backend ls -la /var/run/docker.sock 2>&1
```

---

## 📚 関連ドキュメント

- [NGINX_ACCESS_LOG_MONITORING.md](NGINX_ACCESS_LOG_MONITORING.md) - Nginxアクセスログ監視の設定方法
- [NGINX_MONITORING_DEPLOY_GUIDE.md](NGINX_MONITORING_DEPLOY_GUIDE.md) - デプロイ手順
- [NGINX_MONITORING_RESTART_GUIDE.md](NGINX_MONITORING_RESTART_GUIDE.md) - 再起動手順

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

