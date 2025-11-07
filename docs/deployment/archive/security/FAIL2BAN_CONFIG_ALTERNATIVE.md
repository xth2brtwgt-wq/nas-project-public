# 🔒 Fail2ban設定ファイルの作成方法（読み取り専用ボリューム対応）

**作成日**: 2025-11-02  
**問題**: `/data`ディレクトリが読み取り専用で設定ファイルが作成できない

---

## 📋 現在の問題

- ❌ `/data/jail.d/sshd.local`が作成できない
- エラー: `Read-only file system`
- 原因: `/data`ディレクトリが読み取り専用ボリュームとしてマウントされている

---

## 🛠️ 解決方法

### 方法1: /etc/fail2ban/jail.d/ に設定ファイルを作成

Fail2banは`/etc/fail2ban/jail.d/`ディレクトリの設定ファイルも読み込みます。

```bash
# コンテナ内で実行（現在 / # プロンプトにいる場合）

# 1. /etc/fail2ban/jail.d/ ディレクトリに設定ファイルを作成
cat > /etc/fail2ban/jail.d/sshd.local << 'EOF'
[sshd]
enabled = true
port = 23456
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 604800
findtime = 3600
EOF

# 2. 設定ファイルの権限を設定
chmod 644 /etc/fail2ban/jail.d/sshd.local

# 3. 作成した設定ファイルを確認
cat /etc/fail2ban/jail.d/sshd.local

# 4. Fail2banの設定を再読み込み
fail2ban-client reload

# 5. 設定を確認
fail2ban-client status sshd
```

---

### 方法2: /etc/fail2ban/jail.local を直接編集

メイン設定ファイルを直接編集します。

```bash
# コンテナ内で実行

# 1. 設定ファイルを確認
cat /etc/fail2ban/jail.local | grep -A 10 "\[sshd\]"

# 2. 設定ファイルを編集
vi /etc/fail2ban/jail.local
# または
nano /etc/fail2ban/jail.local

# 3. [sshd]セクションの`port = ssh`を`port = 23456`に変更
# [sshd]
# enabled = true
# port = 23456  # 変更
# filter = sshd
# logpath = /var/log/auth.log
# maxretry = 3
# bantime = 604800

# 4. 保存して終了

# 5. Fail2banの設定を再読み込み
fail2ban-client reload

# 6. 設定を確認
fail2ban-client status sshd
```

---

### 方法3: ホスト側から設定ファイルを配置

コンテナのボリュームマウント経由で設定ファイルを配置する場合。

```bash
# コンテナから出る
exit

# ホスト側で実行
# 1. コンテナのボリュームマウントを確認
docker inspect fail2ban | grep -A 20 "Mounts"

# 2. ホスト側のマウントポイントを確認
# 例: /path/to/fail2ban/data/jail.d/

# 3. ホスト側で設定ファイルを作成
# sudo nano /path/to/fail2ban/data/jail.d/sshd.local

# 4. コンテナ内でFail2banを再読み込み
docker exec fail2ban fail2ban-client reload

# 5. 設定を確認
docker exec fail2ban fail2ban-client status sshd
```

---

## ✅ 推奨方法

**方法1（/etc/fail2ban/jail.d/ に設定ファイルを作成）**が最も簡単で確実です。

---

## 📝 設定後の確認

```bash
# コンテナ内で実行（まだコンテナ内にいる場合）

# 1. 設定ファイルの場所を確認
ls -la /etc/fail2ban/jail.d/

# 2. 設定ファイルの内容を確認
cat /etc/fail2ban/jail.d/sshd.local

# 3. Fail2banの設定を再読み込み
fail2ban-client reload

# 4. SSH jailの状態を確認
fail2ban-client status sshd

# 5. 設定が反映されているか確認
fail2ban-client status sshd | grep -i port

# 6. コンテナから出る
exit
```

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

