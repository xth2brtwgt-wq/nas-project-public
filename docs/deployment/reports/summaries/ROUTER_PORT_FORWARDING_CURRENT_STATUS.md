# 📊 ルーター ポート転送設定 現在の状態

**作成日**: 2025-11-04  
**目的**: ルーターのポート転送設定の現在の状態を記録

---

## ✅ 現在の設定状況

ルーターのポート転送設定を確認しました。以下の設定が存在しています：

### 必須設定（現在使用中）

| ルール名 | 内部IP:ポート | 用途 | 状態 |
|---------|-------------|------|------|
| **HTTP** | 192.168.68.110:8443 | Nginx Proxy Manager | ✅ **必須・使用中** |

**理由**: すべてのサービスがCustom Locationsで1つのProxy Host（ポート8443）経由でアクセス可能になっているため、この設定のみが必要です。

---

### 内部アクセス用設定（保持推奨）

以下の設定は**内部ネットワークからの直接アクセス用**です。削除しないでください。

| ルール名 | 内部IP:ポート | 用途 | 状態 |
|---------|-------------|------|------|
| **amazon-analytics** | 192.168.68.110:8001 | amazon-analytics（直接アクセス用） | ✅ **保持推奨** |
| **document-automation** | 192.168.68.110:8080 | document-automation（直接アクセス用） | ✅ **保持推奨** |
| **meeting-minutes-byc** | 192.168.68.110:5002 | meeting-minutes-byc（直接アクセス用） | ✅ **保持推奨** |
| **nas-dashboard** | 192.168.68.110:9001 | nas-dashboard（直接アクセス用） | ✅ **保持推奨** |
| **nas-dashboard-monitoring-f** | 192.168.68.110:3002 | nas-dashboard-monitoring（フロントエンド、直接アクセス用） | ✅ **保持推奨** |
| **nas-dashboard-monitoring-b** | 192.168.68.110:8002 | nas-dashboard-monitoring（バックエンド、直接アクセス用） | ✅ **保持推奨** |
| **youtube-to-notion** | 192.168.68.110:8111 | youtube-to-notion（直接アクセス用） | ✅ **保持推奨** |
| **lets-encrypts** | 192.168.68.110:80 | Let's Encrypt証明書更新用 | ✅ **保持推奨** |

**理由**: 
- 内部ネットワークから直接アクセスする場合に使用
- Nginx Proxy Managerが各サービスに接続する際にも使用

---

### 不要な設定（削除可能）

以下の設定は**現在の構成では使用されていません**。削除しても問題ありません。

| ルール名 | 内部IP:ポート | 用途 | 状態 |
|---------|-------------|------|------|
| **amazon-analytics-proxy** | 192.168.68.110:8444 | amazon-analytics（別Proxy Host用） | ⚠️ **不要・削除可能** |
| **document-automation-proxy** | 192.168.68.110:8445 | document-automation（別Proxy Host用） | ⚠️ **不要・削除可能** |
| **meeting-minutes-byc-proxy** | 192.168.68.110:8447 | meeting-minutes-byc（別Proxy Host用） | ⚠️ **不要・削除可能** |
| **nas-dashboard-monitoring-proxy** | 192.168.68.110:8446 | nas-dashboard-monitoring（別Proxy Host用） | ⚠️ **不要・削除可能** |
| **youtube-to-notion-proxy** | 192.168.68.110:8448 | youtube-to-notion（別Proxy Host用） | ⚠️ **削除可能（画像に表示されていないが、存在する可能性あり）** |

**理由**: 
- 現在の構成では、すべてのサービスがCustom Locationsで1つのProxy Host（ポート8443）に統合されています
- 各サービスを別々のProxy Hostとして作成する場合のみ必要ですが、現在は使用していません

**削除の推奨**: 
- セキュリティの観点から、使用されていないポートは閉じることを推奨します
- ただし、将来的に各サービスを別々のProxy Hostとして作成する場合は、これらの設定が必要になります

---

## 📋 推奨アクション

### 1. 必須設定の確認

- ✅ **HTTP (8443)**: 設定されていることを確認 ✅
- ✅ 外部ポート8443 → 内部ポート8443が正しく設定されていることを確認

### 2. 内部アクセス用設定の保持

以下の設定は**削除しないでください**：
- ✅ amazon-analytics (8001)
- ✅ document-automation (8080)
- ✅ meeting-minutes-byc (5002)
- ✅ nas-dashboard (9001)
- ✅ nas-dashboard-monitoring-f (3002)
- ✅ nas-dashboard-monitoring-b (8002)
- ✅ youtube-to-notion (8111)
- ✅ lets-encrypts (80)

### 3. 不要な設定の削除（オプション）

以下の設定は**削除しても問題ありません**（セキュリティの観点から推奨）：
- ⚠️ amazon-analytics-proxy (8444)
- ⚠️ document-automation-proxy (8445)
- ⚠️ meeting-minutes-byc-proxy (8447)
- ⚠️ nas-dashboard-monitoring-proxy (8446)
- ⚠️ youtube-to-notion-proxy (8448)

**注意**: 削除する前に、将来的に各サービスを別々のProxy Hostとして作成する予定がないことを確認してください。

---

## ✅ 確認チェックリスト

- [x] HTTP (8443) の設定が存在することを確認
- [x] 内部アクセス用設定（8001、8080、5002、9001、3002、8002、8111、80）が存在することを確認
- [x] 不要な設定（8444-8448）が存在することを確認
- [ ] 不要な設定を削除するかどうかを決定（推奨：削除）
- [ ] 外部アクセスが正常に動作することを確認

---

## 📊 現在の構成

### 外部からのアクセス

```
外部 → ルーター（8443） → Nginx Proxy Manager（8443） → 各サービス（Custom Locations経由）
```

### 内部ネットワークからのアクセス

```
内部 → 直接各サービス（8001、8080、5002、9001、3002、8002、8111）
または
内部 → Nginx Proxy Manager（8443） → 各サービス（Custom Locations経由）
```

---

## ⚠️ 注意事項

### 削除しないでください

以下の設定は**削除しないでください**：
- HTTP (8443) - 必須
- 内部アクセス用設定（8001、8080、5002、9001、3002、8002、8111、80） - 内部アクセス用

### 削除可能（推奨）

以下の設定は**削除しても問題ありません**（セキュリティの観点から推奨）：
- 8444-8448（各サービス用の別Proxy Host設定）

ただし、将来的に各サービスを別々のProxy Hostとして作成する場合は、これらの設定が必要になります。

---

## 📚 参考資料

- [ルーター ポート転送設定確認ガイド](ROUTER_PORT_FORWARDING_VERIFICATION.md)
- [全サービスのサブフォルダ対応完了](ALL_SERVICES_SUBFOLDER_COMPLETE.md)
- [現在の状況まとめ](CURRENT_STATUS_SUMMARY.md)

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

