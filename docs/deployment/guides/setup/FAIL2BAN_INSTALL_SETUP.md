# 🔒 Fail2banインストールと設定ガイド

**作成日**: 2025-11-02  
**対象**: UGreen NAS環境

---

## 📋 現在の状態

- ❌ Fail2ban: 未インストール
- ⚠️ インストールと設定が必要

---

## 🚀 インストール手順

### ステップ1: Fail2banのインストール

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# システムパッケージの更新
sudo apt update

# Fail2banのインストール
sudo apt install fail2ban -y

# インストールの確認
sudo systemctl status fail2ban
```

---

### ステップ2: Fail2ban設定ファイルの作成

```bash
# デフォルト設定ファイルをコピーしてカスタマイズ
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# 設定ファイルを編集
sudo nano /etc/fail2ban/jail.local
```

---

### ステップ3: SSH jail設定（ポート23456対応）

SSHポート（23456）を監視するように設定します。

**設定ファイル（`/etc/fail2ban/jail.local`）の編集**:

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
findtime = 3600       # SSH: 1時間以内の失敗をカウント
```

**重要なポイント**:
- `port = 23456`: カスタムSSHポートを指定
- `maxretry = 3`: 3回の失敗でBAN
- `bantime = 86400`: 24時間（86400秒）BAN

---

### ステップ4: Nginx Proxy Manager用jail設定（オプション）

Nginx Proxy Managerのログを監視する設定を追加します。

**設定ファイルに以下を追加**:

```ini
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

**注意**: Nginx Proxy Managerのログパスが異なる場合、`logpath`を調整してください。

---

### ステップ5: 設定の適用

```bash
# 設定ファイルの構文チェック
sudo fail2ban-client -t

# エラーがない場合、Fail2banを再起動
sudo systemctl restart fail2ban

# 状態を確認
sudo systemctl status fail2ban
sudo fail2ban-client status
```

---

## 🔍 動作確認

### ステップ1: Fail2banの状態確認

```bash
# Fail2banの基本状態を確認
sudo fail2ban-client status

# 有効なjailの一覧を確認
sudo fail2ban-client status | grep "Jail list"
```

### ステップ2: SSH jailの状態確認

```bash
# SSH jailの状態を確認
sudo fail2ban-client status sshd

# 期待される出力:
# Status for the jail: sshd
# |- Filter
# |  |- Currently failed: 0
# |  |- Total failed:     0
# |  `- File list:        /var/log/auth.log
# `- Actions
#    |- Currently banned: 0
#    |- Total banned:     0
#    `- Banned IP list:
```

---

## 🧪 テスト方法（オプション）

### 不正アクセス試行のテスト

**注意**: これはテスト目的のみで使用してください。

```bash
# 別のPCから、わざと間違ったパスワードでSSH接続を試行
# 3回失敗すると、IPアドレスがBANされる

# BANされたIPアドレスの確認
sudo fail2ban-client status sshd | grep "Banned IP list"

# BANを解除（テスト用）
sudo fail2ban-client set sshd unbanip [IPアドレス]
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

# Fail2banが稼働しているか確認
if ! systemctl is-active --quiet fail2ban; then
    echo "[$DATE] 警告: Fail2banが稼働していません" >> "$LOG_FILE"
    exit 1
fi

# SSH jailのBAN数を確認
SSH_BANNED=$(sudo fail2ban-client status sshd 2>/dev/null | grep "Currently banned" | awk '{print $NF}' || echo "0")
echo "[$DATE] SSH jail BAN数: $SSH_BANNED" >> "$LOG_FILE"

# 異常なBAN数がある場合の通知（オプション）
if [ "$SSH_BANNED" -gt 10 ]; then
    echo "[$DATE] 警告: 異常なBAN数が検出されました (BAN数: $SSH_BANNED)" >> "$LOG_FILE"
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

## 🔍 トラブルシューティング

### インストールが失敗する場合

```bash
# パッケージリストの更新
sudo apt update

# 依存関係の問題を確認
sudo apt install -f

# 再度インストール
sudo apt install fail2ban -y
```

### Fail2banが起動しない場合

```bash
# ログを確認
sudo tail -50 /var/log/fail2ban.log

# 設定ファイルの構文チェック
sudo fail2ban-client -t

# Fail2banの再起動
sudo systemctl restart fail2ban
```

### SSH jailが動作しない場合

```bash
# SSHログファイルのパスを確認
sudo ls -la /var/log/auth.log

# ログファイルの権限を確認
sudo chmod 644 /var/log/auth.log

# Fail2banの設定でログパスが正しいか確認
sudo cat /etc/fail2ban/jail.local | grep -A 5 "\[sshd\]"
```

---

## ✅ インストール後のチェックリスト

- [ ] Fail2banがインストール済み
- [ ] Fail2banが稼働中
- [ ] SSH jailが有効で正しいポート（23456）を監視
- [ ] 設定ファイルの構文チェックが成功
- [ ] BAN数が正常範囲内であることを確認
- [ ] 定期チェックスクリプトが設定済み（オプション）

---

## 📚 参考資料

- [Fail2ban公式ドキュメント](https://www.fail2ban.org/)
- [Fail2ban設定ガイド](FAIL2BAN_CONFIGURATION_CHECK.md)
- [セキュリティ対策ガイド](EXTERNAL_ACCESS_SECURITY.md)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

