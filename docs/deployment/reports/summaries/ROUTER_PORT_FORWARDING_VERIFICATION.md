# 🔍 ルーター ポート転送設定確認ガイド

**作成日**: 2025-11-04  
**目的**: 現在の構成でのルーターのポート転送設定を確認

---

## 📋 現在の構成

現在、すべてのサービスがCustom Locationsで1つのProxy Hostに統合されています：

- **Proxy Host**: `yoshi-nas-sys.duckdns.org`（ポート8443）
- **Custom Locations**:
  - `/meetings` → meeting-minutes-byc (192.168.68.110:5002)
  - `/analytics` → amazon-analytics (192.168.68.110:8001)
  - `/monitoring` → nas-dashboard-monitoring (192.168.68.110:3002)
  - `/documents` → document-automation (192.168.68.110:8080)
  - `/youtube` → youtube-to-notion (192.168.68.110:8111)

---

## ✅ 必要なポート転送設定

### 必須設定

現在の構成では、**以下のポート転送設定のみが必要**です：

| サービス | 外部ポート | 内部IP:ポート | プロトコル | 備考 |
|---------|-----------|-------------|----------|------|
| Nginx Proxy Manager | 8443 | 192.168.68.110:8443 | TCP | ✅ **必須** |

### 不要な設定

以下のポート転送設定は**不要**です：

- ❌ 8444（amazon-analytics用）- Custom Locationで統合されているため不要
- ❌ 8445（document-automation用）- Custom Locationで統合されているため不要
- ❌ 8446（nas-dashboard-monitoring用）- Custom Locationで統合されているため不要
- ❌ 8447（meeting-minutes-byc用）- Custom Locationで統合されているため不要
- ❌ 8448（youtube-to-notion用）- Custom Locationで統合されているため不要

**理由**: すべてのサービスが1つのProxy Host（ポート8443）経由でアクセス可能になっているため、追加のポート転送設定は不要です。

---

## 🔍 確認手順

### ステップ1: ルーターの管理画面にアクセス

1. **ルーターの管理画面を開く**
   - 通常は `http://192.168.1.1` または `http://192.168.0.1`
   - または、NASのゲートウェイIPアドレスを確認:
     ```bash
     # NASにSSH接続して確認
     ssh AdminUser@192.168.68.110
     ip route | grep default
     ```

2. **「ポート転送」「ポートマッピング」「仮想サーバー」などのメニューを開く**

### ステップ2: ポート転送設定を確認

以下の設定が存在することを確認：

#### 必須設定（8443）

- **ルール名**: `nginx-proxy-manager` または `HTTP` など
- **外部ポート**: `8443`
- **内部IP**: `192.168.68.110`
- **内部ポート**: `8443`
- **プロトコル**: `TCP`（または`TCP/UDP`）

#### 既存設定（内部アクセス用）

以下の設定は**削除しないでください**。内部ネットワークからの直接アクセス用です：

- **8001**: amazon-analytics（直接アクセス用）
- **8080**: document-automation（直接アクセス用）
- **5002**: meeting-minutes-byc（直接アクセス用）
- **3002**: nas-dashboard-monitoring（直接アクセス用）
- **8111**: youtube-to-notion（直接アクセス用）
- **9001**: nas-dashboard（直接アクセス用）
- **8002**: nas-dashboard-monitoring（バックエンド、直接アクセス用）
- **80**: Let's Encrypt証明書更新用

---

## ✅ 確認チェックリスト

- [ ] ルーターの管理画面にアクセスできる
- [ ] ポート転送設定画面を開くことができる
- [ ] **外部8443 → 内部8443**の設定が存在することを確認
- [ ] プロトコルが`TCP`（または`TCP/UDP`）に設定されていることを確認
- [ ] 内部IPが`192.168.68.110`に設定されていることを確認
- [ ] 既存の内部アクセス用設定（8001、8080、5002、3002、8111、9001、8002、80）が残っていることを確認
- [ ] 追加のポート転送設定（8444-8448）が存在しないことを確認（存在する場合は削除不要だが、使用されていない）

---

## 🧪 動作確認

### 外部アクセステスト

外部から以下のURLにアクセスできることを確認：

```bash
# 各サービスの外部アクセスURLをテスト
curl -I https://yoshi-nas-sys.duckdns.org:8443/meetings
curl -I https://yoshi-nas-sys.duckdns.org:8443/analytics
curl -I https://yoshi-nas-sys.duckdns.org:8443/monitoring
curl -I https://yoshi-nas-sys.duckdns.org:8443/documents
curl -I https://yoshi-nas-sys.duckdns.org:8443/youtube
```

すべてが`200 OK`または`401 Unauthorized`（Basic認証）を返すことを確認してください。

### ポート8443の接続確認

```bash
# ポート8443への接続をテスト
nc -zv yoshi-nas-sys.duckdns.org 8443
# または
telnet yoshi-nas-sys.duckdns.org 8443
```

接続が成功することを確認してください。

---

## ⚠️ 注意事項

### 既存のポート転送設定は削除しないでください

以下の設定は**削除しないでください**：

- **8001、8080、5002、3002、8111、9001、8002、80**: 内部ネットワークからの直接アクセス用
- これらの設定は、Nginx Proxy Managerが各サービスに接続する際にも使用されます

### 追加のポート転送設定（8444-8448）について

もし追加のポート転送設定（8444-8448）が存在する場合：

- **削除不要**: 現在の構成では使用されていませんが、削除しても問題ありません
- **削除推奨**: セキュリティの観点から、使用されていないポートは閉じることを推奨します
- **将来の変更**: 将来的に各サービスを別々のProxy Hostとして作成する場合、これらの設定が必要になります

---

## 📊 設定後の構成

### 外部からのアクセス

```
外部 → ルーター（8443） → Nginx Proxy Manager（8443） → 各サービス（Custom Locations経由）
```

### 内部ネットワークからのアクセス

```
内部 → 直接各サービス（8001、8080、5002、3002、8111、9001、8002）
または
内部 → Nginx Proxy Manager（8443） → 各サービス（Custom Locations経由）
```

---

## 📚 参考資料

- [全サービスのサブフォルダ対応完了](ALL_SERVICES_SUBFOLDER_COMPLETE.md)
- [Nginx Proxy Manager Advancedタブ完全設定](NGINX_PROXY_MANAGER_ADVANCED_TAB_COMPLETE_CONFIG.md)
- [現在の状況まとめ](CURRENT_STATUS_SUMMARY.md)

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

