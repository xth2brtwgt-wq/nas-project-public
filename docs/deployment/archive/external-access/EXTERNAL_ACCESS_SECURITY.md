# 🔒 外部アクセス時のセキュリティ対策ガイド

**作成日**: 2025-11-02  
**対象**: HTTPSで外部アクセス可能なNAS環境

---

## 📋 概要

HTTPSで外部アクセスが可能になった場合に実施すべきセキュリティ対策をまとめています。

---

## ✅ 既に完了している対策

- ✅ **HTTPS設定**: Let's Encrypt証明書を使用したSSL/TLS暗号化
- ✅ **証明書自動更新**: acme.sh + cronジョブによる自動更新

---

## 🔐 優先度の高い対策（必須）

### 1. ファイアウォール設定（UFW）

外部からアクセス可能なポートのみを開放し、不要なポートは閉鎖します。

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# UFWの状態を確認
sudo ufw status

# 必要なポートのみ開放（既に開いている場合も再確認）
# HTTPS（Nginx Proxy Manager）
sudo ufw allow 8443/tcp comment 'Nginx Proxy Manager HTTPS'

# SSH（管理用）
sudo ufw allow 23456/tcp comment 'SSH Management'

# Let's Encrypt証明書更新用（一時的に必要）
# sudo ufw allow 80/tcp comment 'Let's Encrypt HTTP Challenge'
# 注意: 証明書更新時のみ一時的に開放、その後閉鎖推奨

# 他のサービスは内部からのみアクセス可能（ファイアウォールでブロック）
# 外部からの直接アクセスを許可しない:
# - 9001 (nas-dashboard)
# - 8001 (amazon-analytics)
# - 8080 (document-automation)
# - 5002 (meeting-minutes-byc)
# - 3002 (nas-dashboard-monitoring-frontend)
# - 8002 (nas-dashboard-monitoring-backend)
# - 8111 (youtube-to-notion)

# ファイアウォールを有効化
sudo ufw enable

# 設定の確認
sudo ufw status verbose
```

**推奨設定**:
- 外部からはHTTPS（8443）のみ許可
- その他のサービスはNginx Proxy Manager経由でアクセス
- SSHポートは外部からアクセスできないように設定（VPN経由など）

---

### 2. Fail2banの設定

不正アクセス試行を自動検出してIPをブロックします。

```bash
# Fail2banがインストールされているか確認
sudo systemctl status fail2ban

# インストールされていない場合
sudo apt update
sudo apt install fail2ban -y

# Fail2ban設定ファイルを作成
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

**推奨設定** (`/etc/fail2ban/jail.local`):

```ini
[DEFAULT]
# デフォルト設定
bantime = 3600        # BAN時間: 1時間
findtime = 600         # 検出期間: 10分
maxretry = 5           # 最大試行回数: 5回
backend = auto
destemail = root@localhost
sender = root@localhost
action = %(action_)s

[sshd]
enabled = true
port = 23456           # SSHポート番号
filter = sshd
logpath = /var/log/auth.log
maxretry = 3           # SSH: 3回でBAN
bantime = 86400        # SSH: 24時間BAN

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

**Fail2banの起動と確認**:

```bash
# Fail2banを有効化
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 状態を確認
sudo fail2ban-client status

# 各jailの状態を確認
sudo fail2ban-client status sshd
sudo fail2ban-client status nginx-http-auth
```

---

### 3. Nginx Proxy Managerでのセキュリティヘッダー設定

Nginx Proxy ManagerのWeb UIでセキュリティヘッダーを設定します。

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブを開く**

3. **yoshi-nas-sys.duckdns.orgのProxy Hostを編集**

4. **「Advanced」タブを開く**

5. **Custom Nginx Configurationに以下を追加**:

```nginx
# セキュリティヘッダー
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: ws:;" always;

# レート制限（オプション）
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req zone=general burst=20 nodelay;

# IP制限（オプション - 特定のIPからのみアクセスを許可する場合）
# allow 123.45.67.89;  # 許可するIPアドレス
# deny all;
```

6. **「Save」をクリック**

---

### 4. Basic認証の設定（オプション）

Nginx Proxy ManagerでBasic認証を追加します。

1. **Nginx Proxy ManagerのWeb UIで「Proxy Hosts」を開く**

2. **yoshi-nas-sys.duckdns.orgのProxy Hostを編集**

3. **「Access Lists」タブを開く**

4. **「Add Access List」をクリック**

5. **認証情報を入力**:
   - **Name**: `nas-dashboard-auth`
   - **Username**: 任意のユーザー名
   - **Password**: 強力なパスワード

6. **Proxy Host設定で「Access List」を選択**

7. **「Save」をクリック**

---

## 🔍 優先度の高い対策（推奨）

### 5. アクセスログの監視

不正アクセスの兆候を早期に検出します。

```bash
# Nginx Proxy Managerのアクセスログを確認
# Dockerコンテナ内のログを確認
docker logs nginx-proxy-manager --tail 100

# または、マウントされたログファイルを確認（設定による）
sudo tail -100 /var/log/nginx/access.log

# エラーログの確認
sudo tail -100 /var/log/nginx/error.log

# 不正アクセスのパターンを確認
sudo grep -i "401\|403\|404" /var/log/nginx/access.log | tail -50

# 異常なアクセス試行を確認
sudo grep -E "(failed|unauthorized|forbidden)" /var/log/nginx/error.log
```

**定期チェックスクリプト**:

```bash
# スクリプトを作成
sudo nano /usr/local/bin/check-security-logs.sh
```

```bash
#!/bin/bash
# セキュリティログチェックスクリプト

LOG_FILE="$HOME/security-check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] セキュリティログチェック開始" >> "$LOG_FILE"

# 失敗したログイン試行をカウント
FAILED_LOGINS=$(grep -i "failed\|unauthorized" /var/log/auth.log 2>/dev/null | wc -l)
echo "[$DATE] 失敗したログイン試行: $FAILED_LOGINS 回" >> "$LOG_FILE"

# Fail2banのBAN数を確認
BANNED_IPS=$(sudo fail2ban-client status sshd 2>/dev/null | grep "Currently banned" | awk '{print $NF}')
echo "[$DATE] 現在BANされているIP数: $BANNED_IPS" >> "$LOG_FILE"

# 異常なアクセスパターンを確認
SUSPICIOUS_ACCESS=$(grep -iE "(401|403|404)" /var/log/nginx/access.log 2>/dev/null | tail -20)
if [ ! -z "$SUSPICIOUS_ACCESS" ]; then
    echo "[$DATE] 異常なアクセスパターンを検出:" >> "$LOG_FILE"
    echo "$SUSPICIOUS_ACCESS" >> "$LOG_FILE"
fi

echo "[$DATE] セキュリティログチェック完了" >> "$LOG_FILE"
```

```bash
# 実行権限を付与
sudo chmod +x /usr/local/bin/check-security-logs.sh

# cronジョブに追加（毎日午前9時に実行）
crontab -e
# 以下の行を追加:
0 9 * * * /usr/local/bin/check-security-logs.sh
```

---

### 6. セキュリティアップデートの定期実行

システムと依存関係のセキュリティパッチを適用します。

```bash
# セキュリティアップデートスクリプトを作成
sudo nano /usr/local/bin/security-update.sh
```

```bash
#!/bin/bash
# セキュリティアップデートスクリプト

LOG_FILE="$HOME/security-update.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] セキュリティアップデート開始" >> "$LOG_FILE"

# システムパッケージの更新
sudo apt update >> "$LOG_FILE" 2>&1
sudo apt upgrade -y >> "$LOG_FILE" 2>&1

# セキュリティパッチのみ適用（オプション）
# sudo unattended-upgrade -d

# Dockerコンテナの再ビルド（セキュリティ更新がある場合）
# cd /home/AdminUser/nas-project
# docker compose pull
# docker compose up -d

echo "[$DATE] セキュリティアップデート完了" >> "$LOG_FILE"
```

```bash
# 実行権限を付与
sudo chmod +x /usr/local/bin/security-update.sh

# cronジョブに追加（毎週日曜日の午前2時に実行）
crontab -e
# 以下の行を追加:
0 2 * * 0 /usr/local/bin/security-update.sh
```

---

### 7. 不要なポートの閉鎖

外部から不要なポートが開いていないか確認します。

```bash
# 外部から開いているポートを確認（ルーターの設定を確認）
# ルーターの管理画面でポート転送設定を確認

# 内部でリッスンしているポートを確認
sudo netstat -tulpn | grep LISTEN

# 外部からアクセス可能なポートのみをルーターで転送する
# 現在開いているポート:
# - 8443 (HTTPS - Nginx Proxy Manager) ✅ 必要
# - 80 (HTTP - Let's Encrypt証明書更新用) ⚠️ 一時的のみ
# - その他のポートは内部のみでアクセス可能にする
```

---

## 📊 優先度の中程度の対策（推奨）

### 8. アクセス制限（IP制限）

特定のIPアドレスからのみアクセスを許可します。

**Nginx Proxy Managerでの設定**:

1. **「Access Lists」タブで新しいアクセスリストを作成**

2. **「Whitelist IP addresses」を選択**

3. **許可するIPアドレスを追加**:
   ```
   123.45.67.89  # 例: 自宅の固定IP
   98.76.54.32   # 例: オフィスの固定IP
   ```

4. **Proxy Host設定で「Access List」を選択**

**注意**: 動的IPアドレスを使用している場合は、この設定は推奨しません。

---

### 9. 定期的なバックアップ

データの定期的なバックアップを設定します。

```bash
# バックアップスクリプトを作成
sudo nano /usr/local/bin/backup-data.sh
```

```bash
#!/bin/bash
# データバックアップスクリプト

BACKUP_DIR="/home/AdminUser/backups"
DATE=$(date '+%Y%m%d')
LOG_FILE="$HOME/backup.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] バックアップ開始" >> "$LOG_FILE"

# バックアップディレクトリを作成
mkdir -p "$BACKUP_DIR/$DATE"

# 重要なデータをバックアップ
# 例: 証明書ファイル
sudo cp -r /etc/letsencrypt "$BACKUP_DIR/$DATE/letsencrypt"

# 例: 環境変数ファイル
cp -r /home/AdminUser/nas-project-data "$BACKUP_DIR/$DATE/nas-project-data"

# 古いバックアップを削除（30日以上前）
find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} \;

echo "[$(date '+%Y-%m-%d %H:%M:%S')] バックアップ完了" >> "$LOG_FILE"
```

```bash
# 実行権限を付与
sudo chmod +x /usr/local/bin/backup-data.sh

# cronジョブに追加（毎日午前3時に実行）
crontab -e
# 以下の行を追加:
0 3 * * * /usr/local/bin/backup-data.sh
```

---

### 10. ログローテーションの設定

ログファイルが肥大化しないように設定します。

```bash
# logrotate設定を作成
sudo nano /etc/logrotate.d/nas-projects
```

```
/home/AdminUser/nas-project-data/*/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    create 0644 AdminUser admin
}

/var/log/nginx/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    create 0640 www-data adm
}
```

---

## 🔍 定期チェック項目

以下の項目を定期的にチェックしてください：

### 毎日

- [ ] アクセスログの異常パターンを確認
- [ ] Fail2banのBAN状況を確認

### 毎週

- [ ] セキュリティアップデートの確認
- [ ] バックアップの確認

### 毎月

- [ ] SSL証明書の有効期限を確認
- [ ] ファイアウォール設定の見直し
- [ ] 不要なポートの確認

---

## 📝 セキュリティチェックリスト

外部公開前の確認事項：

- [x] HTTPS証明書の設定（完了）
- [x] 証明書自動更新の設定（完了）
- [ ] ファイアウォール設定（UFW）
- [ ] Fail2banの設定
- [ ] セキュリティヘッダーの設定
- [ ] アクセスログの監視
- [ ] セキュリティアップデートの定期実行
- [ ] バックアップ設定
- [ ] ログローテーション設定
- [ ] 不要なポートの閉鎖確認

---

## 📚 参考資料

- [UFW ファイアウォール設定](https://help.ubuntu.com/community/UFW)
- [Fail2ban公式ドキュメント](https://www.fail2ban.org/)
- [Nginx Proxy Manager公式ドキュメント](https://nginxproxymanager.com/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

