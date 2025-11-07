# 🔒 UFW（ファイアウォール）インストールと設定ガイド

**作成日**: 2025-01-27  
**対象**: 外部アクセス可能なNAS環境

---

## 📋 概要

UFW（Uncomplicated Firewall）は、Linuxのファイアウォールを簡単に設定できるツールです。外部アクセスを可能にしている場合、UFWで不要なポートを閉鎖し、必要なポートのみを開放することが重要です。

---

## 🚀 インストール手順

### ステップ1: NAS環境にSSH接続

```bash
ssh -p 23456 AdminUser@192.168.68.110
```

### ステップ2: UFWのインストール

```bash
# システムパッケージの更新
sudo apt update

# UFWのインストール
sudo apt install -y ufw
```

### ステップ3: UFWの基本設定

```bash
# 現在のUFWの状態を確認
sudo ufw status

# デフォルトポリシーの設定
# 外部からの接続は拒否、内部からの接続は許可
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH接続を確保（重要！）
sudo ufw allow 23456/tcp comment 'SSH Management'

# 内部ネットワークからのアクセスを許可
sudo ufw allow from 192.168.68.0/24 comment 'Internal Network'

# 外部からのHTTPSアクセスのみ許可
sudo ufw allow 8443/tcp comment 'HTTPS - Nginx Proxy Manager'

# UFWを有効化
sudo ufw enable

# 設定の確認
sudo ufw status verbose
```

---

## 🔍 推奨設定

### 外部から許可するポート

- ✅ **8443/tcp**: HTTPS（Nginx Proxy Manager経由）
- ✅ **23456/tcp**: SSH（管理用）

### 内部ネットワークからのみ許可するポート

以下のポートは内部ネットワーク（192.168.68.0/24）からのみアクセス可能にします：

- **9001**: nas-dashboard
- **8001**: amazon-analytics
- **8080**: document-automation
- **5002**: meeting-minutes-byc
- **3002**: nas-dashboard-monitoring (frontend)
- **8002**: nas-dashboard-monitoring (backend)
- **8111**: youtube-to-notion
- **8181**: Nginx Proxy Manager Admin

**注意**: これらのポートは、内部ネットワークからのアクセスが既に許可されているため、個別に設定する必要はありません（`sudo ufw allow from 192.168.68.0/24`で全て許可されています）。

---

## ⚠️ 重要な注意事項

### SSH接続を確保する

UFWを有効化する前に、必ずSSHポート（23456）を許可してください。SSH接続が切断されると、リモートからアクセスできなくなります。

```bash
# UFWを有効化する前に必ず実行
sudo ufw allow 23456/tcp comment 'SSH Management'
```

### 設定の確認

UFWを有効化した後、必ず設定を確認してください：

```bash
sudo ufw status verbose
```

期待される出力例：
```
Status: active

To                         Action      From
--                         ------      ----
23456/tcp                  ALLOW       Anywhere          # SSH Management
8443/tcp                   ALLOW       Anywhere          # HTTPS - Nginx Proxy Manager
Anywhere                   ALLOW       192.168.68.0/24   # Internal Network
```

---

## 🔧 トラブルシューティング

### UFWを無効化する（緊急時）

SSH接続が切断された場合、内部ネットワークから以下のコマンドを実行：

```bash
# UFWを一時的に無効化
sudo ufw disable

# または、特定のポートを一時的に許可
sudo ufw allow 8443/tcp
```

### 特定のポートを削除する

```bash
# ルール番号を確認
sudo ufw status numbered

# ルールを削除（例: ルール番号3を削除）
sudo ufw delete 3
```

### ルールを追加する

```bash
# ポートを許可
sudo ufw allow 8443/tcp comment 'HTTPS'

# IPアドレスからのアクセスを許可
sudo ufw allow from 192.168.68.0/24 comment 'Internal Network'

# ポート範囲を許可
sudo ufw allow 8000:9000/tcp comment 'Port Range'
```

---

## 📊 設定後の確認

### 1. UFWの状態確認

```bash
sudo ufw status verbose
```

### 2. 外部からのアクセステスト

```bash
# 外部からHTTPSでアクセスできるか確認
curl -I https://yoshi-nas-sys.duckdns.org:8443

# 外部から直接ポートでアクセスできないことを確認（例: 9001）
curl -I http://yoshi-nas-sys.duckdns.org:9001
# タイムアウトまたは接続拒否が期待される
```

### 3. 内部からのアクセステスト

```bash
# 内部ネットワークから全てのポートにアクセスできることを確認
curl http://192.168.68.110:9001
curl http://192.168.68.110:8001
curl http://192.168.68.110:8080
```

---

## 🔍 セキュリティ確認スクリプト

UFWの設定状況を確認するには、以下のスクリプトを実行してください：

```bash
cd ~/nas-project
./scripts/check-security-status.sh
```

このスクリプトは以下を確認します：
- ✅ UFWがインストールされている
- ✅ UFWが有効化されている
- ✅ HTTPS（8443）が外部から許可されている
- ✅ SSH（23456）が外部から許可されている
- ✅ 内部ネットワークからのアクセスが許可されている

---

## 📚 参考資料

- **外部アクセス時のセキュリティ対策ガイド**: `docs/deployment/EXTERNAL_ACCESS_SECURITY.md`
- **緊急セキュリティ対策設定**: `docs/deployment/SECURITY_SETUP_URGENT.md`
- **セキュリティチェックリスト**: `docs/deployment/SECURITY_CHECKLIST.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

