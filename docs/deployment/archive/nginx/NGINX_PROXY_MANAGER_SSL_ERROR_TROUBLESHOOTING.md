# 🔒 Nginx Proxy Manager - SSL接続エラー トラブルシューティング

**作成日**: 2025-11-02  
**対象**: SSL証明書の設定エラーによる接続失敗の解決

---

## 📋 問題

ブラウザで以下のエラーが表示される：
- "サーバ"yoshi-nas-sys.duckdns.org"にセキュリティ保護された接続を確立できないため、ページ"https://yoshi-nas-sys.duckdns.org:8443/..."を開けません。"

---

## 🔍 原因の確認

### 可能性のある原因

1. **SSL証明書が設定されていない**
2. **SSL証明書が無効または期限切れ**
3. **Proxy HostのSSLタブの設定が正しくない**
4. **Nginx Proxy ManagerのSSL証明書の設定が正しくない**

---

## 🔧 解決方法

### ステップ1: Proxy HostのSSL設定を確認

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hostsタブを開く**

3. **`yoshi-nas-sys.duckdns.org`の設定を開く**

4. **「SSL」タブをクリック**

5. **SSL証明書の設定を確認**:
   - **SSL Certificate**: Let's Encrypt証明書が選択されているか
   - **Force SSL**: ✅（オン）になっているか
   - **HTTP/2 Support**: ✅（オン）推奨

---

### ステップ2: SSL証明書が選択されているか確認

**SSL Certificateが「None」または空欄の場合**:

1. **「SSL Certificate」ドロップダウンをクリック**
2. **Let's Encrypt証明書を選択**
   - 例: `yoshi-nas-sys.duckdns.org` または `Let's Encrypt`

3. **「Save」をクリック**

---

### ステップ3: SSL証明書が存在しない場合

SSL証明書が存在しない場合、証明書を取得する必要があります。

#### 方法1: Nginx Proxy Managerから取得（推奨）

1. **「SSL」タブを開く**
2. **「Request a new SSL Certificate」ボタンをクリック**
3. **設定**:
   - **Domain Names**: `yoshi-nas-sys.duckdns.org`
   - **Email Address for Let's Encrypt**: メールアドレスを入力
   - **I Agree to the Let's Encrypt Terms of Service**: ✅チェック
   - **Use a DNS Challenge**: 必要に応じて設定

4. **「Save」をクリック**

5. **証明書の取得完了を待つ**（数分かかる場合があります）

#### 方法2: acme.shで取得した証明書をインポート

以前`acme.sh`で取得した証明書を使用する場合：

1. **「SSL Certificates」タブを開く**
2. **「Add SSL Certificate」をクリック**
3. **「Let's Encrypt」を選択**
4. **証明書情報を入力**
5. **「Save」をクリック**

---

### ステップ4: 設定を保存してNginxを再読み込み

1. **すべての設定を確認**
2. **「Save」をクリック**
3. **Nginx設定が再読み込みされることを確認**

---

## ✅ 確認方法

### SSL証明書の設定確認

1. **「SSL」タブを開く**
2. **「SSL Certificate」にLet's Encrypt証明書が選択されていることを確認**
3. **「Force SSL」がオンになっていることを確認**

### 接続テスト

```bash
# 内部ネットワークからテスト
curl -I -k https://yoshi-nas-sys.duckdns.org:8443/analytics

# 証明書の詳細を確認
openssl s_client -connect yoshi-nas-sys.duckdns.org:8443 -servername yoshi-nas-sys.duckdns.org < /dev/null 2>&1 | grep -A 5 "Certificate chain"
```

---

## ⚠️ 注意事項

### 証明書の有効期限

Let's Encrypt証明書は90日間有効です。自動更新が設定されていることを確認してください。

### 証明書の更新

以前設定した`renew-cert-and-reload.sh`スクリプトがcronで実行されていることを確認：

```bash
crontab -l | grep renew-cert-and-reload
```

---

## 🔍 トラブルシューティング

### SSL証明書が表示されない場合

**原因**: 証明書が取得されていない、またはインポートされていない

**対処法**:
1. 「SSL Certificates」タブで証明書一覧を確認
2. 証明書が存在しない場合、取得またはインポート
3. Proxy HostのSSLタブで証明書を選択

### SSL証明書が無効と表示される場合

**原因**: 証明書が期限切れ、またはドメイン名が一致しない

**対処法**:
1. 証明書の有効期限を確認
2. 証明書のドメイン名が`yoshi-nas-sys.duckdns.org`と一致していることを確認
3. 必要に応じて証明書を再取得

### 接続エラーが続く場合

**原因**: ブラウザのキャッシュ、または証明書の設定が反映されていない

**対処法**:
1. ブラウザのキャッシュをクリア
2. シークレットモードでアクセスしてみる
3. Nginx Proxy Managerコンテナを再起動:
   ```bash
   docker restart nginx-proxy-manager
   ```

---

## 📝 まとめ

SSL接続エラーの主な原因：

1. **SSL証明書が設定されていない** → SSLタブで証明書を選択
2. **証明書が無効** → 証明書を再取得またはインポート
3. **設定が反映されていない** → 設定を保存してNginxを再読み込み

**解決手順**:
1. Proxy HostのSSLタブを開く
2. SSL証明書が選択されていることを確認
3. 選択されていない場合、証明書を選択
4. 「Force SSL」をオンにする
5. 設定を保存

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

