# 🌐 Nginx Proxy Manager - 各サービスを別々のProxy Hostとして作成

**作成日**: 2025-11-02  
**対象**: Custom Locationsが動作しない場合の代替方法

---

## 📋 問題

Custom Locationsを追加すると、Nginx設定ファイルが生成されず、アクセスできない。

**解決方法**: Custom Locationsを使わず、各サービスを別々のProxy Hostとして作成する。

---

## 🎯 設定方法

### 方法1: サブドメインを使用（推奨）

各サービスにサブドメインを割り当てる：

- `https://yoshi-nas-sys.duckdns.org:8443/` → nas-dashboard
- `https://analytics.yoshi-nas-sys.duckdns.org:8443/` → amazon-analytics
- `https://documents.yoshi-nas-sys.duckdns.org:8443/` → document-automation
- `https://monitoring.yoshi-nas-sys.duckdns.org:8443/` → nas-dashboard-monitoring
- `https://meetings.yoshi-nas-sys.duckdns.org:8443/` → meeting-minutes-byc
- `https://youtube.yoshi-nas-sys.duckdns.org:8443/` → youtube-to-notion

**注意**: DuckDNSではサブドメインが使用できないため、この方法は使用できません。

---

### 方法2: 異なるポート番号を使用（推奨）

各サービスに異なるポート番号を割り当てる（ルーターのポート転送設定が必要）：

- `https://yoshi-nas-sys.duckdns.org:8443/` → nas-dashboard
- `https://yoshi-nas-sys.duckdns.org:8444/` → amazon-analytics
- `https://yoshi-nas-sys.duckdns.org:8445/` → document-automation
- `https://yoshi-nas-sys.duckdns.org:8446/` → nas-dashboard-monitoring
- `https://yoshi-nas-sys.duckdns.org:8447/` → meeting-minutes-byc
- `https://yoshi-nas-sys.duckdns.org:8448/` → youtube-to-notion

**ルーターのポート転送設定が必要**です。

---

### 方法3: 現在の設定を維持（推奨）

Custom Locationsを削除して、現在の設定を維持：

- `https://yoshi-nas-sys.duckdns.org:8443/` → nas-dashboard（Detailsタブの設定）

**その他のサービスは内部ネットワークからのみアクセス**：

- `http://192.168.68.110:8001` → amazon-analytics
- `http://192.168.68.110:8080` → document-automation
- `http://192.168.68.110:3002` → nas-dashboard-monitoring
- `http://192.168.68.110:5002` → meeting-minutes-byc
- `http://192.168.68.110:8111` → youtube-to-notion

---

## 🚀 推奨される方法：方法2（異なるポート番号）

### ステップ1: ルーターのポート転送設定

ルーターで以下のポート転送を設定：

- 外部8444 → 内部8444（amazon-analytics用）
- 外部8445 → 内部8445（document-automation用）
- 外部8446 → 内部8446（nas-dashboard-monitoring用）
- 外部8447 → 内部8447（meeting-minutes-byc用）
- 外部8448 → 内部8448（youtube-to-notion用）

### ステップ2: Nginx Proxy Managerで各Proxy Hostを作成

#### 2-1. nas-dashboard（既存）

- Domain Names: `yoshi-nas-sys.duckdns.org`
- Forward Hostname/IP: `192.168.68.110`
- Forward Port: `9001`
- SSL: 証明書を選択

#### 2-2. amazon-analytics

1. **「Add Proxy Host」をクリック**
2. **Detailsタブ**:
   - Domain Names: `yoshi-nas-sys.duckdns.org`
   - Scheme: `http`
   - Forward Hostname/IP: `192.168.68.110`
   - Forward Port: `8001`
3. **SSLタブ**:
   - SSL Certificate: `yoshi-nas-sys-duckdns-org`を選択
   - Force SSL: ✅オン
4. **Advancedタブ**:
   - Listen Port: `8444`（カスタムポート）
5. **Save**をクリック

#### 2-3. document-automation

1. **「Add Proxy Host」をクリック**
2. **Detailsタブ**:
   - Domain Names: `yoshi-nas-sys.duckdns.org`
   - Forward Hostname/IP: `192.168.68.110`
   - Forward Port: `8080`
3. **SSLタブ**:
   - SSL Certificate: `yoshi-nas-sys-duckdns-org`を選択
   - Force SSL: ✅オン
4. **Advancedタブ**:
   - Listen Port: `8445`（カスタムポート）
5. **Save**をクリック

#### 2-4. nas-dashboard-monitoring

1. **「Add Proxy Host」をクリック**
2. **Detailsタブ**:
   - Domain Names: `yoshi-nas-sys.duckdns.org`
   - Forward Hostname/IP: `192.168.68.110`
   - Forward Port: `3002`
   - Websockets Support: ✅オン
3. **SSLタブ**:
   - SSL Certificate: `yoshi-nas-sys-duckdns-org`を選択
   - Force SSL: ✅オン
4. **Advancedタブ**:
   - Listen Port: `8446`（カスタムポート）
5. **Save**をクリック

#### 2-5. meeting-minutes-byc

1. **「Add Proxy Host」をクリック**
2. **Detailsタブ**:
   - Domain Names: `yoshi-nas-sys.duckdns.org`
   - Forward Hostname/IP: `192.168.68.110`
   - Forward Port: `5002`
   - Websockets Support: ✅オン
3. **SSLタブ**:
   - SSL Certificate: `yoshi-nas-sys-duckdns-org`を選択
   - Force SSL: ✅オン
4. **Advancedタブ**:
   - Listen Port: `8447`（カスタムポート）
5. **Save**をクリック

#### 2-6. youtube-to-notion

1. **「Add Proxy Host」をクリック**
2. **Detailsタブ**:
   - Domain Names: `yoshi-nas-sys.duckdns.org`
   - Forward Hostname/IP: `192.168.68.110`
   - Forward Port: `8111`
   - Websockets Support: ✅オン
3. **SSLタブ**:
   - SSL Certificate: `yoshi-nas-sys-duckdns-org`を選択
   - Force SSL: ✅オン
4. **Advancedタブ**:
   - Listen Port: `8448`（カスタムポート）
5. **Save**をクリック

---

## 📋 設定一覧表（方法2）

| サービス | 外部URL | 内部ポート | Nginx Proxy Managerポート | WebSocket |
|---------|--------|-----------|-------------------------|-----------|
| nas-dashboard | `https://yoshi-nas-sys.duckdns.org:8443/` | 9001 | 8443 | ❌ |
| amazon-analytics | `https://yoshi-nas-sys.duckdns.org:8444/` | 8001 | 8444 | ❌ |
| document-automation | `https://yoshi-nas-sys.duckdns.org:8445/` | 8080 | 8445 | ❌ |
| nas-dashboard-monitoring | `https://yoshi-nas-sys.duckdns.org:8446/` | 3002 | 8446 | ✅ |
| meeting-minutes-byc | `https://yoshi-nas-sys.duckdns.org:8447/` | 5002 | 8447 | ✅ |
| youtube-to-notion | `https://yoshi-nas-sys.duckdns.org:8448/` | 8111 | 8448 | ✅ |

---

## 📝 注意事項

### ルーターのポート転送設定が必要

方法2を使用する場合、ルーターで各ポートの転送設定が必要です。

### Nginx Proxy Managerのポート設定

Nginx Proxy Managerの「Advanced」タブで「Listen Port」を設定する必要がある場合と、自動的に設定される場合があります。

### SSL証明書の共有

すべてのProxy Hostで同じSSL証明書（`yoshi-nas-sys-duckdns-org`）を使用できます。

---

## ✅ 推奨事項

### 現時点での推奨：方法3（現在の設定を維持）

Custom Locationsが動作しない場合、現時点では以下を推奨します：

1. **nas-dashboardのみ外部アクセス可能**（`https://yoshi-nas-sys.duckdns.org:8443/`）
2. **その他のサービスは内部ネットワークからのみアクセス**

**メリット**:
- 設定がシンプル
- セキュリティが高い（外部アクセスが限定的）
- 問題が少ない

**デメリット**:
- 外部から他のサービスにアクセスできない

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

