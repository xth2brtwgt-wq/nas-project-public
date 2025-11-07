# 📁 ファイル転送方法ガイド

**作成日**: 2025-11-02  
**対象**: NASへのファイル転送（scpが使えない場合）

---

## 📋 問題

NASに`scp`や`sftp`が使えない場合、ファイルを転送する方法を説明します。

---

## 🔧 方法1: SSH設定でscp/sftpを有効化（推奨）

UGreen NASのSSH設定で、scp/sftpを有効化できる場合があります。

### 1-1. SSH設定の確認

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# SSH設定ファイルを確認
sudo cat /etc/ssh/sshd_config | grep -E "Subsystem|sftp"
```

### 1-2. SSH設定ファイルの編集（必要に応じて）

```bash
# SSH設定ファイルを編集
sudo nano /etc/ssh/sshd_config

# 以下の行がコメントアウトされている場合は、コメントを外す:
# Subsystem sftp /usr/lib/openssh/sftp-server

# または、パスが異なる場合は適切なパスに変更:
# Subsystem sftp /usr/libexec/openssh/sftp-server

# 設定を保存してエディタを終了
```

### 1-3. SSHサービスの再起動

```bash
# SSHサービスを再起動（接続が切れるので注意）
sudo systemctl restart sshd

# または
sudo service ssh restart
```

**注意**: SSHサービスを再起動すると、現在のSSH接続が切れます。別のターミナルから接続し直してください。

### 1-4. scp/sftpの動作確認

```bash
# ローカルから実行
# scpのテスト
scp -P 23456 /path/to/local/file AdminUser@192.168.68.110:/tmp/

# sftpのテスト
sftp -P 23456 AdminUser@192.168.68.110
```

---

## 📋 方法2: catでファイル内容を表示してコピペ（簡単）

scpが使えない場合、最も簡単な方法です。

### 2-1. ファイル内容を表示

```bash
# ローカルでファイル内容を表示
cat scripts/renew-cert-and-reload.sh
```

### 2-2. NAS上でファイルを作成

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# ファイルを作成
sudo nano /usr/local/bin/renew-cert-and-reload.sh

# 上記で表示した内容をコピー＆ペーストして保存
```

---

## 🌐 方法3: 一時的なHTTPサーバーを起動（中規模ファイル向け）

ローカルでHTTPサーバーを起動し、NAS上からダウンロードする方法です。

### 3-1. ローカルでHTTPサーバーを起動

```bash
# ローカルで実行（プロジェクトのルートディレクトリで）
cd /Users/Yoshi/nas-project

# Python 3のHTTPサーバーを起動（ポート8000）
python3 -m http.server 8000

# または
python -m SimpleHTTPServer 8000  # Python 2の場合
```

### 3-2. NAS上からダウンロード

```bash
# NASにSSH接続（別ターミナルで）
ssh -p 23456 AdminUser@192.168.68.110

# ローカルのIPアドレスを確認（ローカルのターミナルで）
# Macの場合:
ifconfig | grep "inet " | grep -v 127.0.0.1

# 例: 192.168.68.92 などのローカルIPアドレスを確認

# NAS上でダウンロード
curl http://192.168.68.92:8000/scripts/renew-cert-and-reload.sh -o /tmp/renew-cert-and-reload.sh

# または wget を使用
wget http://192.168.68.92:8000/scripts/renew-cert-and-reload.sh -O /tmp/renew-cert-and-reload.sh

# 実行権限を付与
sudo chmod +x /tmp/renew-cert-and-reload.sh
sudo mv /tmp/renew-cert-and-reload.sh /usr/local/bin/
```

### 3-3. HTTPサーバーを停止

```bash
# ローカルで HTTPサーバーを起動したターミナルで Ctrl+C を押して停止
```

---

## 📝 方法4: 直接NAS上でスクリプトを作成（小規模ファイル向け）

小さなファイルの場合は、直接NAS上で作成する方が簡単です。

### 4-1. NAS上でスクリプトを作成

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# スクリプトを作成
sudo nano /usr/local/bin/renew-cert-and-reload.sh
```

### 4-2. スクリプトの内容をコピー＆ペースト

ローカルの`scripts/renew-cert-and-reload.sh`の内容を、NAS上のエディタに貼り付けます。

---

## 🎯 おすすめの方法

### 小規模ファイル（スクリプトなど）の場合
→ **方法2（cat + コピペ）** が最も簡単です

### 中規模ファイルの場合
→ **方法3（HTTPサーバー）** が便利です

### 大規模ファイルや定期的な転送が必要な場合
→ **方法1（scp/sftp有効化）** を試してください

---

## 🔍 トラブルシューティング

### scpが「Connection refused」と表示される場合

```bash
# SSH設定を確認
ssh -p 23456 AdminUser@192.168.68.110 "sudo cat /etc/ssh/sshd_config | grep -E 'Subsystem|sftp'"
```

### scpが「Permission denied」と表示される場合

```bash
# ファイルの権限を確認
ssh -p 23456 AdminUser@192.168.68.110 "ls -la /usr/local/bin/"
```

### HTTPサーバーが起動しない場合

```bash
# ポート8000が使用されている場合、別のポートを使用
python3 -m http.server 8080

# または、ポートを確認
lsof -i :8000
```

---

## 📚 参考資料

- [OpenSSH公式ドキュメント](https://www.openssh.com/)
- [Python HTTPサーバー](https://docs.python.org/3/library/http.server.html)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

