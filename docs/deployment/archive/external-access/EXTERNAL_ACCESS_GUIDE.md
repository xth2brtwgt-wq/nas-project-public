# 🌐 外部アクセス設定ガイド

**作成日**: 2025-01-27  
**対象**: nas-project全プロジェクト

---

## 📋 概要

現在、NAS環境内（192.168.68.110）で動作しているシステムを、インターネット経由でアクセスできるようにするための設定手順です。

---

## 🔍 現在の状況

### 稼働中のサービスとポート

| サービス | 内部ポート | 外部ポート | アクセスURL（ローカル） |
|---------|-----------|-----------|----------------------|
| nas-dashboard | 9000 | 9001 | http://192.168.68.110:9001 |
| amazon-analytics | 8000 | 8001 | http://192.168.68.110:8001 |
| document-automation | 8080 | 8080 | http://192.168.68.110:8080 |
| meeting-minutes-byc | 5000 | 5002 | http://192.168.68.110:5002 |
| nas-dashboard-monitoring (frontend) | 3000 | 3002 | http://192.168.68.110:3002 |
| nas-dashboard-monitoring (backend) | 8000 | 8002 | http://192.168.68.110:8002 |
| youtube-to-notion | 8110 | 8111 | http://192.168.68.110:8111 |

---

## ⚙️ 内部リンクの自動対応

**重要なポイント**: システムは自動的に内部・外部の両方に対応するように設計されています。

### nas-dashboard
リンクは、リクエストのホスト名を使用して動的に生成されます。

- 内部（192.168.68.110）からアクセス → 内部IPのリンクが生成される
- 外部（外部IPやドメイン）からアクセス → 外部ホスト名のリンクが生成される

**環境変数による設定（オプション）**

外部ホスト名を環境変数で設定することも可能です：

```bash
# .env または docker-compose.yml に追加
EXTERNAL_HOST=your-domain.com:9001
# または
EXTERNAL_HOST=123.45.67.89:9001
```

環境変数が設定されている場合は、その値が優先されます。

### nas-dashboard-monitoring
フロントエンドとバックエンドの通信は相対パスを使用しています。

- **API呼び出し**: `/api/...` でnginx経由でバックエンドにアクセス
- **WebSocket**: `/ws` でnginx経由でバックエンドに接続
- **内部・外部のどちらからアクセスしても自動的に動作します**
- **ビルド時の環境変数設定は不要**になりました

---

## 🚀 外部アクセス設定方法

### 方法1: ルーターのポートフォワーディング（推奨）

最も一般的でセキュアな方法です。

#### 1-1. ルーター設定の確認

1. **ルーターの管理画面にアクセス**
   - 通常は `http://192.168.1.1` または `http://192.168.0.1`
   - NASのゲートウェイIPを確認:
     ```bash
     # NASにSSH接続して確認
     ssh -p 23456 AdminUser@192.168.68.110
     ip route | grep default
     ```

2. **ポートフォワーディング設定**
   - 「ポート転送」「ポートマッピング」「仮想サーバー」などのメニューを探す
   - 外部ポート → 内部IP（192.168.68.110）:ポート のマッピングを作成

#### 1-2. 推奨設定例

| サービス | 外部ポート | 内部IP:ポート | プロトコル |
|---------|-----------|-------------|----------|
| nas-dashboard | 9001 | 192.168.68.110:9001 | TCP |
| amazon-analytics | 8001 | 192.168.68.110:8001 | TCP |
| document-automation | 8080 | 192.168.68.110:8080 | TCP |
| meeting-minutes-byc | 5002 | 192.168.68.110:5002 | TCP |
| nas-dashboard-monitoring (frontend) | 3002 | 192.168.68.110:3002 | TCP |
| nas-dashboard-monitoring (backend) | 8002 | 192.168.68.110:8002 | TCP |
| youtube-to-notion | 8111 | 192.168.68.110:8111 | TCP |

#### 1-3. 外部アクセスURL

ルーター設定後、以下の形式でアクセス可能：

```
http://[外部IPアドレス]:[外部ポート]
```

例：
- `http://[外部IP]:9001` → nas-dashboard
- `http://[外部IP]:8001` → amazon-analytics

**外部IPアドレスの確認方法：**
```bash
# ローカルから確認
curl ifconfig.me
# または
curl ipinfo.io/ip
```

---

### 方法2: DDNS（Dynamic DNS）の設定

外部IPが変わっても同じドメインでアクセスできます。

#### 2-1. DDNSサービスの選択

- **No-IP**: https://www.noip.com/（無料プランあり）
- **DuckDNS**: https://www.duckdns.org/（無料）
- **DynDNS**: https://dyn.com/dns/（有料）
- **ルーター内蔵DDNS**: 多くのルーターに内蔵

#### 2-2. ドメイン設定例

```
nas-project.duckdns.org
```

#### 2-3. アクセスURL例

```
http://nas-project.duckdns.org:9001 → nas-dashboard
http://nas-project.duckdns.org:8001 → amazon-analytics
```

---

### 方法3: リバースプロキシ（nginx/Traefik）の設定

複数のサービスを1つのドメインで管理したい場合に推奨。

#### 3-1. nginxリバースプロキシの例

```nginx
server {
    listen 80;
    server_name nas-project.example.com;

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
}
```

---

## 🔒 セキュリティ設定（必須）

外部公開時は、必ず以下のセキュリティ対策を実施してください。

### 1. ファイアウォール設定

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# UFWがインストールされている場合
sudo ufw allow 9001/tcp
sudo ufw allow 8001/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 5002/tcp
sudo ufw allow 3002/tcp
sudo ufw allow 8002/tcp
sudo ufw allow 8111/tcp

# SSHポートは既に開いていることを確認
sudo ufw allow 23456/tcp

# ファイアウォール有効化
sudo ufw enable
sudo ufw status
```

### 2. HTTPS設定（強く推奨）

#### 2-1. Let's Encrypt証明書の取得

```bash
# certbotのインストール（NASがUbuntu/Debianの場合）
sudo apt update
sudo apt install certbot

# 証明書取得
sudo certbot certonly --standalone -d nas-project.example.com
```

#### 2-2. nginxでHTTPS設定

```nginx
server {
    listen 443 ssl;
    server_name nas-project.example.com;

    ssl_certificate /etc/letsencrypt/live/nas-project.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nas-project.example.com/privkey.pem;

    # セキュリティヘッダー
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # リバースプロキシ設定
    location / {
        proxy_pass http://192.168.68.110:9001;
        # ... プロキシ設定 ...
    }
}

# HTTP → HTTPSリダイレクト
server {
    listen 80;
    server_name nas-project.example.com;
    return 301 https://$server_name$request_uri;
}
```

### 3. 認証の追加（推奨）

#### 3-1. Basic認証（nginx）

```bash
# htpasswdのインストール
sudo apt install apache2-utils

# パスワードファイル作成
sudo htpasswd -c /etc/nginx/.htpasswd username

# nginx設定
location / {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://192.168.68.110:9001;
}
```

#### 3-2. アプリケーションレベルでの認証

各アプリケーションにログイン機能を実装することを推奨します。

### 4. アクセス制限（IP制限）

特定のIPアドレスからのみアクセスを許可：

```nginx
# 許可するIPアドレス
allow 123.45.67.89;
allow 98.76.54.32;
deny all;

location / {
    proxy_pass http://192.168.68.110:9001;
}
```

### 5. Fail2banの設定

既にfail2banが設定されている場合は、新しいサービス用のフィルターを追加：

```bash
# fail2ban設定ディレクトリ
cd /etc/fail2ban/filter.d/

# 新しいフィルター作成（例: nas-dashboard）
sudo nano nas-dashboard.conf
```

---

## 📝 チェックリスト

外部公開前の確認事項：

- [ ] ルーターのポートフォワーディング設定完了
- [ ] ファイアウォール設定完了
- [ ] HTTPS証明書取得（推奨）
- [ ] 認証機能の実装（推奨）
- [ ] アクセスログの設定
- [ ] バックアップ設定の確認
- [ ] セキュリティアップデートの適用
- [ ] 外部からアクセステスト実施

---

## 🧪 テスト方法

### 1. ローカルネットワーク内からのテスト

```bash
# 別のPCやスマートフォンから同じWiFiに接続してテスト
curl http://192.168.68.110:9001
```

### 2. 外部からのテスト

```bash
# モバイルデータ通信（WiFi OFF）からテスト
# または
# 外部のサーバーからテスト
curl http://[外部IP]:9001
```

### 3. ポート開放確認

```bash
# 外部からポートスキャン（サービス利用）
# 例: https://www.yougetsignal.com/tools/open-ports/
```

---

## ⚠️ 注意事項

### セキュリティ警告

1. **HTTPは暗号化されていません**
   - パスワードや機密情報が平文で送信されます
   - **必ずHTTPSを使用してください**

2. **パスワードの強度**
   - デフォルトパスワードは使用しない
   - 複雑なパスワードを使用する

3. **定期的な更新**
   - システムと依存関係のセキュリティアップデートを実施
   - 証明書の有効期限を確認

4. **ログ監視**
   - アクセスログを定期的に確認
   - 不正アクセスの兆候がないか監視

5. **不要なポートの公開禁止**
   - 必要最小限のポートのみ開放
   - 使用していないサービスは停止

---

## 🔧 トラブルシューティング

### ポートが開かない

1. **ルーター設定の確認**
   ```bash
   # ポートフォワーディング設定を再確認
   ```

2. **ファイアウォールの確認**
   ```bash
   # NAS上で確認
   sudo ufw status
   sudo iptables -L -n
   ```

3. **サービスが起動しているか確認**
   ```bash
   # コンテナの状態確認
   docker ps
   docker logs [コンテナ名]
   ```

### アクセスできない

1. **外部IPアドレスの確認**
   ```bash
   curl ifconfig.me
   ```

2. **ポートが正しく転送されているか確認**
   ```bash
   # ローカルからテスト
   curl http://192.168.68.110:9001
   ```

3. **ルーターの再起動**
   - 設定変更後、ルーターを再起動してみる

---

## 📚 参考資料

- [nginx リバースプロキシ設定](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [Let's Encrypt 証明書取得](https://letsencrypt.org/)
- [UFW ファイアウォール設定](https://help.ubuntu.com/community/UFW)

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27  
**作成者**: AI Assistant

