# 🌐 Nginx Proxy Manager - 全サービス外部アクセス設定ガイド

**作成日**: 2025-11-02  
**対象**: すべてのサービスをNginx Proxy Manager経由で外部アクセス可能にする

---

## 📋 現在の状況

- ✅ **nas-dashboard**: Nginx Proxy Manager経由で外部アクセス可能
  - `https://yoshi-nas-sys.duckdns.org:8443`
- ❌ **その他のサービス**: 外部からアクセス不可
  - amazon-analytics
  - document-automation
  - nas-dashboard-monitoring
  - meeting-minutes-byc
  - youtube-to-notion

---

## 🎯 目標

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

## 🚀 設定手順

### ステップ1: Nginx Proxy ManagerのWeb UIにアクセス

```bash
# 内部ネットワークからアクセス
http://192.168.68.110:8181
```

---

### ステップ2: 既存のProxy Hostを確認

1. **「Proxy Hosts」タブを開く**
2. **既存の設定（yoshi-nas-sys.duckdns.org）を確認**

---

### ステップ3: 各サービスをProxy Hostとして追加

#### 3-1. amazon-analytics

1. **「Add Proxy Host」をクリック**

2. **「Details」タブ**:
   - **Domain Names**: `yoshi-nas-sys.duckdns.org`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `8001`
   - **Cache Assets**: ✅（オプション）
   - **Block Common Exploits**: ✅（推奨）
   - **Websockets Support**: ⚠️（必要に応じて）

3. **「Custom Locations」タブ**:
   - **「Add Location」をクリック**
   - **Define location**: `/analytics`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `8001`
   - **Websockets Support**: ⚠️（必要に応じて）

4. **「SSL」タブ**:
   - **SSL Certificate**: 既存のLet's Encrypt証明書を選択
   - **Force SSL**: ✅（推奨）

5. **「Advanced」タブ**:
   - セキュリティヘッダーの設定（オプション）

6. **「Save」をクリック**

---

#### 3-2. document-automation

1. **「Add Proxy Host」をクリック**（または既存のProxy Hostを編集）

2. **「Custom Locations」タブ**で追加:
   - **Define location**: `/documents`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `8080`
   - **Websockets Support**: ⚠️（必要に応じて）

3. **「Save」をクリック**

---

#### 3-3. nas-dashboard-monitoring

1. **「Custom Locations」タブ**で追加:
   - **Define location**: `/monitoring`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `3002`
   - **Websockets Support**: ✅（必須 - WebSocketを使用）

2. **「Save」をクリック**

---

#### 3-4. meeting-minutes-byc

1. **「Custom Locations」タブ**で追加:
   - **Define location**: `/meetings`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `5002`
   - **Websockets Support**: ⚠️（必要に応じて）

2. **「Save」をクリック**

---

#### 3-5. youtube-to-notion

1. **「Custom Locations」タブ**で追加:
   - **Define location**: `/youtube`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `8111`
   - **Websockets Support**: ⚠️（必要に応じて）

2. **「Save」をクリック**

---

## 📋 設定一覧表

| サービス | Location | Forward Host/IP | Forward Port | WebSocket |
|---------|----------|----------------|-------------|-----------|
| nas-dashboard | `/`（ルート） | 192.168.68.110 | 9001 | ⚠️ |
| amazon-analytics | `/analytics` | 192.168.68.110 | 8001 | ⚠️ |
| document-automation | `/documents` | 192.168.68.110 | 8080 | ⚠️ |
| nas-dashboard-monitoring | `/monitoring` | 192.168.68.110 | 3002 | ✅ |
| meeting-minutes-byc | `/meetings` | 192.168.68.110 | 5002 | ⚠️ |
| youtube-to-notion | `/youtube` | 192.168.68.110 | 8111 | ⚠️ |

---

## ✅ 設定後のアクセスURL

すべてのサービスが以下のようにアクセス可能になります：

```
https://yoshi-nas-sys.duckdns.org:8443/             → nas-dashboard
https://yoshi-nas-sys.duckdns.org:8443/analytics    → amazon-analytics
https://yoshi-nas-sys.duckdns.org:8443/documents    → document-automation
https://yoshi-nas-sys.duckdns.org:8443/monitoring   → nas-dashboard-monitoring
https://yoshi-nas-sys.duckdns.org:8443/meetings     → meeting-minutes-byc
https://yoshi-nas-sys.duckdns.org:8443/youtube      → youtube-to-notion
```

---

## 🔍 設定後の確認

### ステップ1: 各サービスへのアクセステスト

```bash
# ローカルからテスト（内部ネットワーク）
curl -I -k https://yoshi-nas-sys.duckdns.org:8443/analytics
curl -I -k https://yoshi-nas-sys.duckdns.org:8443/documents
curl -I -k https://yoshi-nas-sys.duckdns.org:8443/monitoring
curl -I -k https://yoshi-nas-sys.duckdns.org:8443/meetings
curl -I -k https://yoshi-nas-sys.duckdns.org:8443/youtube
```

### ステップ2: ブラウザで確認

1. **外部からアクセス**（モバイルデータ通信など）:
   - `https://yoshi-nas-sys.duckdns.org:8443/analytics`
   - `https://yoshi-nas-sys.duckdns.org:8443/documents`
   - など

2. **各サービスが正常に表示されることを確認**

---

## ⚠️ 注意事項

### アプリケーション側の設定が必要な場合

一部のサービスは、サブパス（`/analytics`など）でアクセスする場合、アプリケーション側の設定が必要になる可能性があります。

#### 確認すべき項目

1. **Base URL設定**: アプリケーションが相対パスを使用しているか
2. **リバースプロキシ対応**: サブパスでのアクセスに対応しているか
3. **静的ファイルのパス**: CSS、JavaScriptなどのパスが正しいか

---

## 🔧 トラブルシューティング

### 404エラーが発生する場合

**原因**: アプリケーションがサブパスでのアクセスに対応していない

**対処法**:
1. アプリケーションの設定でBase URLを設定
2. または、Nginx Proxy Managerの設定で`Rewrite`機能を使用

### 静的ファイルが読み込めない場合

**原因**: CSSやJavaScriptのパスが正しくない

**対処法**:
1. アプリケーションの設定でBase URLを設定
2. または、Nginx Proxy Managerの「Advanced」タブでリライトルールを設定

### WebSocketが動作しない場合

**原因**: WebSocket Supportが有効になっていない

**対処法**:
1. Nginx Proxy Managerの設定で「Websockets Support」を有効化
2. サービスがWebSocketを使用している場合、必ず有効にする

---

## 📝 設定例（詳細）

### amazon-analyticsの設定例

**「Custom Locations」タブ**:
```
Define location: /analytics
Scheme: http
Forward Hostname/IP: 192.168.68.110
Forward Port: 8001
Websockets Support: ☐（このサービスがWebSocketを使用しない場合）
```

**「Advanced」タブ**（オプション）:
```nginx
# リバースプロキシ設定
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;

# Base URLのリライト（必要に応じて）
rewrite ^/analytics/(.*)$ /$1 break;
```

---

## ✅ チェックリスト

設定が完了したら、以下を確認してください：

- [ ] Nginx Proxy Managerで各サービスをProxy Hostとして追加
- [ ] SSL証明書が正しく設定されている
- [ ] 各サービスがHTTPS経由でアクセス可能
- [ ] 静的ファイルが正しく読み込まれる
- [ ] WebSocketが動作する（必要なサービス）
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

