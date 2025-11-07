# 🔒 Let's Encrypt証明書取得 - DNS-01チャレンジ（ポート80不要）

**作成日**: 2025-01-27  
**対象**: ポート80が使用できない環境での証明書取得

---

## 📋 概要

DNS-01チャレンジを使用すると、ポート80は不要です。DuckDNSのDNSレコードにTXTレコードを追加することで証明書を取得できます。

**メリット:**
- ポート80が不要
- ファイアウォール設定が不要
- ルーターのポート転送設定が不要

**デメリット:**
- 手動でDNSレコードを追加する必要がある（自動化可能）

---

## 🚀 手順: DNS-01チャレンジで証明書取得

### ステップ1: certbotのインストール（まだの場合）

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# certbotのインストール
sudo apt update
sudo apt install certbot -y
```

### ステップ2: DNS-01チャレンジで証明書取得

```bash
# 証明書取得（DNS-01チャレンジ）
sudo certbot certonly --manual --preferred-challenges dns -d yoshi-nas-sys.duckdns.org
```

### ステップ3: certbotの指示に従う

#### 3-1. メールアドレス入力

```
Enter email address (used for urgent renewal and security notices)
 (Enter 'c' to cancel): nas.system.0828@gmail.com
```

#### 3-2. 利用規約への同意

```
Please read the Terms of Service...
(Y)es/(N)o: Y
```

#### 3-3. メール共有の選択

```
Would you be willing to share your email address...
(Y)es/(N)o: N
```

#### 3-4. TXTレコードの追加指示

certbotが以下のような指示を表示します：

```
Please deploy a DNS TXT record under the name
_acme-challenge.yoshi-nas-sys.duckdns.org with the following value:

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

Before continuing, verify the record is deployed.
```

**重要:** この値をコピーしてください（例: `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`）

### ステップ4: DuckDNSでTXTレコードを追加

1. **DuckDNSのダッシュボードにアクセス**
   - https://www.duckdns.org/ にアクセス
   - ログイン

2. **ドメインを選択**
   - `yoshi-nas-sys` を選択

3. **TXTレコードを追加**
   - DuckDNSのダッシュボードで「TXT」または「Add TXT」を探す
   - 以下の情報を入力：
     - **Name**: `_acme-challenge.yoshi-nas-sys` （または `_acme-challenge`）
     - **Value**: certbotが表示した値（例: `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`）
   - 「Add」または「Save」をクリック

**注意:** DuckDNSのTXTレコード設定画面の場所は、ダッシュボードによって異なります。メニューや「Advanced」などのタブを確認してください。

### ステップ5: DNSレコードの反映を待つ

TXTレコードの反映には数分かかる場合があります。

```bash
# DNSレコードが反映されているか確認（別ターミナルで）
dig TXT _acme-challenge.yoshi-nas-sys.duckdns.org

# または
nslookup -type=TXT _acme-challenge.yoshi-nas-sys.duckdns.org
```

**期待される結果:**
```
_acme-challenge.yoshi-nas-sys.duckdns.org    text = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

### ステップ6: certbotで続行

DNSレコードが反映されたことを確認したら、certbotの画面に戻り、Enterキーを押してください。

```
Press Enter to Continue
```

### ステップ7: 証明書取得の完了

証明書が正常に取得されると、以下のメッセージが表示されます：

```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/yoshi-nas-sys.duckdns.org/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/yoshi-nas-sys.duckdns.org/privkey.pem
```

---

## 🔧 トラブルシューティング

### TXTレコードが反映されない

**確認事項:**
1. DuckDNSでTXTレコードが正しく追加されているか確認
2. DNS反映に時間がかかる場合があります（最大10分程度）
3. 別のDNSサーバーから確認してみる：
   ```bash
   # GoogleのDNSサーバーから確認
   dig @8.8.8.8 TXT _acme-challenge.yoshi-nas-sys.duckdns.org
   ```

### DuckDNSでTXTレコードが見つからない

DuckDNSの基本プランでは、TXTレコードの設定ができない場合があります。

**解決策:**
1. **DuckDNS APIを使用してTXTレコードを設定**
   ```bash
   # DuckDNSのトークンを取得（ダッシュボードで確認）
   # ドメイン名とトークンを使用してTXTレコードを設定
   curl "https://www.duckdns.org/update?domains=yoshi-nas-sys&token=your-token&txt=acme-challenge-value"
   ```

2. **別のDNSプロバイダーを使用**
   - Cloudflare（無料）
   - AWS Route 53
   - Google Cloud DNS

### certbotがタイムアウトする

**対処法:**
- DNSレコードの反映を確認してからEnterを押す
- 最大10分程度待ってから再試行

---

## 🔄 証明書の自動更新

DNS-01チャレンジの場合、自動更新も手動でTXTレコードを追加する必要があります。

### 手動更新

```bash
# 証明書の手動更新
sudo certbot renew --manual --preferred-challenges dns
```

### 自動更新スクリプト（推奨）

DuckDNS APIを使用して自動更新スクリプトを作成できます：

```bash
# スクリプトを作成
sudo nano /usr/local/bin/certbot-renew-dns.sh
```

```bash
#!/bin/bash
# DuckDNS TXTレコード更新スクリプト（certbot用）

DOMAIN="yoshi-nas-sys"
TOKEN="your-duckdns-token"

# 証明書更新（DNS-01チャレンジ）
certbot renew --manual --preferred-challenges dns --manual-auth-hook /usr/local/bin/duckdns-txt-update.sh
```

---

## 📝 チェックリスト

- [ ] certbotがインストール済み
- [ ] DNS-01チャレンジで証明書取得開始
- [ ] certbotからTXTレコードの値を取得
- [ ] DuckDNSでTXTレコードを追加
- [ ] DNSレコードの反映を確認
- [ ] certbotで続行して証明書取得完了
- [ ] 証明書の場所を確認

---

## 🎯 次のステップ

証明書取得が完了したら：

1. **nginx設定ファイルの作成**
   - `docs/deployment/HTTPS_SETUP_GUIDE.md` の「ステップ4: nginxでHTTPS設定」を参照

2. **証明書の場所**
   - `/etc/letsencrypt/live/yoshi-nas-sys.duckdns.org/fullchain.pem`
   - `/etc/letsencrypt/live/yoshi-nas-sys.duckdns.org/privkey.pem`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27  
**作成者**: AI Assistant


