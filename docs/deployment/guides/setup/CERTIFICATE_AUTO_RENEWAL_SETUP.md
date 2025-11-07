# 🔄 SSL証明書自動更新の設定手順

**作成日**: 2025-11-02  
**対象**: acme.sh + Nginx Proxy Manager構成

---

## 📋 前提条件

- acme.shで証明書を取得済み
- Nginx Proxy Managerに証明書を手動インポート済み
- NASにSSH接続可能

---

## 🚀 設定手順

### ステップ1: スクリプトをNASにコピー

```bash
# ローカルから実行
cd /Users/Yoshi/nas-project

# スクリプトをNASにコピー
scp -P 23456 scripts/renew-cert-and-reload.sh AdminUser@192.168.68.110:/tmp/
```

### ステップ2: NAS上でスクリプトを配置

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# スクリプトを適切な場所にコピー
sudo cp /tmp/renew-cert-and-reload.sh /usr/local/bin/

# 実行権限を付与
sudo chmod +x /usr/local/bin/renew-cert-and-reload.sh

# スクリプトの内容を確認
cat /usr/local/bin/renew-cert-and-reload.sh
```

### ステップ3: Nginx Proxy Managerのコンテナ名を確認

```bash
# Nginx Proxy Managerのコンテナ名を確認
docker ps --format "{{.Names}}" | grep -i "nginx.*proxy.*manager\|npm"

# 例:
# nginx-proxy-manager
# npm
# nginx-proxy-manager_app
```

**重要**: 上記のコマンドで表示されたコンテナ名をメモしてください。

### ステップ4: スクリプトの動作テスト

```bash
# スクリプトを手動実行してテスト
sudo /usr/local/bin/renew-cert-and-reload.sh

# ログを確認
sudo tail -20 /var/log/cert-renewal.log
```

### ステップ5: acme.shの自動更新の確認

```bash
# acme.shのcronジョブを確認
crontab -l | grep acme.sh

# 通常は以下のようなエントリが表示されます:
# 0 0 * * * "/home/AdminUser/.acme.sh"/acme.sh --cron --home "/home/AdminUser/.acme.sh" > /dev/null

# もし表示されない場合は、acme.shがまだcronジョブを設定していない可能性があります
# その場合は、以下のコマンドでcronジョブを確認:
crontab -l
```

### ステップ6: cronジョブの設定

acme.shの自動更新後（毎日午前0時）に、証明書の再インポートスクリプトを実行するようにcronジョブを設定します。

```bash
# cronジョブを編集
crontab -e

# 以下の行を追加（acme.shの自動更新の後、毎日午前3時に実行）
# 注意: acme.shの自動更新が毎日午前0時に実行されるため、
#       証明書の再インポートは午前3時に実行するように設定
0 3 * * * /usr/local/bin/renew-cert-and-reload.sh >> /var/log/cert-renewal.log 2>&1

# 保存してエディタを終了（nanoの場合は Ctrl+X → Y → Enter）
```

### ステップ7: cronジョブの確認

```bash
# cronジョブの一覧を確認
crontab -l

# 以下のような出力が表示されるはずです:
# 0 0 * * * "/home/AdminUser/.acme.sh"/acme.sh --cron --home "/home/AdminUser/.acme.sh" > /dev/null
# 0 3 * * * /usr/local/bin/renew-cert-and-reload.sh >> /var/log/cert-renewal.log 2>&1
```

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

# 実際に更新する場合（証明書が期限切れ間近の場合のみ更新される）
~/.acme.sh/acme.sh --renew -d yoshi-nas-sys.duckdns.org --ecc
```

### スクリプトの手動実行テスト

```bash
# スクリプトを手動実行
sudo /usr/local/bin/renew-cert-and-reload.sh

# ログを確認
sudo tail -50 /var/log/cert-renewal.log
```

---

## ⚠️ トラブルシューティング

### スクリプトが実行されない場合

**エラー: "Permission denied"**
```bash
# スクリプトの実行権限を確認
ls -l /usr/local/bin/renew-cert-and-reload.sh

# 実行権限がない場合は付与
sudo chmod +x /usr/local/bin/renew-cert-and-reload.sh
```

**エラー: "acme.shが見つかりません"**
```bash
# acme.shの場所を確認
ls -la ~/.acme.sh/acme.sh

# もし見つからない場合は、acme.shを再インストール
curl https://get.acme.sh | sh
source ~/.bashrc
```

### Nginx Proxy Managerのコンテナが見つからない場合

**スクリプトでコンテナが見つからない**
```bash
# 全てのDockerコンテナを確認
docker ps -a

# Nginx Proxy Managerのコンテナを手動で確認
docker ps | grep -i nginx

# コンテナ名が異なる場合は、スクリプトを編集
sudo nano /usr/local/bin/renew-cert-and-reload.sh

# 以下の行を修正:
# NPM_CONTAINER=$(docker ps --format "{{.Names}}" | grep -i "nginx.*proxy.*manager\|npm" | head -1)
# 実際のコンテナ名に変更:
# NPM_CONTAINER="実際のコンテナ名"
```

### 証明書が更新されない場合

**acme.shの自動更新が動作していない**
```bash
# cronジョブを確認
crontab -l | grep acme.sh

# もし見つからない場合は、acme.shを再インストールしてcronジョブを再設定
curl https://get.acme.sh | sh
source ~/.bashrc
```

**証明書ファイルがコピーされない**
```bash
# 証明書ファイルの存在を確認
ls -la ~/.acme.sh/yoshi-nas-sys.duckdns.org_ecc/

# コピー先のディレクトリを確認
ls -la /etc/letsencrypt/live/yoshi-nas-sys.duckdns.org/
```

---

## 📝 チェックリスト

設定が完了したら、以下を確認してください:

- [ ] スクリプトをNASにコピー済み
- [ ] スクリプトに実行権限を付与済み
- [ ] acme.shのcronジョブが設定されている
- [ ] 証明書再インポートスクリプトのcronジョブが設定されている
- [ ] スクリプトの手動実行テストが成功
- [ ] 証明書の有効期限を確認済み

---

## 🔍 証明書の有効期限監視（オプション）

証明書の有効期限を定期的に監視するスクリプト:

```bash
# 監視スクリプトを作成
sudo nano /usr/local/bin/check-cert-expiry.sh
```

以下の内容を記述:

```bash
#!/bin/bash
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

```bash
# 実行権限を付与
sudo chmod +x /usr/local/bin/check-cert-expiry.sh

# cronジョブに追加（毎週月曜日に実行）
crontab -e

# 以下の行を追加:
0 9 * * 1 /usr/local/bin/check-cert-expiry.sh >> /var/log/cert-expiry-check.log 2>&1
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

