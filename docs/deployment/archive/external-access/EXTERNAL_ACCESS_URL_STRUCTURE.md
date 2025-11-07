# 🌐 外部アクセスURL構成ガイド

**作成日**: 2025-11-02  
**対象**: 外部アクセス可能なNAS環境

---

## 📋 現在の状況

外部アクセス設定により、以下の方法で各サービスにアクセスできます。

---

## 🔍 アクセス方法

### 方法1: 直接ポート番号でアクセス（HTTP）

ルーターのポート転送設定により、外部から直接ポート番号を指定してアクセスできます。

**アクセスURL例**:

```
http://yoshi-nas-sys.duckdns.org:9001  → nas-dashboard
http://yoshi-nas-sys.duckdns.org:8001  → amazon-analytics
http://yoshi-nas-sys.duckdns.org:8080  → document-automation
http://yoshi-nas-sys.duckdns.org:5002  → meeting-minutes-byc
http://yoshi-nas-sys.duckdns.org:3002  → nas-dashboard-monitoring (frontend)
http://yoshi-nas-sys.duckdns.org:8002  → nas-dashboard-monitoring (backend)
http://yoshi-nas-sys.duckdns.org:8111  → youtube-to-notion
```

**注意事項**:
- HTTP（暗号化なし）でのアクセスになります
- セキュリティ上の懸念があります（パスワードが平文で送信される）
- 推奨されません

---

### 方法2: Nginx Proxy Manager経由でアクセス（HTTPS - 推奨）

現在設定されている方法です。

**アクセスURL**:

```
https://yoshi-nas-sys.duckdns.org:8443  → nas-dashboard（Nginx Proxy Manager経由）
```

**現在の設定状況**:
- Nginx Proxy Managerで`yoshi-nas-sys.duckdns.org`が`nas-dashboard`（192.168.68.110:9001）にプロキシ設定済み
- 他のサービス（amazon-analytics、document-automationなど）は未設定

---

## ⚠️ セキュリティ上の懸念

### 直接ポート番号でのアクセス（HTTP）の問題点

1. **暗号化なし**: パスワードや機密情報が平文で送信される
2. **証明書なし**: SSL/TLS証明書が使用できない
3. **セキュリティヘッダーなし**: セキュリティヘッダーが設定されていない
4. **認証なし**: 各サービスに直接アクセスできてしまう

### 推奨されるアクセス方法

**Nginx Proxy Manager経由（HTTPS）**:
- ✅ SSL/TLS暗号化
- ✅ Let's Encrypt証明書
- ✅ セキュリティヘッダー設定可能
- ✅ 一元管理

---

## 🛠️ 推奨される構成

### オプション1: すべてのサービスをNginx Proxy Manager経由でアクセス（推奨）

すべてのサービスをNginx Proxy Managerでプロキシ設定し、HTTPS経由でのみアクセス可能にする。

**メリット**:
- すべてのサービスがHTTPSで暗号化
- 一元管理
- セキュリティヘッダーの一元設定

**デメリット**:
- Nginx Proxy Managerで各サービスを設定する必要がある

---

### オプション2: 現状維持

- **ダッシュボード**: Nginx Proxy Manager経由（HTTPS:8443）
- **その他のサービス**: 直接ポート番号でアクセス（HTTP）

**メリット**:
- 設定変更が不要
- 各サービスに直接アクセス可能

**デメリット**:
- セキュリティリスク（HTTPでアクセス）
- 証明書が使用できない
- セキュリティヘッダーが設定されない

---

### オプション3: 外部からはNginx Proxy Manager経由のみ許可

ルーター設定とファイアウォールで、外部からはHTTPS（8443）のみ許可し、他のポートは内部ネットワークからのみアクセス可能にする。

**メリット**:
- 最高のセキュリティ
- すべてのサービスがHTTPS経由

**デメリット**:
- ルーターとファイアウォールの設定変更が必要
- Nginx Proxy Managerで各サービスを設定する必要がある

---

## 📊 現在の状態

### ルーター設定

ルーターのポート転送設定で、以下のポートが外部に公開されています：

| サービス | 外部ポート | 内部IP:ポート | 現在の状態 |
|---------|-----------|-------------|----------|
| nas-dashboard | 9001 | 192.168.68.110:9001 | ✅ 外部公開 |
| amazon-analytics | 8001 | 192.168.68.110:8001 | ✅ 外部公開 |
| document-automation | 8080 | 192.168.68.110:8080 | ✅ 外部公開 |
| meeting-minutes-byc | 5002 | 192.168.68.110:5002 | ✅ 外部公開 |
| nas-dashboard-monitoring (frontend) | 3002 | 192.168.68.110:3002 | ✅ 外部公開 |
| nas-dashboard-monitoring (backend) | 8002 | 192.168.68.110:8002 | ✅ 外部公開 |
| youtube-to-notion | 8111 | 192.168.68.110:8111 | ✅ 外部公開 |
| **HTTPS (Nginx Proxy Manager)** | **8443** | **192.168.68.110:8443** | ✅ **外部公開（推奨）** |

### ファイアウォール（UFW）設定

現在の設定では、以下のポートが外部からアクセス可能です：

- 9001, 8001, 8080, 5002, 3002, 8002, 8111（各サービス）
- 8443（Nginx Proxy Manager - HTTPS）

---

## 🔍 確認方法

### 外部から直接アクセスできるか確認

```bash
# 外部から直接ポート番号でアクセステスト
curl -I http://yoshi-nas-sys.duckdns.org:9001
curl -I http://yoshi-nas-sys.duckdns.org:8001
curl -I http://yoshi-nas-sys.duckdns.org:8080
```

### Nginx Proxy Manager経由でアクセスできるか確認

```bash
# HTTPS経由でアクセステスト（推奨）
curl -I -k https://yoshi-nas-sys.duckdns.org:8443
```

---

## ✅ まとめ

### 質問への回答

**はい、現在の設定では、ダッシュボード以外の画面についても直接URLを入力して各画面を表示できます。**

**例**:
- `http://yoshi-nas-sys.duckdns.org:9001` → nas-dashboard
- `http://yoshi-nas-sys.duckdns.org:8001` → amazon-analytics
- `http://yoshi-nas-sys.duckdns.org:8080` → document-automation
- など

**ただし**:
- ⚠️ HTTP（暗号化なし）でのアクセスになります
- ⚠️ セキュリティリスクがあります
- ✅ Nginx Proxy Manager経由（HTTPS:8443）でのアクセスを推奨

---

## 🔒 セキュリティ推奨事項

### 推奨されるアクセス方法

1. **ダッシュボード**: `https://yoshi-nas-sys.duckdns.org:8443`（Nginx Proxy Manager経由）

2. **その他のサービス**: 
   - 内部ネットワークから: `http://192.168.68.110:9001`など
   - 外部から: `http://yoshi-nas-sys.duckdns.org:9001`など（HTTP、セキュリティリスクあり）
   - または、Nginx Proxy Managerで各サービスもプロキシ設定（推奨）

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

