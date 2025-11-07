# 🔄 Nginx Proxy Manager - Custom Locations再試行ガイド

**作成日**: 2025-11-02  
**目的**: 同じドメイン名で複数のサービスを提供するためにCustom Locationsを再試行

---

## ⚠️ 問題

「yoshi-nas-sys.duckdns.org is already in use」エラーが発生

**原因**: Nginx Proxy Managerでは、同じドメイン名を複数のProxy Hostで使用することはできません。

**解決方法**: 既存のProxy HostにCustom Locationsを追加します。

---

## 🎯 アクセスURL（完成後）

```
https://yoshi-nas-sys.duckdns.org:8443/              → nas-dashboard
https://yoshi-nas-sys.duckdns.org:8443/analytics     → amazon-analytics
https://yoshi-nas-sys.duckdns.org:8443/documents     → document-automation
https://yoshi-nas-sys.duckdns.org:8443/monitoring    → nas-dashboard-monitoring
https://yoshi-nas-sys.duckdns.org:8443/meetings       → meeting-minutes-byc
https://yoshi-nas-sys.duckdns.org:8443/youtube        → youtube-to-notion
```

すべて同じドメイン名とポート番号（8443）を使用します。

---

## 🚀 設定手順

### ステップ1: 既存のProxy Hostを編集

1. **Nginx Proxy ManagerのWeb UIにアクセス**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブを開く**

3. **`yoshi-nas-sys.duckdns.org`のProxy Hostを編集**（歯車アイコンをクリック）

4. **現在の設定を確認**:
   - Domain Names: `yoshi-nas-sys.duckdns.org` ✅
   - Forward Hostname/IP: `192.168.68.110` ✅
   - Forward Port: `9001`（nas-dashboard）✅
   - Access List: `nas-dashboard-auth` ✅

---

### ステップ2: Custom Locationsタブに移動

1. **「Custom Locations」タブをクリック**

2. **既存の設定を確認**:
   - `/`（ルート）→ nas-dashboard（既存）

3. **各サービスを追加**

---

### ステップ3: amazon-analyticsを追加

1. **「Add Location」をクリック**

2. **設定項目**:
   - **Define location**: `/analytics`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `8001`
   - **Cache Assets**: ✅（オプション）
   - **Block Common Exploits**: ✅（推奨）
   - **Websockets Support**: ❌（不要）

3. **「Custom Nginx configuration」は空欄のまま**

4. **「Save」をクリック**（Locationの保存）

---

### ステップ4: document-automationを追加

1. **「Add Location」をクリック**

2. **設定項目**:
   - **Define location**: `/documents`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `8080`
   - **Cache Assets**: ✅
   - **Block Common Exploits**: ✅
   - **Websockets Support**: ❌

3. **「Save」をクリック**

---

### ステップ5: nas-dashboard-monitoringを追加（WebSocket設定あり）

1. **「Add Location」をクリック**

2. **設定項目**:
   - **Define location**: `/monitoring`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `3002`
   - **Cache Assets**: ✅
   - **Block Common Exploits**: ✅
   - **Websockets Support**: ✅ **（重要: オンにする）**

3. **「Custom Nginx configuration」に以下を追加**:

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

4. **「Save」をクリック**

---

### ステップ6: meeting-minutes-bycを追加（WebSocket設定あり）

1. **「Add Location」をクリック**

2. **設定項目**:
   - **Define location**: `/meetings`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `5002`
   - **Cache Assets**: ✅
   - **Block Common Exploits**: ✅
   - **Websockets Support**: ✅ **（重要: オンにする）**

3. **「Custom Nginx configuration」に以下を追加**:

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

4. **「Save」をクリック**

---

### ステップ7: youtube-to-notionを追加

1. **「Add Location」をクリック**

2. **設定項目**:
   - **Define location**: `/youtube`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `8111`
   - **Cache Assets**: ✅
   - **Block Common Exploits**: ✅
   - **Websockets Support**: ❌（または必要に応じて✅）

3. **「Save」をクリック**

---

### ステップ8: Proxy Host全体を保存

1. **すべてのCustom Locationsを追加した後**

2. **Proxy Hostの設定画面で「Save」をクリック**（画面下部の緑色の「Save」ボタン）

3. **設定が反映されるまで数秒待つ**

---

## ⚠️ 以前のトラブルについて

以前、Custom Locationsを追加すると設定ファイルが生成されず、アクセスできなくなる問題がありました。

**今回の試行で確認すること**:
1. 各Custom Locationを1つずつ追加して、その都度「Save」をクリック
2. Proxy Host全体を保存する前に、各Locationが正しく表示されているか確認
3. 設定ファイルが生成されているか確認（できれば）

---

## ✅ 動作確認

### 各サービスへのアクセステスト

1. **外部ネットワークからアクセス**（モバイルデータ通信など）

2. **各サービスのURLにアクセス**:
   ```
   https://yoshi-nas-sys.duckdns.org:8443/              → nas-dashboard
   https://yoshi-nas-sys.duckdns.org:8443/analytics     → amazon-analytics
   https://yoshi-nas-sys.duckdns.org:8443/documents     → document-automation
   https://yoshi-nas-sys.duckdns.org:8443/monitoring    → nas-dashboard-monitoring
   https://yoshi-nas-sys.duckdns.org:8443/meetings       → meeting-minutes-byc
   https://yoshi-nas-sys.duckdns.org:8443/youtube        → youtube-to-notion
   ```

3. **認証ダイアログが表示されることを確認**（すべて同じBasic認証）

4. **正しい認証情報でアクセスできることを確認**

---

## 📝 チェックリスト

- [ ] 既存のProxy Hostを編集
- [ ] Custom Locationsタブに移動
- [ ] `/analytics`を追加（amazon-analytics）
- [ ] `/documents`を追加（document-automation）
- [ ] `/monitoring`を追加（nas-dashboard-monitoring、WebSocket設定あり）
- [ ] `/meetings`を追加（meeting-minutes-byc、WebSocket設定あり）
- [ ] `/youtube`を追加（youtube-to-notion）
- [ ] Proxy Host全体を保存
- [ ] 各サービスへのアクセステスト実施

---

## 🧪 トラブルシューティング

### Custom Locationsを追加した後、アクセスできなくなった場合

1. **Custom Locationsを一度すべて削除**
2. **Proxy Hostを保存**
3. **再度、1つずつ追加して確認**

### 設定ファイルが生成されない場合

以前と同じ問題が発生している可能性があります。その場合は、別の方法（各サービスを別々のProxy Hostとして作成）を検討する必要があります。

---

## 📚 参考資料

- [Nginx Proxy Manager - Custom Locations設定まとめ](NGINX_PROXY_MANAGER_CUSTOM_LOCATIONS_SUMMARY.md)
- [Nginx Proxy Manager - WebSocket設定ガイド](NGINX_PROXY_MANAGER_WEBSOCKET_CONFIG.md)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant



