# 🔒 追加のセキュリティ対策推奨事項

**作成日**: 2025-01-27  
**対象**: 外部アクセス可能なNAS環境

---

## 📋 概要

現在設定済みのセキュリティ対策に加えて、追加で推奨されるセキュリティ対策を優先度順にまとめています。

---

## ✅ 現在完了している対策

1. ✅ **ファイアウォール設定**（組み込みファイアウォール）
   - 内部ネットワークからの全アクセス許可
   - 外部からのHTTPS（8443）アクセスのみ許可
   - 外部からのSSH（23456）アクセスのみ許可

2. ✅ **アプリケーションレベルのセキュリティ**
   - セッションタイムアウト（10分）
   - DOS保護（有効）
   - ログイン失敗時のIPブロック（5分で3回）
   - TLS 1.2以上の強制

---

## 🔐 優先度：高（追加で推奨）

### 1. Fail2banの設定

NASの組み込みファイアウォールとは別に、Fail2banで不正アクセス試行を自動検出してIPをブロックします。

**メリット**:
- 組み込みファイアウォールのログイン失敗時のIPブロックと併用可能
- SSHやNginx Proxy Managerのログを監視して、より詳細な保護を提供
- 自動的にBANされたIPアドレスを管理

**確認方法**:
```bash
# Fail2banの状態を確認
sudo systemctl status fail2ban
sudo fail2ban-client status
```

**設定手順**: `docs/deployment/FAIL2BAN_INSTALL_SETUP.md` を参照

**推奨設定**:
- SSH（23456）を監視（3回失敗で24時間BAN）
- Nginx Proxy Managerを監視（3回失敗で1時間BAN）

---

### 2. Basic認証の確認

Nginx Proxy ManagerでBasic認証が設定されているか確認します。

**確認方法**:
- 外部から `https://yoshi-nas-sys.duckdns.org:8443/` にアクセス
- 認証ダイアログが表示されることを確認

**設定手順**: `docs/deployment/NGINX_PROXY_MANAGER_BASIC_AUTH_SETUP.md` を参照

**推奨設定**:
- 強力なパスワード（12文字以上、大文字・小文字・数字・記号を含む）
- 定期的なパスワード変更

---

## 🔍 優先度：中（強く推奨）

### 3. セキュリティヘッダーの設定

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

**効果**:
- XSS（クロスサイトスクリプティング）攻撃の防止
- クリックジャッキング攻撃の防止
- MIMEタイプスニッフィングの防止
- レート制限によるDoS攻撃の軽減

---

### 4. アクセスログの監視

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

**推奨設定**:
- 毎日アクセスログを確認
- 異常なアクセスパターンを検出したら通知

---

### 5. セキュリティアップデートの定期実行

システムと依存関係のセキュリティパッチを適用します。

**確認方法**:
```bash
# セキュリティアップデートの確認
sudo apt list --upgradable | grep -i security

# セキュリティアップデートスクリプトの確認
crontab -l | grep security-update
```

**定期実行スクリプト**: `docs/deployment/EXTERNAL_ACCESS_SECURITY.md` の「6. セキュリティアップデートの定期実行」を参照

**推奨設定**:
- 週次でセキュリティアップデートを確認
- 重要なセキュリティパッチは即座に適用

---

## 📊 優先度：低（推奨）

### 6. IP制限（固定IPを使用している場合）

特定のIPアドレスからのみアクセスを許可します。

**注意**: 動的IPアドレスを使用している場合は、この設定は推奨しません。

**設定場所**:
- Nginx Proxy ManagerのWeb UI → Access Lists → 新しいアクセスリストを作成 → Whitelist IP addresses

**推奨設定**:
- 管理者の固定IPアドレスのみを許可
- オフィスや自宅の固定IPアドレスを許可

---

### 7. 定期的なバックアップ

データの定期的なバックアップを設定します。

**バックアップスクリプト**: `docs/deployment/EXTERNAL_ACCESS_SECURITY.md` の「9. 定期的なバックアップ」を参照

**推奨設定**:
- 毎日バックアップを実行
- バックアップの確認方法を明確にする
- 30日以上前のバックアップは自動削除

---

### 8. ログローテーションの設定

ログファイルが肥大化しないように設定します。

**設定場所**: `/etc/logrotate.d/nas-projects`

**設定内容**: `docs/deployment/EXTERNAL_ACCESS_SECURITY.md` の「10. ログローテーションの設定」を参照

**推奨設定**:
- 毎日ログをローテート
- 30日分のログを保持
- 古いログは自動圧縮

---

## 🔍 定期チェック項目

### 毎日
- [ ] アクセスログの異常パターンを確認
- [ ] Fail2banのBAN状況を確認（設定している場合）
- [ ] NASの組み込みファイアウォールの通知を確認

### 毎週
- [ ] セキュリティアップデートの確認
- [ ] バックアップの確認
- [ ] SSL証明書の有効期限を確認

### 毎月
- [ ] SSL証明書の有効期限を確認
- [ ] ファイアウォール設定の見直し
- [ ] 不要なポートの確認
- [ ] パスワードの変更（必要に応じて）

---

## 📚 参考資料

- **セキュリティチェックリスト**: `docs/deployment/SECURITY_CHECKLIST.md`
- **外部アクセス時のセキュリティ対策ガイド**: `docs/deployment/EXTERNAL_ACCESS_SECURITY.md`
- **Fail2banインストールと設定**: `docs/deployment/FAIL2BAN_INSTALL_SETUP.md`
- **Basic認証設定**: `docs/deployment/NGINX_PROXY_MANAGER_BASIC_AUTH_SETUP.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

