# 🔒 外部アクセス時のセキュリティ対策チェックリスト

**作成日**: 2025-01-27  
**対象**: 外部アクセス可能なNAS環境

---

## 📋 概要

外部アクセスを可能にしている場合に実施すべきセキュリティ対策を優先度順にまとめています。

---

## ✅ 優先度：高（必須）

### 1. ファイアウォール設定

外部からアクセス可能なポートを最小限に制限します。

**設定方法（2つの選択肢）**:

#### 方法1: NAS組み込みファイアウォール（推奨・GUIで簡単）

NAS管理画面の「セキュリティ」→「ファイアウォール」から設定します。

**設定手順**: `docs/deployment/NAS_BUILTIN_FIREWALL_SETUP.md` を参照

**メリット**:
- ✅ GUIで簡単に設定できる
- ✅ 通知機能が統合されている
- ✅ NAS管理画面から直接設定できる

#### 方法2: UFW（コマンドライン）

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# UFWの状態を確認
sudo ufw status verbose
```

**設定手順**: `docs/deployment/UFW_INSTALL_SETUP.md` を参照

**推奨設定**（どちらの方法でも同じ）:
- ✅ 外部からはHTTPS（8443）のみ許可
- ✅ SSH（23456）は外部からアクセス可能（管理用）
- ✅ 内部ネットワーク（192.168.68.0/24）からは全てアクセス可能
- ❌ その他のポート（9001, 8001, 8080, 5002, 3002, 8002, 8111）は外部からアクセス不可

**注意**: 組み込みファイアウォールとUFWは同時に使用しないでください。どちらか一方を選択してください。

**チェック項目**:
- [ ] ファイアウォールが有効化されている（組み込みまたはUFW）
- [ ] 外部からは8443（HTTPS）のみ許可されている
- [ ] その他のポートは内部ネットワークからのみアクセス可能

---

### 2. Fail2banの設定

不正アクセス試行を自動検出してIPをブロックします。

**確認方法**:
```bash
# Fail2banの状態を確認
sudo systemctl status fail2ban
sudo fail2ban-client status

# SSH jailの状態を確認
sudo fail2ban-client status sshd
```

**推奨設定**:
- ✅ SSH（23456）を監視（3回失敗で24時間BAN）
- ✅ Nginx Proxy Managerを監視（3回失敗で1時間BAN）

**設定手順**: `docs/deployment/FAIL2BAN_INSTALL_SETUP.md` を参照

**チェック項目**:
- [ ] Fail2banがインストールされている
- [ ] Fail2banが稼働中である
- [ ] SSH jailが有効化されている（ポート23456）
- [ ] Nginx Proxy Manager用のjailが有効化されている

---

### 3. HTTPS設定

すべての外部アクセスはHTTPS経由にします。

**確認方法**:
```bash
# 外部からHTTPSでアクセスできるか確認
curl -I https://yoshi-nas-sys.duckdns.org:8443

# SSL証明書の有効期限を確認
openssl s_client -connect yoshi-nas-sys.duckdns.org:8443 -servername yoshi-nas-sys.duckdns.org < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

**チェック項目**:
- [ ] HTTPSでアクセス可能である
- [ ] SSL証明書が有効である
- [ ] 証明書の自動更新が設定されている

---

### 4. Basic認証の設定

Nginx Proxy ManagerでBasic認証を設定します。

**確認方法**:
- 外部から `https://yoshi-nas-sys.duckdns.org:8443/` にアクセス
- 認証ダイアログが表示されることを確認

**設定手順**: `docs/deployment/NGINX_PROXY_MANAGER_BASIC_AUTH_SETUP.md` を参照

**チェック項目**:
- [ ] Basic認証が有効化されている
- [ ] 強力なパスワードが設定されている（12文字以上、大文字・小文字・数字・記号を含む）
- [ ] 認証ダイアログが表示される

---

## 🔍 優先度：中（強く推奨）

### 5. セキュリティヘッダーの設定

Nginx Proxy Managerでセキュリティヘッダーを設定します。

**設定場所**:
- Nginx Proxy ManagerのWeb UI → Proxy Hosts → yoshi-nas-sys.duckdns.org → Advanced → Custom Nginx Configuration

**推奨設定**:
```nginx
# セキュリティヘッダー
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: ws:;" always;

# レート制限
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req zone=general burst=20 nodelay;
```

**設定手順**: `docs/deployment/EXTERNAL_ACCESS_SECURITY.md` の「3. Nginx Proxy Managerでのセキュリティヘッダー設定」を参照

**チェック項目**:
- [ ] Strict-Transport-Securityヘッダーが設定されている
- [ ] X-Frame-Optionsヘッダーが設定されている
- [ ] X-Content-Type-Optionsヘッダーが設定されている
- [ ] X-XSS-Protectionヘッダーが設定されている
- [ ] Content-Security-Policyヘッダーが設定されている
- [ ] レート制限が設定されている

---

### 6. アクセスログの監視

不正アクセスの兆候を早期に検出します。

**確認方法**:
```bash
# Nginx Proxy Managerのアクセスログを確認
docker logs nginx-proxy-manager --tail 100

# 不正アクセスのパターンを確認
sudo grep -i "401\|403\|404" /var/log/nginx/access.log | tail -50

# 異常なアクセス試行を確認
sudo grep -E "(failed|unauthorized|forbidden)" /var/log/nginx/error.log
```

**定期チェックスクリプト**: `docs/deployment/EXTERNAL_ACCESS_SECURITY.md` の「5. アクセスログの監視」を参照

**チェック項目**:
- [ ] アクセスログの定期チェックスクリプトが設定されている
- [ ] 異常なアクセスパターンを確認する仕組みがある

---

### 7. セキュリティアップデートの定期実行

システムと依存関係のセキュリティパッチを適用します。

**確認方法**:
```bash
# セキュリティアップデートの確認
sudo apt list --upgradable | grep -i security

# セキュリティアップデートスクリプトの確認
crontab -l | grep security-update
```

**定期実行スクリプト**: `docs/deployment/EXTERNAL_ACCESS_SECURITY.md` の「6. セキュリティアップデートの定期実行」を参照

**チェック項目**:
- [ ] セキュリティアップデートの定期実行スクリプトが設定されている
- [ ] 週次でセキュリティアップデートが実行される

---

## 📊 優先度：低（推奨）

### 8. IP制限（固定IPを使用している場合）

特定のIPアドレスからのみアクセスを許可します。

**注意**: 動的IPアドレスを使用している場合は、この設定は推奨しません。

**設定場所**:
- Nginx Proxy ManagerのWeb UI → Access Lists → 新しいアクセスリストを作成 → Whitelist IP addresses

**チェック項目**:
- [ ] 固定IPアドレスを使用している場合のみ設定
- [ ] 許可するIPアドレスが正しく設定されている

---

### 9. 定期的なバックアップ

データの定期的なバックアップを設定します。

**バックアップスクリプト**: `docs/deployment/EXTERNAL_ACCESS_SECURITY.md` の「9. 定期的なバックアップ」を参照

**チェック項目**:
- [ ] バックアップスクリプトが設定されている
- [ ] 定期的にバックアップが実行されている
- [ ] バックアップの確認方法が明確である

---

### 10. ログローテーションの設定

ログファイルが肥大化しないように設定します。

**設定場所**: `/etc/logrotate.d/nas-projects`

**設定内容**: `docs/deployment/EXTERNAL_ACCESS_SECURITY.md` の「10. ログローテーションの設定」を参照

**チェック項目**:
- [ ] ログローテーションが設定されている
- [ ] ログファイルが適切にローテートされている

---

## 🔍 定期チェック項目

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

## 🛠️ 現在の設定状況を確認するスクリプト

以下のスクリプトを実行して、現在の設定状況を確認できます：

```bash
# セキュリティ設定確認スクリプトを実行
./scripts/check-security-status.sh
```

**確認項目**:
- UFWの状態
- Fail2banの状態
- SSL証明書の有効期限
- Basic認証の設定
- セキュリティヘッダーの設定

---

## 📚 参考資料

- **外部アクセス時のセキュリティ対策ガイド**: `docs/deployment/EXTERNAL_ACCESS_SECURITY.md`
- **緊急セキュリティ対策設定**: `docs/deployment/SECURITY_SETUP_URGENT.md`
- **Fail2banインストールと設定**: `docs/deployment/FAIL2BAN_INSTALL_SETUP.md`
- **Basic認証設定**: `docs/deployment/NGINX_PROXY_MANAGER_BASIC_AUTH_SETUP.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

