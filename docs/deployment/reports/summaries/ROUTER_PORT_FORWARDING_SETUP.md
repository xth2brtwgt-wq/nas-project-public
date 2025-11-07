# 🔧 ルーター ポート転送設定ガイド

**作成日**: 2025-11-02  
**目的**: 全サービスを外部アクセス可能にするためのルーター設定

---

## 📋 現在の設定状況

現在のポート転送設定（画像確認）:

| サービス名 | 内部IP:ポート | 用途 |
|---------|-------------|------|
| HTTP | 192.168.68.110:8443 | Nginx Proxy Manager（既存） |
| nas-dashboard | 192.168.68.110:9001 | nas-dashboard（直接アクセス用） |
| amazon-analytics | 192.168.68.110:8001 | amazon-analytics（直接アクセス用） |
| document-automation | 192.168.68.110:8080 | document-automation（直接アクセス用） |
| meeting-minutes-byc | 192.168.68.110:5002 | meeting-minutes-byc（直接アクセス用） |
| nas-dashboard-monitoring-f | 192.168.68.110:3002 | nas-dashboard-monitoring（直接アクセス用） |
| nas-dashboard-monitoring-b | 192.168.68.110:8002 | nas-dashboard-monitoring（直接アクセス用） |
| youtube-to-notion | 192.168.68.110:8111 | youtube-to-notion（直接アクセス用） |
| lets-encrypts | 192.168.68.110:80 | Let's Encrypt証明書更新用 |

---

## ✅ 必要な追加設定

### Nginx Proxy Manager経由で外部アクセス可能にする場合

各サービスをNginx Proxy Manager経由でアクセス可能にするため、**以下のポート転送設定を追加**してください：

| サービス | 外部ポート | 内部IP:ポート | プロトコル | 備考 |
|---------|-----------|-------------|----------|------|
| nas-dashboard | 8443 | 192.168.68.110:8443 | TCP | ✅ **既に設定済み** |
| amazon-analytics | 8444 | 192.168.68.110:8444 | TCP | ⚠️ **追加が必要** |
| document-automation | 8445 | 192.168.68.110:8445 | TCP | ⚠️ **追加が必要** |
| nas-dashboard-monitoring | 8446 | 192.168.68.110:8446 | TCP | ⚠️ **追加が必要** |
| meeting-minutes-byc | 8447 | 192.168.68.110:8447 | TCP | ⚠️ **追加が必要** |
| youtube-to-notion | 8448 | 192.168.68.110:8448 | TCP | ⚠️ **追加が必要** |

**重要**: 
- 内部ポート（8444〜8448）は、Nginx Proxy Managerが各サービス用に使用するポートです
- 各サービス自体のポート（8001、8080など）ではありません
- Nginx Proxy Managerで各サービス用のProxy Hostを作成する際に、これらのポートを使用します

---

## 🚀 追加設定手順

### ステップ1: ルーターの管理画面でポート転送設定を追加

1. **ルーターの管理画面を開く**
   - 通常は `http://192.168.1.1` または `http://192.168.0.1`

2. **「ポート転送」「ポートマッピング」「仮想サーバー」などのメニューを開く**

3. **新しいポート転送ルールを追加**（「+」ボタンや「追加」ボタンをクリック）

#### amazon-analytics用（8444）

- **ルール名**: `amazon-analytics-proxy`
- **外部ポート**: `8444`
- **内部IP**: `192.168.68.110`
- **内部ポート**: `8444`
- **プロトコル**: `TCP`（または`TCP/UDP`）

#### document-automation用（8445）

- **ルール名**: `document-automation-proxy`
- **外部ポート**: `8445`
- **内部IP**: `192.168.68.110`
- **内部ポート**: `8445`
- **プロトコル**: `TCP`

#### nas-dashboard-monitoring用（8446）

- **ルール名**: `nas-dashboard-monitoring-proxy`
- **外部ポート**: `8446`
- **内部IP**: `192.168.68.110`
- **内部ポート**: `8446`
- **プロトコル**: `TCP`

#### meeting-minutes-byc用（8447）

- **ルール名**: `meeting-minutes-byc-proxy`
- **外部ポート**: `8447`
- **内部IP**: `192.168.68.110`
- **内部ポート**: `8447`
- **プロトコル**: `TCP`

#### youtube-to-notion用（8448）

- **ルール名**: `youtube-to-notion-proxy`
- **外部ポート**: `8448`
- **内部IP**: `192.168.68.110`
- **内部ポート**: `8448`
- **プロトコル**: `TCP`

4. **各ルールを保存**

---

## ⚠️ 現在の設定について

### 既存のポート転送設定は削除しないでください

現在の設定（8001、8080、5002、3002、8111など）は、**内部ネットワークからの直接アクセス用**です。

これらの設定は：
- ✅ **内部ネットワークから直接アクセス**する場合に使用
- ✅ **Nginx Proxy Managerが各サービスに接続**する際に使用

**削除しないでください**。

---

## 📊 設定後の構成

### 外部からのアクセス

```
外部 → ルーター（8444） → Nginx Proxy Manager（8444） → 各サービス（8001等）
```

### 内部ネットワークからのアクセス

```
内部 → 直接各サービス（8001、8080等）
```

---

## ✅ 設定確認チェックリスト

- [ ] ルーターのポート転送設定を追加（8444〜8448）
- [ ] 各ポート転送ルールが正しく設定されている
- [ ] 外部ポートと内部ポートが一致している（8444→8444など）
- [ ] プロトコルがTCPに設定されている
- [ ] 既存のポート転送設定（8001、8080等）は残している

---

## 🧪 動作確認

### 各ポートの接続確認

```bash
# 外部から各ポートへの接続をテスト
curl -I https://yoshi-nas-sys.duckdns.org:8444/
curl -I https://yoshi-nas-sys.duckdns.org:8445/
curl -I https://yoshi-nas-sys.duckdns.org:8446/
curl -I https://yoshi-nas-sys.duckdns.org:8447/
curl -I https://yoshi-nas-sys.duckdns.org:8448/
```

---

## 📚 参考資料

- [全サービス外部アクセス設定ガイド](ALL_SERVICES_EXTERNAL_ACCESS_SETUP.md)
- [Nginx Proxy Manager - 別々のProxy Hostとして作成](NGINX_PROXY_MANAGER_SEPARATE_PROXY_HOSTS.md)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant



