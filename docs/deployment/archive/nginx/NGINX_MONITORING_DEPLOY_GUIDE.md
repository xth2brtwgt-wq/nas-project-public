# 🚀 Nginxアクセスログ監視機能のデプロイガイド

**作成日**: 2025-01-27  
**対象**: NAS環境でのNginxアクセスログ監視機能のデプロイ

---

## 📋 概要

Nginxアクセスログ監視機能をNAS環境にデプロイする手順です。

---

## 🚀 デプロイ手順

### ステップ1: NAS環境にSSH接続

```bash
ssh -p 23456 AdminUser@192.168.68.110
```

### ステップ2: プロジェクトディレクトリに移動

```bash
cd ~/nas-project/nas-dashboard-monitoring
```

### ステップ3: 最新のコードを取得

```bash
# 最新の変更を取得
git pull origin main

# または、特定のブランチから取得
git fetch origin
git checkout main
git pull origin main
```

### ステップ4: コンテナを再ビルド

```bash
# バックエンドコンテナを再ビルド
docker compose up -d --build backend
```

### ステップ5: ログを確認

```bash
# バックエンドのログを確認（Nginx監視の開始メッセージを確認）
docker compose logs backend --tail 100 | grep -i nginx

# または、すべてのログを確認
docker compose logs backend --tail 100
```

**期待される出力**:
```
🔍 Nginxアクセスログ監視を開始しました
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

### 2. APIエンドポイントで監視状況を確認

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

### 3. ログで監視開始を確認

```bash
# ログでNginx監視の開始メッセージを確認
docker compose logs backend --tail 200 | grep "Nginxアクセスログ監視"
```

---

## 🔧 トラブルシューティング

### 問題1: Nginx監視の開始メッセージが表示されない

**原因**: 最新のコードがデプロイされていない可能性があります。

**解決方法**:
1. **最新のコードを取得**
   ```bash
   git pull origin main
   ```

2. **コンテナを再ビルド**
   ```bash
   docker compose up -d --build backend
   ```

3. **ログを確認**
   ```bash
   docker compose logs backend --tail 100
   ```

### 問題2: インポートエラーが発生する

**原因**: `nginx_log_monitor`モジュールが正しくインポートされていない可能性があります。

**解決方法**:
1. **ファイルの存在を確認**
   ```bash
   ls -la app/services/nginx_log_monitor.py
   ```

2. **コンテナ内でファイルを確認**
   ```bash
   docker compose exec backend ls -la /app/app/services/nginx_log_monitor.py
   ```

3. **コンテナを再ビルド**
   ```bash
   docker compose up -d --build backend
   ```

### 問題3: Nginx Proxy Managerコンテナにアクセスできない

**原因**: Dockerコンテナ名が異なる可能性があります。

**解決方法**:
1. **Nginx Proxy Managerコンテナ名を確認**
   ```bash
   docker ps | grep nginx-proxy-manager
   ```

2. **コンテナ名を確認したら、`nginx_log_monitor.py`を修正**
   ```python
   # ファイル: nas-dashboard-monitoring/app/services/nginx_log_monitor.py
   # 行: 約150行目付近
   result = subprocess.run(
       ['docker', 'exec', 'nginx-proxy-manager', 'tail', '-1000', log_path],
       # ↑ コンテナ名を実際の名前に変更
   )
   ```

### 問題4: ログファイルが見つからない

**原因**: Nginxログファイルのパスが異なる可能性があります。

**解決方法**:
1. **Nginx Proxy Managerコンテナ内のログファイルを確認**
   ```bash
   docker exec nginx-proxy-manager ls -lh /data/logs/
   ```

2. **ログファイルのパスを確認したら、`nginx_log_monitor.py`を修正**
   ```python
   # ファイル: nas-dashboard-monitoring/app/services/nginx_log_monitor.py
   # 行: 約20行目付近
   self.nginx_log_paths = [
       "/data/logs/proxy-host-6_access.log",  # 実際のパスに変更
   ]
   ```

---

## 📚 関連ドキュメント

- [NGINX_ACCESS_LOG_MONITORING.md](NGINX_ACCESS_LOG_MONITORING.md) - Nginxアクセスログ監視の設定方法
- [NGINX_MONITORING_RESTART_GUIDE.md](NGINX_MONITORING_RESTART_GUIDE.md) - サービスの再起動方法

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

