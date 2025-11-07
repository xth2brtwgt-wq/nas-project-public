# 🔄 SSL証明書の自動更新ガイド

**作成日**: 2025-11-02  
**対象**: acme.sh + Nginx Proxy Manager構成

---

## 📋 現在の構成

- **証明書取得ツール**: acme.sh（DuckDNS DNS-01チャレンジ）
- **証明書の場所**: `~/.acme.sh/yoshi-nas-sys.duckdns.org_ecc/`
- **証明書管理**: Nginx Proxy Manager（手動インポート）

---

## 🎯 自動更新の方法

### 方法1: acme.shの自動更新 + Nginx Proxy Manager再インポート（推奨）

acme.shはデフォルトで自動更新機能を持っていますが、Nginx Proxy Managerへの再インポートは手動で行う必要があります。

#### 1-1. acme.shの自動更新の確認

acme.shはデフォルトでcronジョブを設定します：

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# cronジョブを確認
crontab -l | grep acme.sh

# 通常は以下のようなエントリが表示されます:
# 0 0 * * * "/home/AdminUser/.acme.sh"/acme.sh --cron --home "/home/AdminUser/.acme.sh" > /dev/null
```

#### 1-2. 証明書更新後の自動再インポートスクリプト

証明書を更新した後、Nginx Proxy Managerに自動的に再インポートするスクリプトを作成します：

```bash
# スクリプトを作成
sudo nano /usr/local/bin/renew-cert-and-reload.sh
```

以下の内容を記述：

```bash
#!/bin/bash
# acme.sh証明書更新 + Nginx Proxy Manager再インポートスクリプト

DOMAIN="yoshi-nas-sys.duckdns.org"
ACME_DIR="$HOME/.acme.sh/${DOMAIN}_ecc"
NPM_CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"

# acme.shで証明書を更新
~/.acme.sh/acme.sh --renew -d ${DOMAIN} --ecc

# 証明書ファイルを/etc/letsencrypt/live/にコピー（Nginx Proxy Managerが参照）
sudo mkdir -p ${NPM_CERT_DIR}
sudo cp ${ACME_DIR}/fullchain.cer ${NPM_CERT_DIR}/fullchain.pem
sudo cp ${ACME_DIR}/${DOMAIN}.key ${NPM_CERT_DIR}/privkey.pem

# ファイルの権限を設定
sudo chown root:root ${NPM_CERT_DIR}/*.pem
sudo chmod 644 ${NPM_CERT_DIR}/fullchain.pem
sudo chmod 600 ${NPM_CERT_DIR}/privkey.pem

# Nginx Proxy Managerのコンテナを再起動（証明書を再読み込み）
docker restart nginx-proxy-manager

echo "証明書の更新とNginx Proxy Managerの再読み込みが完了しました: $(date)"
```

スクリプトに実行権限を付与：

```bash
sudo chmod +x /usr/local/bin/renew-cert-and-reload.sh
```

#### 1-3. cronジョブの設定

acme.shの自動更新後に、上記のスクリプトを実行するようにcronジョブを設定：

```bash
# cronジョブを編集
crontab -e

# 以下の行を追加（毎日午前3時に実行）
0 3 * * * /usr/local/bin/renew-cert-and-reload.sh >> /var/log/cert-renewal.log 2>&1
```

---

### 方法2: Nginx Proxy Managerの自動更新機能を使用

Nginx Proxy ManagerはLet's Encrypt証明書を直接取得・自動更新する機能を持っています。

#### 2-1. Nginx Proxy Managerでの証明書設定変更

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`（管理ポート）

2. **「SSL Certificates」タブを開く**

3. **現在の証明書を削除または無効化**

4. **「Add SSL Certificate」→「Let's Encrypt」を選択**

5. **証明書情報を入力**
   - **Domain Names**: `yoshi-nas-sys.duckdns.org`
   - **Email Address**: `nas.system.0828@gmail.com`
   - **Agree to Terms**: チェック

6. **Use a DNS Challenge**: **ON**（推奨）
   - **DNS Provider**: `duckdns`
   - **DuckDNS Token**: DuckDNSのトークンを入力

7. **「Save」をクリック**

#### 2-2. Proxy Host設定で証明書を選択

1. **「Proxy Hosts」タブを開く**

2. **対象のProxy Host（yoshi-nas-sys.duckdns.org）を編集**

3. **「SSL」タブで証明書を選択**
   - **SSL Certificate**: 新しく作成したLet's Encrypt証明書を選択

4. **「Save」をクリック**

#### 2-3. 自動更新の確認

Nginx Proxy Managerは自動的に証明書を更新します：
- 証明書の有効期限が30日以内になったら自動更新
- 更新はNginx Proxy Managerが自動的に管理

---

## 🧪 テスト方法

### 証明書の有効期限を確認

```bash
# 現在の証明書の有効期限を確認
openssl s_client -connect yoshi-nas-sys.duckdns.org:8443 -servername yoshi-nas-sys.duckdns.org </dev/null 2>/dev/null | openssl x509 -noout -dates

# 出力例:
# notBefore=Nov  1 08:28:44 2025 GMT
# notAfter=Jan 30 08:28:43 2026 GMT
```

### acme.shの自動更新テスト

```bash
# acme.shの更新テスト（実際には更新しない）
~/.acme.sh/acme.sh --renew -d yoshi-nas-sys.duckdns.org --ecc --force --dry-run
```

### Nginx Proxy Managerの証明書更新テスト

Nginx Proxy ManagerのWeb UIで：
1. **「SSL Certificates」タブを開く**
2. 証明書を選択
3. **「Renew Certificate」ボタンをクリック**（ある場合）

---

## ⚠️ トラブルシューティング

### acme.shの自動更新が失敗する場合

**エラー: "DNS propagation check failed"**
- DNS反映を待ってから再試行
- DuckDNSのAPIトークンが正しいか確認

**エラー: "Rate limit exceeded"**
- Let's Encryptのレート制限に達している
- 1時間待ってから再試行

### Nginx Proxy Managerの証明書更新が失敗する場合

**エラー: "Internal Error"**
- ポート80または443へのアクセスがブロックされている可能性
- DNS-01チャレンジを使用していることを確認

**証明書が更新されない**
- Nginx Proxy Managerのログを確認
- 手動で証明書を再取得してみる

---

## 📝 チェックリスト

### 方法1（acme.sh + スクリプト）を使用する場合

- [ ] acme.shのcronジョブが設定されている
- [ ] 証明書更新・再インポートスクリプトを作成
- [ ] スクリプトに実行権限を付与
- [ ] cronジョブを設定
- [ ] スクリプトの動作テスト

### 方法2（Nginx Proxy Manager自動更新）を使用する場合

- [ ] Nginx Proxy ManagerでLet's Encrypt証明書を作成
- [ ] Proxy Host設定で証明書を選択
- [ ] 証明書の自動更新が有効か確認

---

## 🔍 証明書の有効期限監視

証明書の有効期限を定期的に監視するスクリプト：

```bash
#!/bin/bash
# 証明書の有効期限チェックスクリプト

DOMAIN="yoshi-nas-sys.duckdns.org"
EXPIRY_DATE=$(echo | openssl s_client -connect ${DOMAIN}:8443 -servername ${DOMAIN} 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
CURRENT_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt 30 ]; then
    echo "警告: ${DOMAIN} の証明書は ${DAYS_LEFT} 日後に期限切れです"
    # メール通知やSlack通知などをここに追加
else
    echo "証明書は ${DAYS_LEFT} 日間有効です"
fi
```

---

## 📚 参考資料

- [acme.sh公式ドキュメント](https://github.com/acmesh-official/acme.sh)
- [Nginx Proxy Manager公式ドキュメント](https://nginxproxymanager.com/)
- [Let's Encrypt公式サイト](https://letsencrypt.org/)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

