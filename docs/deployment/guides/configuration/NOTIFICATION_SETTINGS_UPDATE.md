# 📧 通知設定の更新ガイド

**作成日**: 2025-01-27  
**対象**: nas-dashboard-monitoringの通知設定

---

## 📋 概要

`nas-dashboard-monitoring`のメール通知とSlack通知の設定を、他のプロジェクト（`nas-dashboard`）から取得して設定しました。

---

## ✅ 更新内容

### メール設定

以下の設定を`nas-dashboard`プロジェクトから取得して設定しました：

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=mipatago.netsetting@gmail.com
SMTP_PASSWORD=bpio kqxc pvqv sgyd
EMAIL_FROM=mipatago.netsetting@gmail.com
EMAIL_TO=nas.system.0828@gmail.com
```

### Slack設定

Slack設定は他のプロジェクトから見つかりませんでした。Slack通知が必要な場合は、以下を設定してください：

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## 🔧 設定方法

### 手動で設定する場合

1. **NAS環境にSSH接続**
   ```bash
   ssh -p 23456 AdminUser@192.168.68.110
   ```

2. **プロジェクトディレクトリに移動**
   ```bash
   cd ~/nas-project/nas-dashboard-monitoring
   ```

3. **.envファイルを編集**
   ```bash
   nano .env
   ```

4. **メール設定を更新**
   ```bash
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=mipatago.netsetting@gmail.com
   SMTP_PASSWORD=bpio kqxc pvqv sgyd
   EMAIL_FROM=mipatago.netsetting@gmail.com
   EMAIL_TO=nas.system.0828@gmail.com
   ```

5. **Slack設定を追加（オプション）**
   ```bash
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

6. **サービスを再起動**
   ```bash
   docker compose restart backend
   ```

---

## ✅ 動作確認

### 1. ログを確認

```bash
# メール通知のエラーがないか確認
docker compose logs backend --tail 50 | grep -i 'email\|notification'

# 期待される出力（エラーがない場合）:
# 通知送信結果: {'email': True, 'slack': False}
```

### 2. テスト通知を送信

異常検知が発生した場合、自動的にメール通知が送信されます。

---

## 🔧 トラブルシューティング

### 問題1: メール認証エラー

**症状**: `BadCredentials`エラーが発生する

**原因**: Gmailのアプリパスワードが正しくない、または期限切れ

**解決方法**:
1. Gmailのアプリパスワードを再生成
2. `.env`ファイルの`SMTP_PASSWORD`を更新
3. サービスを再起動

### 問題2: Slack通知エラー

**症状**: `404 - no_team`エラーが発生する

**原因**: Slack Webhook URLが正しくない、または期限切れ

**解決方法**:
1. SlackのIncoming Webhookを再作成
2. `.env`ファイルの`SLACK_WEBHOOK_URL`を更新
3. サービスを再起動

---

## 📚 関連ドキュメント

- [NGINX_ACCESS_LOG_MONITORING.md](NGINX_ACCESS_LOG_MONITORING.md) - Nginxアクセスログ監視の設定方法

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

