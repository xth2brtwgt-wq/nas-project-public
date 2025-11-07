# 🔄 Nginx Proxy Manager - Proxy Host再作成ガイド

**作成日**: 2025-11-02  
**対象**: Proxy Hostを再作成して設定を正しく反映する

---

## 📋 問題

設定は正しく見えるが、実際にアクセスするとSSLエラーが発生し、ページが表示されない。

**原因**: Nginx設定ファイルが正しく生成されていない可能性があります。

---

## 🔧 解決方法: Proxy Hostを再作成

### ステップ1: 既存のProxy Hostを削除

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hostsタブを開く**

3. **`yoshi-nas-sys.duckdns.org`の設定を見つける**

4. **右側のメニュー（⋮）をクリック**

5. **「Delete」をクリックして削除**

---

### ステップ2: 新しいProxy Hostを作成

1. **「Add Proxy Host」をクリック**

2. **「Details」タブで設定**:
   - **Domain Names**: `yoshi-nas-sys.duckdns.org`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `9001`
   - **Cache Assets**: ✅（オン）
   - **Block Common Exploits**: ✅（オン）
   - **Websockets Support**: ✅（オン）

3. **「SSL」タブで設定**:
   - **SSL Certificate**: `yoshi-nas-sys-duckdns-org`を選択
   - **Force SSL**: ✅（オン）
   - **HTTP/2 Support**: ✅（オン）
   - **HSTS Enabled**: ✅（オン）
   - **HSTS Subdomains**: ✅（オン）

4. **「Custom Locations」タブで設定**:
   - 各Locationを追加（後述の手順参照）

5. **「Save」をクリック**

---

### ステップ3: Custom Locationsを追加

#### 3-1. `/analytics` を追加

1. **「Add Location」をクリック**
2. **設定**:
   - Define location: `/analytics`
   - Scheme: `http`
   - Forward Hostname/IP: `192.168.68.110`
   - Forward Port: `8001`
3. **「Save」をクリック**

#### 3-2. `/documents` を追加

1. **「Add Location」をクリック**
2. **設定**:
   - Define location: `/documents`
   - Scheme: `http`
   - Forward Hostname/IP: `192.168.68.110`
   - Forward Port: `8080`
3. **「Save」をクリック**

#### 3-3. `/monitoring` を追加（WebSocket設定あり）

1. **「Add Location」をクリック**
2. **基本設定**:
   - Define location: `/monitoring`
   - Scheme: `http`
   - Forward Hostname/IP: `192.168.68.110`
   - Forward Port: `3002`
3. **歯車アイコン（⚙️）をクリック**
4. **Custom Nginx configuration**に以下を記述:
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```
5. **「Save」をクリック**

#### 3-4. `/meetings` を追加（WebSocket設定あり）

1. **「Add Location」をクリック**
2. **基本設定**:
   - Define location: `/meetings`
   - Scheme: `http`
   - Forward Hostname/IP: `192.168.68.110`
   - Forward Port: `5002`
3. **歯車アイコン（⚙️）をクリック**
4. **Custom Nginx configuration**に以下を記述:
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```
5. **「Save」をクリック**

#### 3-5. `/youtube` を追加（WebSocket設定あり）

1. **「Add Location」をクリック**
2. **基本設定**:
   - Define location: `/youtube`
   - Scheme: `http`
   - Forward Hostname/IP: `192.168.68.110`
   - Forward Port: `8111`
3. **歯車アイコン（⚙️）をクリック**
4. **Custom Nginx configuration**に以下を記述:
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```
5. **「Save」をクリック**

---

### ステップ4: 最終設定を保存

1. **すべてのCustom Locationsを追加したら、「Details」タブに戻る**

2. **「SSL」タブを確認**:
   - SSL Certificate: `yoshi-nas-sys-duckdns-org`が選択されている
   - Force SSL: ✅オン
   - HTTP/2 Support: ✅オン
   - HSTS Enabled: ✅オン
   - HSTS Subdomains: ✅オン

3. **「Save」をクリックして最終保存**

---

## ✅ 確認方法

### 設定ファイルの生成確認

再作成後、Nginx設定ファイルが生成されているか確認：

```bash
docker exec nginx-proxy-manager ls -la /data/nginx/proxy_host/
```

**期待される結果**: `.conf`ファイルが表示される

### 接続テスト

```bash
# 内部ネットワークからテスト
curl -I -k https://yoshi-nas-sys.duckdns.org:8443/

# またはブラウザでアクセス
# https://yoshi-nas-sys.duckdns.org:8443/
```

---

## 📝 注意事項

### 設定の順序

1. **Detailsタブ**: 基本設定を入力
2. **SSLタブ**: 証明書を選択
3. **Custom Locationsタブ**: 各Locationを追加
4. **最終保存**: すべての設定を確認して「Save」をクリック

### Custom Locationsの追加順序

各Locationを1つずつ追加して「Save」をクリックするのではなく、すべてのLocationを追加してから最後に「Save」をクリックしてもOKです。

---

## 🔍 トラブルシューティング

### 設定ファイルが生成されない場合

**対処法**:
1. Proxy Hostの設定を再度確認
2. 「Save」を再度クリック
3. Nginx Proxy Managerコンテナを再起動:
   ```bash
   docker restart nginx-proxy-manager
   ```

### SSL証明書が表示されない場合

**対処法**:
1. 「SSL Certificates」タブで証明書が存在することを確認
2. 存在しない場合、証明書を取得またはインポート

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

