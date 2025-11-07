# 🌐 全サービス外部アクセス設定ガイド

**作成日**: 2025-11-02  
**目的**: 全てのシステムを外部アクセス可能にし、ダッシュボード経由でのみアクセス可能にする

---

## 📋 要件

1. **全サービスを外部アクセス可能にする**
   - amazon-analytics
   - document-automation
   - nas-dashboard-monitoring
   - meeting-minutes-byc
   - youtube-to-notion

2. **ダッシュボード経由でのみアクセス可能にする**
   - 各サービスのURLを直接入力してもアクセスできない
   - 必ずダッシュボードでログインしてからアクセスできるようにする

---

## 🎯 実装方法

### 方法1: 各サービスを別々のProxy Hostとして作成（推奨）

各サービスに異なるポート番号を割り当て、全てにBasic認証を適用します。

**アクセスURL（完成後）**:
```
https://yoshi-nas-sys.duckdns.org:8443/   → nas-dashboard（認証必須）
https://yoshi-nas-sys.duckdns.org:8444/   → amazon-analytics（認証必須）
https://yoshi-nas-sys.duckdns.org:8445/   → document-automation（認証必須）
https://yoshi-nas-sys.duckdns.org:8446/   → nas-dashboard-monitoring（認証必須）
https://yoshi-nas-sys.duckdns.org:8447/   → meeting-minutes-byc（認証必須）
https://yoshi-nas-sys.duckdns.org:8448/   → youtube-to-notion（認証必須）
```

**ダッシュボード経由でのみアクセス可能にする方法**:

1. **内部ネットワークからの直接アクセスをブロック**
   - 各サービスを内部ネットワーク（192.168.68.0/24）からの直接アクセスを拒否
   - Nginx Proxy Manager経由でのみアクセス可能にする

2. **ダッシュボードから各サービスへのリンクを提供**
   - ダッシュボードのログイン後、各サービスへのリンクを表示
   - ダッシュボード経由で各サービスにアクセスする導線を提供

---

## 🚀 設定手順

### ステップ1: ルーターのポート転送設定を追加

1. **ルーターの管理画面にアクセス**

2. **ポート転送設定を追加**:

| サービス | 外部ポート | 内部IP:ポート | プロトコル |
|---------|-----------|-------------|----------|
| nas-dashboard | 8443 | 192.168.68.110:8443 | TCP |
| amazon-analytics | 8444 | 192.168.68.110:8444 | TCP |
| document-automation | 8445 | 192.168.68.110:8445 | TCP |
| nas-dashboard-monitoring | 8446 | 192.168.68.110:8446 | TCP |
| meeting-minutes-byc | 8447 | 192.168.68.110:8447 | TCP |
| youtube-to-notion | 8448 | 192.168.68.110:8448 | TCP |

**注意**: 内部ポート（8444〜8448）はNginx Proxy Managerのポートです。各サービス自体のポート（8001、8080、3002、5002、8111）ではありません。

---

### ステップ2: Nginx Proxy Managerで各サービス用のProxy Hostを作成

#### 2-1. amazon-analytics (ポート8444)

1. **Nginx Proxy ManagerのWeb UIにアクセス**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → 「Add Proxy Host」をクリック**

3. **「Details」タブ**:
   - **Domain Names**: `yoshi-nas-sys.duckdns.org`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `8001`
   - **Cache Assets**: ✅（オプション）
   - **Block Common Exploits**: ✅（推奨）
   - **Websockets Support**: ❌（不要）
   - **Access List**: `nas-dashboard-auth`（既存のAccess Listを選択）

4. **「SSL」タブ**:
   - **SSL Certificate**: `yoshi-nas-sys-duckdns-org`（既存の証明書を選択）
   - **Force SSL**: ✅（推奨）
   - **HTTP/2 Support**: ✅（推奨）

5. **「Custom」タブ**（オプション）:
   - カスタム設定は不要

6. **「Save」をクリック**

7. **「Advanced」タブで「Listen Port」を確認**:
   - **Listen Port**: `8444` を設定（または自動的に設定される）

---

#### 2-2. document-automation (ポート8445)

同様の手順で設定：
- **Forward Port**: `8080`
- **Listen Port**: `8445`
- **Access List**: `nas-dashboard-auth`

---

#### 2-3. nas-dashboard-monitoring (ポート8446)

同様の手順で設定：
- **Forward Port**: `3002`
- **Listen Port**: `8446`
- **Websockets Support**: ✅（必須）
- **Access List**: `nas-dashboard-auth`

**WebSocket設定が必要な場合**:
「Advanced」タブの「Custom Nginx configuration」に以下を追加：

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

---

#### 2-4. meeting-minutes-byc (ポート8447)

同様の手順で設定：
- **Forward Port**: `5002`
- **Listen Port**: `8447`
- **Websockets Support**: ✅（必須 - Socket.IO）
- **Access List**: `nas-dashboard-auth`

**WebSocket設定**（上記と同じ）を追加。

---

#### 2-5. youtube-to-notion (ポート8448)

同様の手順で設定：
- **Forward Port**: `8111`
- **Listen Port**: `8448`
- **Websockets Support**: ✅（必要な場合）
- **Access List**: `nas-dashboard-auth`

---

### ステップ3: 内部ネットワークからの直接アクセスをブロック

各サービスを内部ネットワークからの直接アクセスをブロックし、Nginx Proxy Manager経由でのみアクセス可能にします。

#### 方法A: Nginx Proxy ManagerでIP制限を追加（推奨）

1. **既存のAccess List（`nas-dashboard-auth`）を編集**

2. **「Access」タブを開く**

3. **外部からのみアクセス可能にする設定**:
   - **allow** `0.0.0.0/0` を追加（すべてのIPからアクセス可能）
   - **「Satisfy Any」をオンにする**（Basic認証またはIP制限のどちらか一方を満たせばアクセス可能）

4. **各サービスを内部ネットワークからの直接アクセスをブロック**:
   - 各サービスのdocker-compose.ymlで、ポートを外部に公開しない
   - または、各サービスをNginx Proxy Manager経由でのみアクセス可能にする

#### 方法B: 各サービスのアプリケーションレベルで認証を追加

各サービスに認証チェックを追加し、ダッシュボード経由でのみアクセス可能にする（実装が複雑なため、後で検討）。

---

### ステップ4: ダッシュボードから各サービスへのリンクを追加

nas-dashboardの`app.py`を編集して、各サービスへのリンクを追加します。

---

## ✅ 動作確認

### 各サービスへのアクセステスト

1. **外部ネットワークからアクセス**（モバイルデータ通信など）

2. **各サービスのURLにアクセス**:
   ```
   https://yoshi-nas-sys.duckdns.org:8443/   → nas-dashboard
   https://yoshi-nas-sys.duckdns.org:8444/   → amazon-analytics
   https://yoshi-nas-sys.duckdns.org:8445/   → document-automation
   https://yoshi-nas-sys.duckdns.org:8446/   → nas-dashboard-monitoring
   https://yoshi-nas-sys.duckdns.org:8447/   → meeting-minutes-byc
   https://yoshi-nas-sys.duckdns.org:8448/   → youtube-to-notion
   ```

3. **認証ダイアログが表示されることを確認**

4. **正しい認証情報でアクセスできることを確認**

---

## ⚠️ 注意事項

### ダッシュボード経由でのみアクセス可能にする制限

現在の実装では、各サービスのURLを直接入力すると、Basic認証のダイアログが表示され、認証に成功すればアクセスできます。

**完全にダッシュボード経由でのみアクセス可能にするには**:

1. **各サービスに独自の認証システムを実装**
   - ダッシュボードでログインしたユーザーにトークンを発行
   - 各サービスがトークンを検証してアクセスを許可

2. **SSO（Single Sign-On）の実装**
   - ダッシュボードでログイン後、各サービスに自動的に認証情報を渡す

3. **Refererチェック**
   - 各サービスがRefererヘッダーをチェックし、ダッシュボードからのアクセスのみを許可

これらは実装が複雑なため、まずは全サービスを外部アクセス可能にし、Basic認証で保護することを推奨します。

---

## 📝 チェックリスト

- [ ] ルーターのポート転送設定を追加（8444〜8448）
- [ ] Nginx Proxy Managerで各サービス用のProxy Hostを作成
- [ ] 各Proxy HostにAccess List（`nas-dashboard-auth`）を適用
- [ ] SSL証明書を各Proxy Hostに適用
- [ ] WebSocket設定が必要なサービスに設定を追加
- [ ] 各サービスへのアクセステスト実施
- [ ] ダッシュボードから各サービスへのリンクを追加（オプション）

---

## 📚 参考資料

- [Nginx Proxy Manager - 別々のProxy Hostとして作成](NGINX_PROXY_MANAGER_SEPARATE_PROXY_HOSTS.md)
- [Nginx Proxy Manager - Basic認証設定ガイド](NGINX_PROXY_MANAGER_BASIC_AUTH_SETUP.md)
- [Nginx Proxy Manager - WebSocket設定ガイド](NGINX_PROXY_MANAGER_WEBSOCKET_CONFIG.md)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant



