# 🔄 Nginxアクセスログ監視サービスの再起動ガイド

**作成日**: 2025-01-27  
**対象**: NAS環境でのNginxアクセスログ監視サービスの再起動

---

## 📋 概要

Nginxアクセスログ監視機能を有効にするために、`nas-dashboard-monitoring`サービスのバックエンドを再起動します。

---

## 🚀 再起動手順

### ステップ1: NAS環境にSSH接続

```bash
ssh -p 23456 AdminUser@192.168.68.110
```

### ステップ2: プロジェクトディレクトリに移動

```bash
cd ~/nas-project/nas-dashboard-monitoring
```

### ステップ3: 最新のコードを取得（オプション）

```bash
# 最新の変更を取得
git pull origin main
```

### ステップ4: バックエンドコンテナを再起動

**方法1: docker composeコマンドを使用（推奨）**

```bash
# バックエンドコンテナのみを再起動
docker compose restart backend
```

**方法2: dockerコマンドを直接使用**

```bash
# バックエンドコンテナ名を確認
docker ps | grep nas-dashboard-monitoring

# バックエンドコンテナを再起動
docker restart nas-dashboard-monitoring-backend-1
```

**方法3: すべてのサービスを再起動**

```bash
# すべてのサービスを再起動
docker compose restart
```

---

## ✅ 動作確認

### 1. コンテナの状態を確認

```bash
# コンテナが正常に起動しているか確認
docker compose ps

# または
docker ps | grep nas-dashboard-monitoring
```

### 2. ログを確認

```bash
# バックエンドのログを確認（Nginx監視の開始メッセージを確認）
docker compose logs backend --tail 50 | grep nginx

# または
docker logs nas-dashboard-monitoring-backend-1 --tail 50 | grep nginx
```

**期待される出力**:
```
🔍 Nginxアクセスログ監視を開始しました
```

### 3. APIエンドポイントで監視状況を確認

```bash
# 監視状況を取得
curl http://localhost:8002/api/v1/security/nginx-monitoring/status

# または、外部からアクセス
curl http://192.168.68.110:8002/api/v1/security/nginx-monitoring/status
```

**期待されるレスポンス**:
```json
{
  "status": "active",
  "monitored_logs": [
    "/data/logs/proxy-host-6_access.log"
  ],
  "thresholds": {
    "error_404_per_minute": 20,
    "error_401_per_minute": 10,
    "error_403_per_minute": 10,
    "requests_per_ip_per_minute": 100,
    "requests_per_ip_per_hour": 1000
  },
  "total_ips_monitored": 0,
  "last_check_time": null
}
```

---

## 🔧 トラブルシューティング

### 問題1: `docker-compose: command not found`

**原因**: NAS環境では`docker compose`（スペース区切り）を使用する必要があります。

**解決方法**:
```bash
# docker compose（スペース区切り）を使用
docker compose restart backend
```

### 問題2: `cd: nas-dashboard-monitoring: No such file or directory`

**原因**: プロジェクトのパスが異なります。

**解決方法**:
```bash
# 正しいパスに移動
cd ~/nas-project/nas-dashboard-monitoring

# または、絶対パスを使用
cd /home/AdminUser/nas-project/nas-dashboard-monitoring
```

### 問題3: コンテナが起動しない

**確認事項**:
1. **Dockerが起動しているか確認**
   ```bash
   docker ps
   ```

2. **ログを確認**
   ```bash
   docker compose logs backend --tail 100
   ```

3. **コンテナを再ビルド**
   ```bash
   docker compose up -d --build backend
   ```

### 問題4: Nginx監視が開始されない

**確認事項**:
1. **ログを確認**
   ```bash
   docker compose logs backend --tail 100 | grep -i nginx
   ```

2. **Nginx Proxy Managerコンテナ名を確認**
   ```bash
   docker ps | grep nginx-proxy-manager
   ```
   
   コンテナ名が異なる場合は、`nginx_log_monitor.py`の`docker exec`コマンドを修正してください。

3. **Nginxログファイルのパスを確認**
   ```bash
   docker exec nginx-proxy-manager ls -lh /data/logs/
   ```

---

## 📚 関連ドキュメント

- [NGINX_ACCESS_LOG_MONITORING.md](NGINX_ACCESS_LOG_MONITORING.md) - Nginxアクセスログ監視の設定方法
- [SERVICE_STATUS_CHECK_GUIDE.md](SERVICE_STATUS_CHECK_GUIDE.md) - サービス状態の確認方法

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

