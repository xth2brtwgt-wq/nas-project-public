# ✅ Nginx Proxy Manager - 現在の設定状況

**作成日**: 2025-11-02  
**状態**: nas-dashboardのみ外部アクセス可能（Custom Locationsは使用しない）

---

## 📋 現在の設定

### 外部アクセス可能なサービス

**nas-dashboard**のみ外部アクセス可能：

- **外部URL**: `https://yoshi-nas-sys.duckdns.org:8443/`
- **内部転送先**: `http://192.168.68.110:9001`
- **SSL証明書**: Let's Encrypt（`yoshi-nas-sys-duckdns-org`）

### 内部ネットワークからのみアクセス可能なサービス

以下のサービスは内部ネットワークからのみアクセス可能：

- **amazon-analytics**: `http://192.168.68.110:8001`
- **document-automation**: `http://192.168.68.110:8080`
- **nas-dashboard-monitoring**: `http://192.168.68.110:3002`
- **meeting-minutes-byc**: `http://192.168.68.110:5002`
- **youtube-to-notion**: `http://192.168.68.110:8111`

---

## 📝 注意事項

### Custom Locationsについて

Custom Locationsを追加すると、Nginx Proxy Managerの設定ファイルが生成されず、アクセスできなくなる問題があります。

**現時点では、Custom Locationsは使用しない設定を維持**します。

---

## 🔮 今後の展開（必要に応じて）

他のサービスも外部からアクセスしたい場合の方法：

### 方法1: 各サービスを別々のProxy Hostとして作成

各サービスに異なるポート番号を割り当てる：

- `https://yoshi-nas-sys.duckdns.org:8444/` → amazon-analytics
- `https://yoshi-nas-sys.duckdns.org:8445/` → document-automation
- `https://yoshi-nas-sys.duckdns.org:8446/` → nas-dashboard-monitoring
- `https://yoshi-nas-sys.duckdns.org:8447/` → meeting-minutes-byc
- `https://yoshi-nas-sys.duckdns.org:8448/` → youtube-to-notion

**必要な設定**:
- ルーターのポート転送設定（8444〜8448を追加）
- Nginx Proxy Managerで各サービス用のProxy Hostを作成

詳細は`docs/deployment/NGINX_PROXY_MANAGER_SEPARATE_PROXY_HOSTS.md`を参照。

---

### 方法2: Custom Locationsの問題を解決

Custom Locationsが動作するようになった場合、以下の設定を追加：

- `/analytics` → amazon-analytics
- `/documents` → document-automation
- `/monitoring` → nas-dashboard-monitoring（WebSocket設定あり）
- `/meetings` → meeting-minutes-byc（WebSocket設定あり）
- `/youtube` → youtube-to-notion（WebSocket設定あり）

詳細は`docs/deployment/NGINX_PROXY_MANAGER_CUSTOM_LOCATIONS_SUMMARY.md`を参照。

---

## 🔒 セキュリティ設定

### ✅ Basic認証が有効化されています

- **設定完了日**: 2025-11-02
- **アクセス制御**: Basic認証による認証が必要
- `https://yoshi-nas-sys.duckdns.org:8443/` → 認証必須

**設定内容**:
- Access List名: `nas-dashboard-auth`
- 「Satisfy Any」設定: 有効（「deny all」がある場合でもBasic認証でアクセス可能）

**動作確認**:
- ✅ 認証ダイアログが表示される
- ✅ 正しい認証情報でアクセスできる
- ✅ 間違った認証情報ではアクセスできない

### 🔐 その他のセキュリティ対策（推奨）

詳細は`docs/deployment/EXTERNAL_ACCESS_SECURITY.md`を参照。

1. **セキュリティヘッダーの設定**（推奨）
2. **Fail2banの設定**（既に設定済み）
3. **IP制限**（固定IPを使用している場合）
4. **アクセスログの監視**

---

## ✅ 確認チェックリスト

- [x] nas-dashboardが外部からアクセス可能
- [x] SSL証明書が正しく設定されている
- [x] 他のサービスは内部ネットワークからアクセス可能
- [x] Custom Locationsは使用しない（問題回避）
- [x] **Basic認証を追加**（完了）

---

## 📚 参考資料

- [Nginx Proxy Manager - Basic認証設定ガイド](NGINX_PROXY_MANAGER_BASIC_AUTH_SETUP.md)
- [外部アクセス時のセキュリティ対策ガイド](EXTERNAL_ACCESS_SECURITY.md)
- [Nginx Proxy Manager - Custom Locations設定まとめ](NGINX_PROXY_MANAGER_CUSTOM_LOCATIONS_SUMMARY.md)
- [Nginx Proxy Manager - 別々のProxy Hostとして作成](NGINX_PROXY_MANAGER_SEPARATE_PROXY_HOSTS.md)
- [現在のアクセス状況](CURRENT_ACCESS_STATUS.md)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

