# 🔧 Certbot AttributeError トラブルシューティング

**作成日**: 2025-01-27  
**対象**: certbot 2.1.0でのAttributeErrorエラー

---

## 📋 問題

```
AttributeError: can't set attribute
```

これはcertbot 2.1.0の既知の問題です。

---

## 🔧 解決方法

### 方法1: certbotの設定ファイルをクリーンアップ（推奨）

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# certbotの設定ディレクトリをバックアップ
sudo cp -r /etc/letsencrypt /etc/letsencrypt.backup

# アカウント情報を削除（再登録が必要）
sudo rm -rf /etc/letsencrypt/accounts
sudo rm -rf /etc/letsencrypt/renewal

# 証明書取得を再試行
sudo certbot certonly --authenticator dns-duckdns --dns-duckdns-credentials /etc/letsencrypt/duckdns.ini -d yoshi-nas-sys.duckdns.org --non-interactive --agree-tos --email nas.system.0828@gmail.com
```

### 方法2: 手動で証明書を取得（別の方法）

certbotの問題を回避するため、**acme.sh**という別のツールを使用する方法もあります。

#### acme.shのインストール

```bash
# NAS上で実行
curl https://get.acme.sh | sh

# シェルを再読み込み
source ~/.bashrc
```

#### acme.shで証明書取得

```bash
# DuckDNS APIトークンを設定
export DuckDNS_Token="b505b11e-157c-4966-8816-b9865cd0bfee"

# 証明書取得
~/.acme.sh/acme.sh --issue --dns dns_duckdns -d yoshi-nas-sys.duckdns.org

# 証明書をコピー（nginxが使用する場所へ）
sudo ~/.acme.sh/acme.sh --install-cert -d yoshi-nas-sys.duckdns.org \
  --key-file /etc/letsencrypt/live/yoshi-nas-sys.duckdns.org/privkey.pem \
  --fullchain-file /etc/letsencrypt/live/yoshi-nas-sys.duckdns.org/fullchain.pem \
  --reloadcmd "sudo systemctl reload nginx"
```

### 方法3: レート制限が解除されるまで待つ

Let's Encryptのレート制限（1時間に5回の失敗）が解除されるまで待ちます。

次回の証明書取得は、前回の失敗から1時間後に行ってください。

---

## 🎯 推奨される手順

1. **まず方法1を試す**（設定ファイルのクリーンアップ）
2. それでもエラーが出る場合は**方法2を試す**（acme.shを使用）
3. レート制限が解除されるまで待つ（方法3）

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27  
**作成者**: AI Assistant


