# 📋 Nginx Proxy Manager - Custom Locations 設定まとめ

**作成日**: 2025-11-02  
**対象**: すべてのサービスのCustom Locations設定

---

## 📋 Custom Locations一覧

### 1. `/analytics` (amazon-analytics)

**基本設定**:
- **Define location**: `/analytics`
- **Scheme**: `http`
- **Forward Hostname/IP**: `192.168.68.110`
- **Forward Port**: `8001`
- **Websockets Support**: オフ（不要）

**Custom Nginx configuration**: 空欄（不要）

---

### 2. `/documents` (document-automation)

**基本設定**:
- **Define location**: `/documents`
- **Scheme**: `http`
- **Forward Hostname/IP**: `192.168.68.110`
- **Forward Port**: `8080`
- **Websockets Support**: オフ（不要）

**Custom Nginx configuration**: 空欄（不要）

---

### 3. `/monitoring` (nas-dashboard-monitoring)

**基本設定**:
- **Define location**: `/monitoring`
- **Scheme**: `http`
- **Forward Hostname/IP**: `192.168.68.110`
- **Forward Port**: `3002`
- **Websockets Support**: オン（必須）

**Custom Nginx configuration**:
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

### 4. `/meetings` (meeting-minutes-byc)

**基本設定**:
- **Define location**: `/meetings`
- **Scheme**: `http`
- **Forward Hostname/IP**: `192.168.68.110`
- **Forward Port**: `5002`
- **Websockets Support**: オン（必須 - Socket.IO）

**Custom Nginx configuration**:
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

### 5. `/youtube` (youtube-to-notion)

**基本設定**:
- **Define location**: `/youtube`
- **Scheme**: `http`
- **Forward Hostname/IP**: `192.168.68.110`
- **Forward Port**: `8111`
- **Websockets Support**: オン（必須 - Socket.IO）

**Custom Nginx configuration**:
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

## 📋 設定一覧表

| Location | Forward Host/IP | Forward Port | WebSocket設定 | サービス名 |
|----------|----------------|-------------|---------------|-----------|
| `/analytics` | 192.168.68.110 | 8001 | ❌ 不要 | amazon-analytics |
| `/documents` | 192.168.68.110 | 8080 | ❌ 不要 | document-automation |
| `/monitoring` | 192.168.68.110 | 3002 | ✅ **必須** | nas-dashboard-monitoring |
| `/meetings` | 192.168.68.110 | 5002 | ✅ **必須** | meeting-minutes-byc |
| `/youtube` | 192.168.68.110 | 8111 | ✅ **必須** | youtube-to-notion |

---

## 📝 注意事項

### `/`（ルート）について

- `/`（ルート）は**Custom Locationsではなく、Detailsタブの設定**を使用します
- Detailsタブ:
  - Domain Names: `yoshi-nas-sys.duckdns.org`
  - Forward Hostname/IP: `192.168.68.110`
  - Forward Port: `9001`
  - → `https://yoshi-nas-sys.duckdns.org:8443/` → `http://192.168.68.110:9001`（nas-dashboard）

### WebSocket設定が必要なサービス

以下の3つのサービスは、Custom Locationsの詳細設定（歯車アイコン⚙️）で「Custom Nginx configuration」にWebSocket設定を追加する必要があります：

1. **`/monitoring`** (nas-dashboard-monitoring)
2. **`/meetings`** (meeting-minutes-byc)
3. **`/youtube`** (youtube-to-notion)

### WebSocket設定が不要なサービス

以下の2つのサービスは、WebSocket設定は不要です：

1. **`/analytics`** (amazon-analytics)
2. **`/documents`** (document-automation)

---

## 🔧 設定手順

### ステップ1: Custom Locationsタブを開く

1. Proxy Hostsタブを開く
2. `yoshi-nas-sys.duckdns.org`の設定を開く
3. 「Custom Locations」タブをクリック

### ステップ2: 各Locationを追加

1. 「Add Location」をクリック
2. 基本設定を入力:
   - Define location: `/analytics`、`/documents`など
   - Scheme: `http`
   - Forward Hostname/IP: `192.168.68.110`
   - Forward Port: 各サービスのポート番号

### ステップ3: WebSocket設定を追加（必要な場合）

WebSocketが必要なサービス（`/monitoring`、`/meetings`、`/youtube`）の場合：

1. 右側の**歯車アイコン（⚙️）**をクリック
2. 「Custom Nginx configuration」テキストエリアにWebSocket設定を記述
3. 設定を保存

### ステップ4: 設定を保存

すべてのLocationを追加したら、「Save」をクリックして保存

---

## ✅ 確認チェックリスト

- [ ] `/analytics` が追加されている
- [ ] `/documents` が追加されている
- [ ] `/monitoring` が追加されている（WebSocket設定あり）
- [ ] `/meetings` が追加されている（WebSocket設定あり）
- [ ] `/youtube` が追加されている（WebSocket設定あり）
- [ ] Detailsタブでルート設定（`/`）が正しい
- [ ] SSLタブで証明書が選択されている
- [ ] すべての設定を保存

---

## 🌐 アクセスURL（完成後）

すべてのサービスが以下のようにアクセス可能になります：

```
https://yoshi-nas-sys.duckdns.org:8443/             → nas-dashboard（Detailsタブ）
https://yoshi-nas-sys.duckdns.org:8443/analytics    → amazon-analytics
https://yoshi-nas-sys.duckdns.org:8443/documents    → document-automation
https://yoshi-nas-sys.duckdns.org:8443/monitoring   → nas-dashboard-monitoring
https://yoshi-nas-sys.duckdns.org:8443/meetings     → meeting-minutes-byc
https://yoshi-nas-sys.duckdns.org:8443/youtube      → youtube-to-notion
```

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

