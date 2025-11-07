# 🔒 Fail2ban SSHポート設定の更新手順（23456対応）

**作成日**: 2025-11-02  
**対象**: Dockerコンテナとして動作しているFail2ban（カスタムSSHポート23456対応）

---

## 📋 現在の状況

- ✅ Fail2banコンテナ: 稼働中・正常動作
- ✅ SSH jail: 有効・31個のIPがBAN中
- ⚠️ SSHポート設定: `port = ssh`（標準ポート22を監視）
- 🎯 **目的**: SSHポート（23456）を監視するように設定を更新

---

## 🛠️ 設定の更新手順

### 方法1: コンテナ内で設定ファイルを作成（推奨）

```bash
# 1. コンテナに接続して設定ファイルを作成
docker exec -it fail2ban sh

# 2. jail.dディレクトリにSSH設定ファイルを作成
cat > /data/jail.d/sshd.local << 'EOF'
[sshd]
enabled = true
port = 23456
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 604800
findtime = 3600
EOF

# 3. 設定ファイルの権限を設定
chmod 644 /data/jail.d/sshd.local

# 4. コンテナから出る
exit

# 5. Fail2banの設定を再読み込み
docker exec fail2ban fail2ban-client reload

# 6. 設定を確認
docker exec fail2ban fail2ban-client status sshd
```

---

### 方法2: メイン設定ファイルを編集（オプション）

```bash
# 1. コンテナ内の設定ファイルを編集
docker exec -it fail2ban sh

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

# 5. コンテナから出る
exit

# 6. Fail2banの設定を再読み込み
docker exec fail2ban fail2ban-client reload

# 7. 設定を確認
docker exec fail2ban fail2ban-client status sshd
```

---

## ✅ 設定後の確認

### ステップ1: Fail2banの再読み込み

```bash
# Fail2banの設定を再読み込み
docker exec fail2ban fail2ban-client reload

# 状態を確認
docker exec fail2ban fail2ban-client status
```

### ステップ2: SSH jailの設定確認

```bash
# SSH jailの状態を確認
docker exec fail2ban fail2ban-client status sshd

# 設定が正しく反映されているか確認
docker exec fail2ban cat /data/jail.d/sshd.local 2>/dev/null || docker exec fail2ban grep -A 5 "\[sshd\]" /etc/fail2ban/jail.local
```

---

## ⚠️ 重要な注意事項

### 設定変更時の注意

1. **既存のBANは維持される**
   - 設定変更後も、既存のBANされたIPは維持されます
   - 新しい設定で監視が開始されます

2. **動作確認**
   - 設定変更後、実際にSSHポート（23456）への攻撃が検出されるか確認
   - ログを確認して、正しく監視されているか確認

3. **ロールバック**
   - 問題が発生した場合、設定を元に戻すことができます

---

## 🔍 動作確認

### ステップ1: 設定の確認

```bash
# SSH jailの設定を確認
docker exec fail2ban fail2ban-client status sshd | grep -i port

# 期待される出力:
# port = 23456  （または設定に応じたポート番号）
```

### ステップ2: ログの確認

```bash
# Fail2banのログを確認
docker logs fail2ban --tail 50 | grep -i ssh

# SSHポート（23456）への攻撃が検出されているか確認
docker logs fail2ban --tail 100 | grep "23456"
```

---

## 📊 現在のセキュリティ状況

### 正常に動作している機能

- ✅ **Fail2banコンテナ**: 稼働中（Up 8 days (healthy)）
- ✅ **SSH jail**: 有効・動作中
- ✅ **現在31個のIPがBAN中**: 不正アクセス試行を検出してブロック
- ✅ **総BAN数: 189回**: これまでに多数の不正アクセスをブロック
- ✅ **不正アクセス試行: 257回検出**: 攻撃を正常に検出

---

## 💡 推奨事項

### 現在の状態について

Fail2banは正常に動作しており、多数の不正アクセス試行を検出してブロックしています。

**設定変更の必要性**:
- 現在標準SSHポート（22）を監視しているが、実際に使用しているのはカスタムポート（23456）
- カスタムポート（23456）への攻撃も監視するため、設定を更新することを推奨
- ただし、現在も正常に動作しているため、緊急ではありません

---

## 📝 チェックリスト

設定更新後の確認：

- [ ] Fail2banの設定を再読み込み済み
- [ ] SSH jailの設定で`port = 23456`が設定されている
- [ ] Fail2banが正常に動作している
- [ ] 既存のBANが維持されている
- [ ] ログでSSHポート（23456）が監視されていることを確認

---

## 🔄 ロールバック手順

問題が発生した場合：

```bash
# 作成した設定ファイルを削除
docker exec fail2ban rm /data/jail.d/sshd.local

# または、設定を元に戻す
docker exec fail2ban sed -i 's/port = 23456/port = ssh/' /etc/fail2ban/jail.local

# Fail2banを再読み込み
docker exec fail2ban fail2ban-client reload

# 状態を確認
docker exec fail2ban fail2ban-client status sshd
```

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

