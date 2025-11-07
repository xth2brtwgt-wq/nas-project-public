# Sudo非対話実行設定ガイド

## 概要
チャット内でsudoコマンドを非対話的に実行できるようにするための設定手順です。

## 前提条件
- NAS環境へのSSHアクセス権限
- 管理者権限（AdminUser）
- sudoersファイルの編集権限

---

## 方法1: sudoersファイルでNOPASSWD設定（推奨）

### メリット
- 特定のコマンドのみにsudo権限を付与（セキュリティ性が高い）
- パスワード入力不要
- 永続的な設定

### 設定手順

#### 1. sudoersファイルのバックアップ
```bash
sudo cp /etc/sudoers /etc/sudoers.backup.$(date +%Y%m%d)
```

#### 2. sudoers.dディレクトリに設定ファイルを作成（推奨）
```bash
# NAS環境（AdminUser）の場合
sudo visudo -f /etc/sudoers.d/adminuser-nopasswd
```

#### 3. 必要なコマンドにNOPASSWDを設定

**nas-dashboard-monitoring用の設定例:**
```bash
# nas-dashboard-monitoring: Docker関連コマンド
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/docker
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/docker compose
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/docker-compose
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart docker
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/systemctl status docker

# ログファイル読み取り
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/tail
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/cat /var/log/*
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/less /var/log/*

# SSH設定ファイル読み取り（既にマウントされている場合は不要）
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/cat /etc/ssh/sshd_config
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/cat /etc/ssh/sshd_config.d/*

# データディレクトリ管理（必要に応じて）
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/mkdir -p /home/AdminUser/nas-project-data/*
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/chown -R AdminUser:admin /home/AdminUser/nas-project-data/*
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/chmod -R 755 /home/AdminUser/nas-project-data/*
```

#### 4. 設定の確認
```bash
# 構文チェック
sudo visudo -c

# 実際のテスト
sudo -n docker ps
```

---

## 方法2: 環境変数でSUDO_PASSWORDを設定

### 注意事項
⚠️ **セキュリティリスクがあります**
- 環境変数にパスワードを保存するため、ログやプロセス一覧に表示される可能性があります
- 本番環境での使用は非推奨

### 設定手順

#### 1. 環境変数の設定
```bash
# .envに追加（実際の稼働設定）
echo "SUDO_PASSWORD=your_password_here" >> .env

# .env.restoreをバックアップとして作成（推奨）
cp .env .env.restore
```

#### 2. sudo実行ヘルパー関数の作成
```python
# utils/sudo_helper.py
import subprocess
import os
import getpass

def run_sudo_command(command: list[str], password: str | None = None) -> subprocess.CompletedProcess:
    """
    sudoコマンドを非対話的に実行する
    
    Args:
        command: 実行するコマンド（リスト形式）
        password: sudoパスワード（Noneの場合は環境変数から取得）
    
    Returns:
        subprocess.CompletedProcess: 実行結果
    """
    if password is None:
        password = os.getenv('SUDO_PASSWORD')
    
    if password is None:
        # 環境変数にない場合は対話的に取得
        password = getpass.getpass('sudo password: ')
    
    # echoパスワード | sudo -S コマンドで実行
    cmd = ['sudo', '-S'] + command
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=password + '\n')
    
    return subprocess.CompletedProcess(
        cmd,
        process.returncode,
        stdout,
        stderr
    )
```

#### 3. 使用例
```python
from utils.sudo_helper import run_sudo_command

# Dockerコマンドの実行
result = run_sudo_command(['docker', 'ps'])
if result.returncode == 0:
    print(result.stdout)
else:
    print(f"Error: {result.stderr}")
```

---

## 方法3: sudoタイムアウトの活用

### 説明
sudoで一度パスワードを入力すると、デフォルトで15分間は再入力不要になります。

### 設定手順

#### 1. sudoタイムアウトの延長（オプション）
```bash
# sudoersファイルに追加
sudo visudo

# 以下を追加（タイムアウトを30分に延長）
Defaults timestamp_timeout=30
```

#### 2. 使用例
```bash
# 初回: パスワードを入力
sudo docker ps

# 15分以内（または設定した時間内）は再入力不要
sudo docker compose up -d
```

---

## 推奨設定（NAS環境）

NAS環境では、**方法1（sudoersファイル設定）**を推奨します。

### セキュリティを考慮した設定例

```bash
# /etc/sudoers.d/adminuser-nopasswd
# このファイルはGit管理外（.gitignoreに追加）

# Docker関連（必要最小限）
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/docker ps
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/docker logs
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/docker compose up
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/docker compose down
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/docker compose restart

# ログ読み取り（読み取り専用）
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/tail -n * /var/log/*
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/cat /var/log/*

# データディレクトリ管理（必要に応じて）
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/mkdir -p /home/AdminUser/nas-project-data/*
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/chown -R AdminUser:admin /home/AdminUser/nas-project-data/*
AdminUser ALL=(ALL) NOPASSWD: /usr/bin/chmod -R 755 /home/AdminUser/nas-project-data/*
```

### 設定後の確認

```bash
# 1. 構文チェック
sudo visudo -c

# 2. 実際のテスト
sudo -n docker ps
sudo -n tail -n 10 /var/log/auth.log

# 3. 権限確認
sudo -l
```

---

## トラブルシューティング

### エラー: "sudo: no tty present and no askpass program specified"
**原因**: sudoがパスワードを要求しているが、非対話的な環境で実行できない

**解決策**:
1. sudoersファイルでNOPASSWDを設定する（方法1）
2. `SUDO_PASSWORD`環境変数を設定する（方法2、非推奨）

### エラー: "sudoersファイルの構文エラー"
**原因**: sudoersファイルの構文が間違っている

**解決策**:
```bash
# 構文チェック
sudo visudo -c

# エラーが発生した場合は、バックアップから復元
sudo cp /etc/sudoers.backup.* /etc/sudoers
```

### エラー: "permission denied"
**原因**: sudoersファイルで許可されていないコマンドを実行している

**解決策**:
1. 必要なコマンドをsudoersファイルに追加
2. または、`sudo -l`で現在の権限を確認

---

## セキュリティ注意事項

1. **最小権限の原則**: 必要なコマンドのみにsudo権限を付与
2. **sudoersファイルの保護**: `/etc/sudoers.d/`のファイルは適切な権限（644）で保護
3. **定期的な監査**: 設定したsudo権限を定期的に見直す
4. **ログ監視**: sudoコマンドの実行ログを監視（`/var/log/auth.log`）

---

## 参考リンク

- [sudoers(5) man page](https://www.sudo.ws/man/1.8.15/sudoers.man.html)
- [sudo NOPASSWD設定](https://www.sudo.ws/man/1.8.15/sudoers.man.html#NOPASSWD_and_NOPASSWD)



