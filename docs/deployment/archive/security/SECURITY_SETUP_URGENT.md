# 🚨 緊急セキュリティ対策設定

**作成日**: 2025-11-02  
**緊急度**: 高

---

## ⚠️ 現在の状態

### 発見された問題

1. **ファイアウォール（UFW）**: 多くのポートが外部からアクセス可能
   - 9001, 8001, 8080, 5002, 3002, 8002, 8111, 23456, 80, 443など
   - **リスク**: これらのポートは外部から直接アクセスできており、Nginx Proxy Manager経由でアクセスすべき

2. **Fail2ban**: インストールされていない
   - **リスク**: 不正アクセス試行に対する保護がない

---

## 🔧 緊急対応手順

### ステップ1: ファイアウォール設定の最適化

外部からアクセス可能なポートをHTTPS（8443）のみに制限します。

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# 現在のルールを確認
sudo ufw status numbered

# 外部からのアクセスを削除（内部ネットワークからのみアクセス可能にする）
# 注意: 実行前に必ずSSH接続（23456）が開いていることを確認してください！

# 1. SSH接続を確保（重要！）
sudo ufw allow 23456/tcp comment 'SSH Management'

# 2. 内部ネットワークからのアクセスを許可
sudo ufw allow from 192.168.68.0/24 comment 'Internal Network'

# 3. 外部からの直接アクセスを削除（HTTPS（8443）以外）
# まず、番号を確認してから削除
sudo ufw delete allow 9001/tcp
sudo ufw delete allow 8001/tcp
sudo ufw delete allow 8080/tcp
sudo ufw delete allow 5002/tcp
sudo ufw delete allow 3002/tcp
sudo ufw delete allow 8002/tcp
sudo ufw delete allow 8111/tcp
sudo ufw delete allow 80/tcp
sudo ufw delete allow 443/tcp
sudo ufw delete allow 9443/tcp
sudo ufw delete allow 10443/tcp

# IPv6も同様に削除
sudo ufw delete allow 9001/tcp
sudo ufw delete allow 8001/tcp
sudo ufw delete allow 8080/tcp
sudo ufw delete allow 5002/tcp
sudo ufw delete allow 3002/tcp
sudo ufw delete allow 8002/tcp
sudo ufw delete allow 8111/tcp
sudo ufw delete allow 80/tcp
sudo ufw delete allow 443/tcp
sudo ufw delete allow 9443/tcp
sudo ufw delete allow 10443/tcp

# 4. 外部からのHTTPSアクセスのみ許可
sudo ufw allow 8443/tcp comment 'HTTPS - Nginx Proxy Manager'

# 5. 設定を確認
sudo ufw status verbose
```

**期待される設定**:
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
Anywhere                   ALLOW       192.168.68.0/24
23456/tcp                  ALLOW       Anywhere          # SSH Management
8443/tcp                   ALLOW       Anywhere          # HTTPS - Nginx Proxy Manager
8181                       ALLOW       192.168.68.0/24   # Nginx Proxy Manager Admin
8081/tcp                   ALLOW       Anywhere          # Nginx Proxy Manager HTTP
```

**注意**: 
- SSHポート（23456）は必ず開けておく
- 内部ネットワーク（192.168.68.0/24）からのアクセスは許可
- 外部からはHTTPS（8443）のみ許可

---

### ステップ2: Fail2banのインストールと設定

```bash
# Fail2banのインストール
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

## ⚠️ 重要な注意事項

### ファイアウォール設定の変更時

1. **SSH接続を維持する**
   - SSHポート（23456）は必ず開けておく
   - 設定変更中は別のSSHセッションを開いておく（推奨）

2. **段階的に削除する**
   - 一度にすべて削除せず、1つずつ確認しながら削除

3. **設定の確認**
   - 変更後、必ず`sudo ufw status`で確認

---

## ✅ 設定後の確認

### 1. ファイアウォール設定の確認

```bash
# UFWの状態を確認
sudo ufw status verbose

# 外部からアクセス可能なポートが8443のみであることを確認
```

### 2. Fail2banの動作確認

```bash
# Fail2banの状態を確認
sudo fail2ban-client status

# SSH jailの状態を確認
sudo fail2ban-client status sshd

# Nginx Proxy Managerのログを確認（Fail2banが監視対象）
sudo tail -50 /var/log/nginx/error.log
```

### 3. アクセステスト

```bash
# 内部からアクセステスト（全てアクセス可能であることを確認）
curl http://192.168.68.110:9001

# 外部からアクセステスト（HTTPSのみアクセス可能であることを確認）
curl -I https://yoshi-nas-sys.duckdns.org:8443
```

---

## 📝 設定後の期待される状態

### ファイアウォール（UFW）

- ✅ 外部からHTTPS（8443）のみアクセス可能
- ✅ SSH（23456）は外部からアクセス可能（管理用）
- ✅ 内部ネットワーク（192.168.68.0/24）からは全てアクセス可能
- ✅ その他のポートは外部からアクセス不可

### Fail2ban

- ✅ SSH（23456）に対する不正アクセス試行を監視
- ✅ Nginx Proxy Managerに対する不正アクセス試行を監視
- ✅ 3回の失敗で1時間BAN
- ✅ SSHの不正アクセスは24時間BAN

---

## 🔍 トラブルシューティング

### ファイアウォール設定後にアクセスできなくなった場合

```bash
# 緊急時の対応（内部ネットワークから実行）
# UFWを一時的に無効化（注意: セキュリティリスクあり）
sudo ufw disable

# または、特定のポートを一時的に許可
sudo ufw allow 8443/tcp
```

### Fail2banが動作しない場合

```bash
# Fail2banのログを確認
sudo tail -50 /var/log/fail2ban.log

# Fail2banの再起動
sudo systemctl restart fail2ban

# 設定ファイルの構文チェック
sudo fail2ban-client -t
```

---

## 📚 参考資料

- [UFW ファイアウォール設定](https://help.ubuntu.com/community/UFW)
- [Fail2ban公式ドキュメント](https://www.fail2ban.org/)
- [セキュリティ対策ガイド](EXTERNAL_ACCESS_SECURITY.md)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

