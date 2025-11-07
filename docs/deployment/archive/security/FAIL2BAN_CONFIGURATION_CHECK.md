# 🔒 Fail2ban設定確認と最適化ガイド

**作成日**: 2025-11-02  
**対象**: デフォルトでインストール済みのFail2ban

---

## 📋 現在の状態

- ✅ Fail2ban: インストール済み・稼働中
- ⚠️ 設定確認が必要

---

## 🔍 Fail2ban設定の確認手順

### ステップ1: Fail2banの状態確認

NAS上で以下を実行してください：

```bash
# Fail2banの状態を確認
sudo systemctl status fail2ban

# Fail2banの基本情報を確認
sudo fail2ban-client status

# 有効なjailの一覧を確認
sudo fail2ban-client status | grep "Jail list"
```

---

### ステップ2: 各jailの設定を確認

```bash
# SSH jailの状態を確認（ポート23456を使用している場合）
sudo fail2ban-client status sshd

# Nginx Proxy Manager用のjailを確認
sudo fail2ban-client status nginx-http-auth
sudo fail2ban-client status nginx-limit-req
```

---

### ステップ3: 設定ファイルの確認

```bash
# メイン設定ファイルを確認
sudo cat /etc/fail2ban/jail.local 2>/dev/null || echo "jail.localが存在しません"

# デフォルト設定ファイルを確認
sudo cat /etc/fail2ban/jail.conf | head -50
```

---

## 🛠️ 推奨設定（SSHポート23456対応）

デフォルトのFail2banは標準SSHポート（22）を監視している可能性があります。  
カスタムSSHポート（23456）を使用している場合、設定を調整する必要があります。

### 設定ファイルの編集

```bash
# 設定ファイルを作成または編集
sudo nano /etc/fail2ban/jail.local
```

**推奨設定**:

```ini
[DEFAULT]
# デフォルト設定
bantime = 3600        # BAN時間: 1時間
findtime = 600        # 検出期間: 10分
maxretry = 5          # 最大試行回数: 5回
backend = auto
destemail = root@localhost
sender = root@localhost
action = %(action_)s

[sshd]
enabled = true
port = 23456          # SSHポート番号（カスタムポート）
filter = sshd
logpath = /var/log/auth.log
maxretry = 3          # SSH: 3回でBAN
bantime = 86400       # SSH: 24時間BAN
findtime = 3600       # SSH: 1時間以内

[nginx-http-auth]
enabled = true
port = http,https
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600

[nginx-limit-req]
enabled = true
port = http,https
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
bantime = 3600
```

---

### 設定の適用

```bash
# 設定ファイルの構文チェック
sudo fail2ban-client -t

# Fail2banを再起動して設定を反映
sudo systemctl restart fail2ban

# 状態を確認
sudo fail2ban-client status
```

---

## 🔍 BAN履歴の確認

```bash
# BANされているIPアドレスの確認
sudo fail2ban-client status sshd | grep "Banned IP list"

# 詳細なBAN履歴を確認（ログファイル）
sudo grep -i "ban\|unban" /var/log/fail2ban.log | tail -50

# BAN数を確認
sudo fail2ban-client status sshd | grep "Currently banned"
```

---

## 🔄 Nginx Proxy Managerのログ監視設定

Nginx Proxy Managerのログパスを確認して、Fail2banが監視できるようにします。

```bash
# Nginx Proxy Managerのログファイルの場所を確認
docker logs nginx-proxy-manager --tail 10

# または、マウントされたログファイルを確認
ls -la /var/log/nginx/
```

**ログパスが異なる場合**:

```bash
# Nginx Proxy Managerのコンテナ内のログパスを確認
docker exec nginx-proxy-manager ls -la /data/logs/

# Fail2banの設定でログパスを指定
# /etc/fail2ban/jail.local でログパスを調整
```

---

## 📊 監視とアラート設定（オプション）

### 定期チェックスクリプト

```bash
# スクリプトを作成
sudo nano /usr/local/bin/check-fail2ban.sh
```

```bash
#!/bin/bash
# Fail2ban状態チェックスクリプト

LOG_FILE="$HOME/fail2ban-check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Fail2ban状態チェック開始" >> "$LOG_FILE"

# SSH jailのBAN数を確認
SSH_BANNED=$(sudo fail2ban-client status sshd 2>/dev/null | grep "Currently banned" | awk '{print $NF}' || echo "0")
echo "[$DATE] SSH jail BAN数: $SSH_BANNED" >> "$LOG_FILE"

# Nginx jailのBAN数を確認
NGINX_BANNED=$(sudo fail2ban-client status nginx-http-auth 2>/dev/null | grep "Currently banned" | awk '{print $NF}' || echo "0")
echo "[$DATE] Nginx jail BAN数: $NGINX_BANNED" >> "$LOG_FILE"

# 異常なBAN数がある場合の通知（オプション）
if [ "$SSH_BANNED" -gt 10 ] || [ "$NGINX_BANNED" -gt 10 ]; then
    echo "[$DATE] 警告: 異常なBAN数が検出されました" >> "$LOG_FILE"
    # ここにメール通知やSlack通知などを追加
fi

echo "[$DATE] Fail2ban状態チェック完了" >> "$LOG_FILE"
```

```bash
# 実行権限を付与
sudo chmod +x /usr/local/bin/check-fail2ban.sh

# cronジョブに追加（毎日午前9時に実行）
crontab -e
# 以下の行を追加:
0 9 * * * /usr/local/bin/check-fail2ban.sh
```

---

## ✅ 設定確認チェックリスト

- [ ] Fail2banが稼働していることを確認
- [ ] SSH jailが有効で正しいポート（23456）を監視している
- [ ] Nginx Proxy Manager用のjailが有効（可能な場合）
- [ ] BAN数が正常範囲内であることを確認
- [ ] ログファイルのパスが正しいことを確認
- [ ] 定期チェックスクリプトが設定済み（オプション）

---

## 🔍 トラブルシューティング

### Fail2banが動作していない場合

```bash
# Fail2banのログを確認
sudo tail -50 /var/log/fail2ban.log

# Fail2banの再起動
sudo systemctl restart fail2ban

# 設定ファイルの構文チェック
sudo fail2ban-client -t
```

### ログファイルが見つからない場合

```bash
# ログファイルの場所を確認
sudo find /var/log -name "*.log" | grep -E "(auth|nginx)"

# Nginx Proxy Managerのログパスを確認
docker exec nginx-proxy-manager ls -la /data/logs/
```

---

## 📚 参考資料

- [Fail2ban公式ドキュメント](https://www.fail2ban.org/)
- [セキュリティ対策ガイド](EXTERNAL_ACCESS_SECURITY.md)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

