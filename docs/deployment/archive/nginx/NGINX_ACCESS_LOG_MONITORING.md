# 🔍 Nginxアクセスログ監視と異常検出ガイド

**作成日**: 2025-01-27  
**対象**: Nginx Proxy Managerのアクセスログを監視し、異常なアクセスパターンを検出する方法

---

## 📋 概要

Nginx Proxy Managerのアクセスログを自動的に監視し、異常なアクセスパターンを検出してアラートを送信する機能です。

---

## 🎯 監視対象

### 検出する異常パターン

1. **大量の404エラー**
   - 1分間に20回以上の404エラー（存在しないリソースへのアクセス）
   - スキャン攻撃やディレクトリトラバーサル攻撃の可能性

2. **大量の401エラー（認証失敗）**
   - 1分間に10回以上の401エラー
   - ブルートフォース攻撃の可能性

3. **大量の403エラー（アクセス拒否）**
   - 1分間に10回以上の403エラー
   - 不正なアクセス試行の可能性

4. **異常なリクエスト数**
   - 1分間に100回以上のリクエスト（同一IP）
   - 1時間に1000回以上のリクエスト（同一IP）
   - DoS攻撃やボット攻撃の可能性

5. **異常なパス（SQLインジェクション、XSS攻撃など）**
   - SQLインジェクション攻撃のパターン
   - XSS攻撃のパターン
   - ディレクトリトラバーサル攻撃のパターン
   - コマンドインジェクション攻撃のパターン

---

## ⚙️ 設定方法

### ステップ1: 監視サービスの確認

`nas-dashboard-monitoring`サービスが起動していることを確認します：

```bash
# サービスが起動しているか確認
docker ps | grep nas-dashboard-monitoring

# ログを確認
docker logs nas-dashboard-monitoring-backend-1 --tail 50
```

### ステップ2: 監視設定の確認

監視サービスは自動的に起動します。設定を変更する場合は、以下のファイルを編集します：

**ファイル**: `nas-dashboard-monitoring/app/services/nginx_log_monitor.py`

**設定可能な項目**:

```python
# 監視対象のログファイル（Dockerコンテナ内のパス）
self.nginx_log_paths = [
    "/data/logs/proxy-host-6_access.log",  # メインのProxy Host
]

# 異常検出の閾値
self.thresholds = {
    'error_404_per_minute': 20,  # 1分間に20回以上の404エラー
    'error_401_per_minute': 10,  # 1分間に10回以上の401エラー
    'error_403_per_minute': 10,  # 1分間に10回以上の403エラー
    'requests_per_ip_per_minute': 100,  # 1分間に100回以上のリクエスト（同一IP）
    'requests_per_ip_per_hour': 1000,  # 1時間に1000回以上のリクエスト（同一IP）
}

# アラート送信のクールダウン時間（分）
self.alert_cooldown_minutes = 30  # 30分間は同じIPからのアラートを送信しない
```

### ステップ3: 通知設定の確認

アラートは既存の通知サービス（メール・Slack）を通じて送信されます。

**通知設定ファイル**: `nas-dashboard-monitoring/.env`

```bash
# SMTP設定（メール通知用）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=alert-recipient@gmail.com

# Slack設定（Slack通知用）
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## 📊 監視状況の確認

### APIエンドポイント

監視状況を確認するには、以下のAPIエンドポイントを使用します：

```bash
# 監視状況を取得
curl http://192.168.68.110:8002/api/v1/security/nginx-monitoring/status

# レスポンス例
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
  "total_ips_monitored": 5,
  "last_check_time": "2025-01-27T12:00:00"
}
```

### ダッシュボードでの確認

`nas-dashboard-monitoring`のフロントエンドで、異常検知結果を確認できます：

1. **異常検知画面**
   - `/monitoring` → 「異常検知」タブ
   - 検出された異常の一覧を表示

2. **セキュリティレポート**
   - `/monitoring` → 「セキュリティ」タブ
   - セキュリティ状況のサマリーを表示

---

## 🔔 アラート通知

### 通知方法

1. **メール通知**
   - 異常検知時にメールを送信
   - 設定: `.env`ファイルのSMTP設定

2. **Slack通知**
   - 異常検知時にSlackにメッセージを送信
   - 設定: `.env`ファイルのSlack Webhook URL

3. **ダッシュボード通知**
   - リアルタイムでWebSocket経由で通知
   - フロントエンドで自動的に表示

### アラート内容

アラートには以下の情報が含まれます：

- **検知時刻**: 異常が検出された時刻
- **重要度**: CRITICAL、HIGH、MEDIUM、LOW
- **異常タイプ**: 検出された異常の種類
- **IPアドレス**: 異常なアクセスの送信元IP
- **詳細情報**: 検出された異常の詳細（回数、パスなど）

---

## 🔧 トラブルシューティング

### 監視が動作していない場合

1. **サービスが起動しているか確認**
   ```bash
   docker ps | grep nas-dashboard-monitoring
   ```

2. **ログを確認**
   ```bash
   docker logs nas-dashboard-monitoring-backend-1 --tail 100 | grep nginx
   ```

3. **Nginx Proxy Managerコンテナ名を確認**
   ```bash
   docker ps | grep nginx-proxy-manager
   ```
   
   コンテナ名が異なる場合は、`nginx_log_monitor.py`の`docker exec`コマンドを修正してください。

### アラートが送信されない場合

1. **通知設定を確認**
   - `.env`ファイルのSMTP/Slack設定が正しいか確認

2. **通知サービスのログを確認**
   ```bash
   docker logs nas-dashboard-monitoring-backend-1 --tail 100 | grep notification
   ```

3. **クールダウン時間を確認**
   - 同じIPからのアラートは30分間は送信されません
   - クールダウン時間を変更する場合は、`nginx_log_monitor.py`を編集

### 誤検知が多い場合

1. **閾値を調整**
   - `nginx_log_monitor.py`の`thresholds`を調整
   - 環境に応じて適切な値に設定

2. **ホワイトリストに追加**
   - 正常なアクセス元IPをホワイトリストに追加
   - `nginx_log_monitor.py`にホワイトリスト機能を追加

---

## 📚 関連ドキュメント

- [NGINX_ACCESS_LOG_ANALYSIS.md](NGINX_ACCESS_LOG_ANALYSIS.md) - Nginxアクセスログの分析方法
- [NGINX_ACCESS_LOG_CHECK.md](NGINX_ACCESS_LOG_CHECK.md) - Nginxアクセスログの確認方法
- [SECURITY_STATUS_VERIFICATION.md](SECURITY_STATUS_VERIFICATION.md) - セキュリティ設定の確認方法

---

## ✅ 完了

Nginxアクセスログ監視が有効になると、以下の機能が自動的に動作します：

1. **自動監視**: 1分ごとにNginxアクセスログをチェック
2. **異常検出**: 異常なアクセスパターンを自動検出
3. **アラート送信**: 異常検出時にメール・Slack・ダッシュボードに通知
4. **統計管理**: IPごとの統計を管理し、古いデータを自動削除

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

