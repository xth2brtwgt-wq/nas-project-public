# 🚀 Nginx Proxy Manager - 全サービス外部アクセス設定（ステップバイステップ）

**作成日**: 2025-11-02  
**対象**: すべてのサービスをNginx Proxy Manager経由で外部アクセス可能にする

---

## 📋 設定前の確認

### 現在の状態

- ✅ **nas-dashboard**: Nginx Proxy Manager経由で外部アクセス可能
  - `https://yoshi-nas-sys.duckdns.org:8443`
- ❌ **その他のサービス**: 外部からアクセス不可

### 目標

すべてのサービスをNginx Proxy Manager経由で外部からHTTPSでアクセス可能にする。

**アクセスURL（完成後）**:
```
https://yoshi-nas-sys.duckdns.org:8443/             → nas-dashboard
https://yoshi-nas-sys.duckdns.org:8443/analytics    → amazon-analytics
https://yoshi-nas-sys.duckdns.org:8443/documents    → document-automation
https://yoshi-nas-sys.duckdns.org:8443/monitoring   → nas-dashboard-monitoring
https://yoshi-nas-sys.duckdns.org:8443/meetings     → meeting-minutes-byc
https://yoshi-nas-sys.duckdns.org:8443/youtube      → youtube-to-notion
```

---

## 🎯 設定手順

### ステップ1: Nginx Proxy ManagerのWeb UIにアクセス

1. ブラウザで以下のURLにアクセス:
   ```
   http://192.168.68.110:8181
   ```

2. Nginx Proxy Managerの管理画面が表示される

---

### ステップ2: 既存のProxy Hostを編集

1. **「Proxy Hosts」タブをクリック**

2. **`yoshi-nas-sys.duckdns.org`** の設定を見つける

3. **編集ボタン（✏️）をクリック**して設定を開く

---

### ステップ3: Custom Locationsタブに移動

1. **「Custom Locations」タブをクリック**

2. 既存の設定（nas-dashboardの`/`）が表示される

3. **「Add Location」ボタンをクリック**して、各サービスを追加

---

### ステップ4: 各サービスを追加

#### 4-1. amazon-analytics を追加

1. **「Add Location」をクリック**

2. **設定項目**:
   - **Define location**: `/analytics`
   - **Scheme**: `http`（ドロップダウンから選択）
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `8001`
   - **Websockets Support**: ☐（オフ）
   - **Access List**: デフォルト（変更不要）

3. **「Save」をクリック**

---

#### 4-2. document-automation を追加

1. **「Add Location」をクリック**

2. **設定項目**:
   - **Define location**: `/documents`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `8080`
   - **Websockets Support**: ☐（オフ）

3. **「Save」をクリック**

---

#### 4-3. nas-dashboard-monitoring を追加

1. **「Add Location」をクリック**

2. **基本設定項目**:
   - **Define location**: `/monitoring`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `3002`

3. **WebSocket設定（重要）**:
   - 右側の**歯車アイコン（⚙️）**をクリックして詳細設定を開く
   - **「Custom Nginx configuration」テキストエリア**に以下を記述:

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

   - ⚠️ **重要: nas-dashboard-monitoringはWebSocketを使用するため、この設定が必要**

4. **「Save」をクリック**

---

#### 4-4. meeting-minutes-byc を追加

1. **「Add Location」をクリック**

2. **基本設定項目**:
   - **Define location**: `/meetings`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `5002`

3. **WebSocket設定（重要）**:
   - 右側の**歯車アイコン（⚙️）**をクリックして詳細設定を開く
   - **「Custom Nginx configuration」テキストエリア**に以下を記述:

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

   - ⚠️ **重要: meeting-minutes-bycはSocket.IOを使用するため、この設定が必要**

4. **「Save」をクリック**

---

#### 4-5. youtube-to-notion を追加

1. **「Add Location」をクリック**

2. **基本設定項目**:
   - **Define location**: `/youtube`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `8111`

3. **WebSocket設定（重要）**:
   - 右側の**歯車アイコン（⚙️）**をクリックして詳細設定を開く
   - **「Custom Nginx configuration」テキストエリア**に以下を記述:

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

   - ⚠️ **重要: youtube-to-notionはSocket.IOを使用するため、この設定が必要**

4. **「Save」をクリック**

---

### ステップ5: メイン設定を保存

1. すべてのCustom Locationsを追加したら、**「Details」タブ**に戻る

2. **「SSL」タブ**を確認:
   - **SSL Certificate**: Let's Encrypt証明書が選択されている
   - **Force SSL**: ✅（オン）← **推奨**

3. **「Save」をクリック**して、すべての設定を保存

---

## ✅ 設定後の確認

### ステップ1: 各サービスへのアクセステスト

各サービスが正しくアクセスできるか確認します:

```bash
# ローカルからテスト（内部ネットワーク）
curl -I -k https://yoshi-nas-sys.duckdns.org:8443/analytics
curl -I -k https://yoshi-nas-sys.duckdns.org:8443/documents
curl -I -k https://yoshi-nas-sys.duckdns.org:8443/monitoring
curl -I -k https://yoshi-nas-sys.duckdns.org:8443/meetings
curl -I -k https://yoshi-nas-sys.duckdns.org:8443/youtube
```

**期待される結果**:
- HTTP 200 OK または HTTP 302 Found（リダイレクト）
- HTTP 404 Not Found の場合は、アプリケーション側の設定が必要

---

### ステップ2: ブラウザで確認

1. **外部からアクセス**（モバイルデータ通信など）:
   - `https://yoshi-nas-sys.duckdns.org:8443/analytics`
   - `https://yoshi-nas-sys.duckdns.org:8443/documents`
   - `https://yoshi-nas-sys.duckdns.org:8443/monitoring`
   - `https://yoshi-nas-sys.duckdns.org:8443/meetings`
   - `https://yoshi-nas-sys.duckdns.org:8443/youtube`

2. **各サービスが正常に表示されることを確認**

---

## 📋 設定一覧表

| サービス | Location | Forward Host/IP | Forward Port | WebSocket |
|---------|----------|----------------|-------------|-----------|
| nas-dashboard | `/`（ルート） | 192.168.68.110 | 9001 | ❌ 不要 |
| amazon-analytics | `/analytics` | 192.168.68.110 | 8001 | ❌ 不要 |
| document-automation | `/documents` | 192.168.68.110 | 8080 | ❌ 不要 |
| nas-dashboard-monitoring | `/monitoring` | 192.168.68.110 | 3002 | ✅ **必須** |
| meeting-minutes-byc | `/meetings` | 192.168.68.110 | 5002 | ✅ **必須**（Socket.IO） |
| youtube-to-notion | `/youtube` | 192.168.68.110 | 8111 | ✅ **必須**（Socket.IO） |

---

## ⚠️ 注意事項

### アプリケーション側の設定が必要な場合

一部のサービスは、サブパス（`/analytics`など）でアクセスする場合、アプリケーション側の設定が必要になる可能性があります。

#### 確認すべき項目

1. **Base URL設定**: アプリケーションが相対パスを使用しているか
2. **リバースプロキシ対応**: サブパスでのアクセスに対応しているか
3. **静的ファイルのパス**: CSS、JavaScriptなどのパスが正しいか

#### 問題が発生した場合

- **404エラー**: アプリケーションの設定でBase URLを設定
- **静的ファイルが読み込めない**: Nginx Proxy Managerの「Advanced」タブでリライトルールを設定
- **WebSocketが動作しない**: 「Websockets Support」をオンにする

---

## 🔧 トラブルシューティング

### 404エラーが発生する場合

**原因**: アプリケーションがサブパスでのアクセスに対応していない

**対処法**:
1. アプリケーションの設定でBase URLを設定
2. または、Nginx Proxy Managerの「Advanced」タブでリライトルールを設定

### 静的ファイルが読み込めない場合

**原因**: CSSやJavaScriptのパスが正しくない

**対処法**:
1. アプリケーションの設定でBase URLを設定
2. または、Nginx Proxy Managerの「Advanced」タブでリライトルールを設定

### WebSocketが動作しない場合

**原因**: WebSocket Supportが有効になっていない

**対処法**:
1. Custom Locationsの各Locationの**歯車アイコン（⚙️）**をクリックして詳細設定を確認
2. 詳細設定に「Websockets Support」があれば有効化
3. 詳細設定にない場合、「Advanced」タブで以下の設定を追加:
   ```nginx
   proxy_set_header Upgrade $http_upgrade;
   proxy_set_header Connection "upgrade";
   ```
4. サービスがWebSocketを使用している場合、必ず有効にする（特にnas-dashboard-monitoring）

---

## ✅ チェックリスト

設定が完了したら、以下を確認してください：

- [ ] Nginx Proxy Managerで各サービスをCustom Locationとして追加
- [ ] SSL証明書が正しく設定されている
- [ ] 各サービスがHTTPS経由でアクセス可能
- [ ] 静的ファイルが正しく読み込まれる
- [ ] WebSocketが動作する（nas-dashboard-monitoring）
- [ ] 外部からアクセステスト成功

---

## 📚 参考資料

- [Nginx Proxy Manager公式ドキュメント](https://nginxproxymanager.com/)
- [リバースプロキシ設定](EXTERNAL_ACCESS_GUIDE.md)
- [セキュリティ対策ガイド](EXTERNAL_ACCESS_SECURITY.md)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

