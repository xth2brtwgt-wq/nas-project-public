# 🔒 HTTPS設定ガイド（Let's Encrypt + nginx）

**作成日**: 2025-01-27  
**対象**: nas-project全プロジェクト

---

## 📋 概要

このガイドでは、Let's Encryptの無料SSL証明書を使用してHTTPSを設定する手順を説明します。

**前提条件:**
- ドメイン名またはDDNS設定済み（例: `nas-project.duckdns.org`）
- ポート80と443が外部からアクセス可能（証明書取得のため）
- NASにSSH接続可能

---

## 🎯 設定方法の選択

### 方法1: nginxリバースプロキシで全サービスをHTTPS化（推奨）

**メリット:**
- 1つの証明書で全サービスをHTTPS化
- 設定が1箇所で管理しやすい
- セキュリティヘッダーの一元管理

**デメリット:**
- nginxの設置が必要

### 方法2: 各サービス個別にHTTPS設定

**メリット:**
- 各サービスの独立性が高い

**デメリット:**
- 証明書の管理が複雑
- 各サービスの設定変更が必要

**→ このガイドでは方法1（リバースプロキシ）を推奨します**

---

## 🚀 ステップ1: ドメイン/DDNSの準備

### 1-1. ドメイン名の確認

HTTPS設定には、ドメイン名（またはDDNS）が必要です。

**既に設定済みの場合:**
- ドメイン名を確認（例: `nas-project.duckdns.org`）

**未設定の場合:**
1. **DuckDNS** (無料) を使用する場合:
   - https://www.duckdns.org/ にアクセス
   - アカウント作成
   - ドメインを選択（例: `nas-project`）
   - 外部IPアドレスを設定
   - 結果: `nas-project.duckdns.org`

2. **No-IP** (無料プランあり) を使用する場合:
   - https://www.noip.com/ にアクセス
   - アカウント作成
   - ホスト名を作成

### 1-2. ドメインがNASを指しているか確認

```bash
# 外部IPを確認
curl ifconfig.me

# ドメインが外部IPを指しているか確認
nslookup nas-project.duckdns.org
# または
dig nas-project.duckdns.org
```

**重要:** ドメインが外部IPアドレスを正しく指している必要があります。

---

## 🚀 ステップ2: nginxのインストールと基本設定

### 2-1. NASにSSH接続

```bash
ssh -p 23456 AdminUser@192.168.68.110
```

### 2-2. nginxのインストール

```bash
# システム更新
sudo apt update

# nginxのインストール
sudo apt install nginx -y

# nginxの状態確認
sudo systemctl status nginx

# nginxを自動起動に設定
sudo systemctl enable nginx
```

### 2-3. ポート80と443が空いているか確認

```bash
# ポート80を確認
sudo netstat -tulpn | grep :80

# ポート443を確認
sudo netstat -tulpn | grep :443
```

**もしポート80や443が使用されている場合:**
- Dockerコンテナや他のサービスを一時的に停止する必要がある場合があります
- または、別のポートで証明書取得を行う（複雑）

---

## 🚀 ステップ3: Let's Encrypt証明書の取得

### 3-1. certbotのインストール

```bash
# certbotのインストール
sudo apt install certbot python3-certbot-nginx -y
```

### 3-2. 証明書の取得（スタンドアロンモード）

**重要:** 証明書取得中は、nginxやポート80を使用するサービスを停止する必要があります。

```bash
# nginxを停止（証明書取得のため）
sudo systemctl stop nginx

# 証明書を取得（スタンドアロンモード）
# [your-domain] を実際のドメイン名に置き換えてください
sudo certbot certonly --standalone -d [your-domain]

# 例:
sudo certbot certonly --standalone -d nas-project.duckdns.org
```

**実行時の手順:**
1. メールアドレスを入力（証明書の有効期限通知など）
2. 利用規約に同意
3. 証明書取得が完了

### 3-3. 証明書の場所を確認

```bash
# 証明書の場所
ls -la /etc/letsencrypt/live/[your-domain]/

# 確認すべきファイル:
# - fullchain.pem (証明書+中間証明書)
# - privkey.pem (秘密鍵)
```

---

## 🚀 ステップ4: nginxでHTTPS設定

### 4-1. nginx設定ファイルの作成

```bash
# 設定ファイルを作成
sudo nano /etc/nginx/sites-available/nas-project-https
```

### 4-2. 設定内容（例: nas-dashboard）

以下の内容を設定ファイルに記述します（`[your-domain]` を実際のドメイン名に置き換えてください）:

```nginx
# HTTP → HTTPSリダイレクト
server {
    listen 80;
    server_name [your-domain];

    # Let's Encrypt認証用（自動更新で使用）
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # その他はすべてHTTPSにリダイレクト
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS設定（nas-dashboard）
server {
    listen 443 ssl http2;
    server_name [your-domain];

    # SSL証明書の設定
    ssl_certificate /etc/letsencrypt/live/[your-domain]/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/[your-domain]/privkey.pem;

    # SSL設定（セキュリティ強化）
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # セキュリティヘッダー
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # nas-dashboardへのプロキシ
    location / {
        proxy_pass http://192.168.68.110:9001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # タイムアウト設定
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 4-3. 複数のサービスを設定する場合

複数のサービスをサブパスで提供する例:

```nginx
# HTTPS設定（複数サービス）
server {
    listen 443 ssl http2;
    server_name [your-domain];

    # SSL証明書の設定
    ssl_certificate /etc/letsencrypt/live/[your-domain]/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/[your-domain]/privkey.pem;

    # SSL設定
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # セキュリティヘッダー
    add_header Strict-Transport-Security "max-age=31536000" always;

    # nas-dashboard
    location /dashboard/ {
        proxy_pass http://192.168.68.110:9001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # amazon-analytics
    location /analytics/ {
        proxy_pass http://192.168.68.110:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # document-automation
    location /documents/ {
        proxy_pass http://192.168.68.110:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # nas-dashboard-monitoring
    location /monitoring/ {
        proxy_pass http://192.168.68.110:3002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4-4. 設定ファイルを有効化

```bash
# シンボリックリンクを作成（有効化）
sudo ln -s /etc/nginx/sites-available/nas-project-https /etc/nginx/sites-enabled/

# 設定ファイルの構文チェック
sudo nginx -t

# エラーがない場合、nginxを再起動
sudo systemctl restart nginx

# nginxの状態確認
sudo systemctl status nginx
```

---

## 🚀 ステップ5: ルーターのポート転送設定

HTTPSを使用する場合、**ポート443**も転送する必要があります。

### 5-1. ルーター設定

ルーターのポート転送設定に以下を追加:

| 外部ポート | 内部IP:ポート | プロトコル | 用途 |
|-----------|-------------|----------|------|
| 80 | 192.168.68.110:80 | TCP | HTTP（HTTPSリダイレクト用） |
| 443 | 192.168.68.110:443 | TCP | HTTPS |

### 5-2. 既存のポート転送設定

既存のポート転送（9001、8001など）は、以下の2つの選択肢があります:

**選択肢A: ポート転送を維持し、HTTPS経由でもアクセス可能にする**
- nginxで複数のポートを転送
- ルーター設定は変更不要

**選択肢B: HTTPSのみに統一する**
- ルーターのポート転送を443のみに統一
- すべてのサービスをHTTPS経由でアクセス

---

## 🚀 ステップ6: 証明書の自動更新設定

Let's Encryptの証明書は90日間有効です。自動更新を設定します。

### 6-1. certbotの自動更新テスト

```bash
# 自動更新のテスト（実際には更新しない）
sudo certbot renew --dry-run

# 成功したら、自動更新が正常に動作しています
```

### 6-2. 自動更新の確認

certbotは自動的にcronジョブを設定します：

```bash
# cronジョブを確認
sudo crontab -l

# 通常は以下のようなエントリが自動追加されます:
# 0 12 * * * certbot renew --quiet
```

### 6-3. 手動更新（テスト用）

```bash
# 証明書の手動更新
sudo certbot renew

# nginxを再起動して新しい証明書を読み込む
sudo systemctl reload nginx
```

---

## 🧪 テスト方法

### 1. HTTPSアクセステスト

```bash
# ローカルからテスト
curl -I https://[your-domain]

# 証明書の確認
openssl s_client -connect [your-domain]:443 -showcerts
```

### 2. ブラウザで確認

1. `https://[your-domain]` にアクセス
2. ブラウザのアドレスバーに鍵マークが表示されることを確認
3. 証明書情報を確認:
   - ブラウザで鍵マークをクリック
   - 「証明書を表示」を選択
   - 「発行者: Let's Encrypt」を確認

### 3. セキュリティヘッダーの確認

```bash
# セキュリティヘッダーを確認
curl -I https://[your-domain] | grep -i strict-transport
```

---

## ⚠️ トラブルシューティング

### 証明書取得に失敗する場合

**エラー: "Failed to bind to port 80"**
```bash
# ポート80を使用しているプロセスを確認
sudo lsof -i :80

# プロセスを停止してから証明書取得を再試行
```

**エラー: "Domain does not point to this server"**
- ドメインが外部IPアドレスを正しく指しているか確認
- DNS設定の反映に時間がかかる場合がある（数時間）

### nginxが起動しない場合

```bash
# エラーログを確認
sudo tail -50 /var/log/nginx/error.log

# 設定ファイルの構文チェック
sudo nginx -t
```

### HTTPSでアクセスできない場合

```bash
# nginxのエラーログを確認
sudo tail -50 /var/log/nginx/error.log

# ポート443が開いているか確認
sudo netstat -tulpn | grep :443

# ルーターのポート転送設定を確認
```

---

## 📝 チェックリスト

- [ ] ドメイン/DDNS設定完了
- [ ] nginxインストール完了
- [ ] Let's Encrypt証明書取得完了
- [ ] nginx設定ファイル作成完了
- [ ] 設定ファイルを有効化
- [ ] ルーターでポート443を転送設定
- [ ] HTTPSアクセステスト成功
- [ ] 証明書の自動更新テスト成功

---

## 📚 参考資料

- [Let's Encrypt公式サイト](https://letsencrypt.org/)
- [certbot公式ドキュメント](https://certbot.eff.org/)
- [nginx公式ドキュメント](https://nginx.org/en/docs/)

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27  
**作成者**: AI Assistant


