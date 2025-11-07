# 📋 Nginx Proxy Manager - Custom Locations の `/`（ルート）について

**作成日**: 2025-11-02  
**対象**: Custom Locationsでの`/`（ルート）設定の説明

---

## ❓ よくある質問

### Q: Custom Locationsで`/`（ルート）を追加する際、実際のフォルダ名を付ける必要がありますか？

**A: いいえ、必要ありません。**

`/`は**ルートパス**を意味するため、フォルダ名を付ける必要はありません。

---

## 📋 Custom Locationsでの`/`の役割

### `/`（ルート）の意味

- **`/`**: ドメインのルートパス（`https://yoshi-nas-sys.duckdns.org:8443/`）
- **実際のフォルダ名は不要**: `/`だけでルートパスを指定できます

### 設定例

#### 正しい設定

```
Define location: /
Scheme: http
Forward Hostname/IP: 192.168.68.110
Forward Port: 9001
```

この設定で、`https://yoshi-nas-sys.duckdns.org:8443/` へのアクセスが `http://192.168.68.110:9001` に転送されます。

#### 間違った設定（不要）

```
Define location: /dashboard    ← これは不要（フォルダ名を付ける必要はない）
Scheme: http
Forward Hostname/IP: 192.168.68.110
Forward Port: 9001
```

この設定だと、`https://yoshi-nas-sys.duckdns.org:8443/dashboard` へのアクセスのみが転送され、ルートパス（`/`）へのアクセスは転送されません。

---

## 🎯 現在の設定構成

### Proxy Hostの設定

**Domain Names**: `yoshi-nas-sys.duckdns.org`

**Custom Locations**:

| Location | Forward Host/IP | Forward Port | 転送先 |
|----------|----------------|-------------|--------|
| `/` | 192.168.68.110 | 9001 | nas-dashboard |
| `/analytics` | 192.168.68.110 | 8001 | amazon-analytics |
| `/documents` | 192.168.68.110 | 8080 | document-automation |
| `/monitoring` | 192.168.68.110 | 3002 | nas-dashboard-monitoring |
| `/meetings` | 192.168.68.110 | 5002 | meeting-minutes-byc |
| `/youtube` | 192.168.68.110 | 8111 | youtube-to-notion |

---

## ✅ 設定手順

### ステップ1: Custom Locationsタブを開く

1. **Proxy Hostsタブを開く**
2. **`yoshi-nas-sys.duckdns.org`の設定を開く**
3. **Custom Locationsタブをクリック**

### ステップ2: `/`（ルート）のLocationを確認

**`/`（ルート）のLocationが存在するか確認**:

- **存在する場合**: そのまま設定を確認
- **存在しない場合**: 以下を追加

### ステップ3: `/`（ルート）のLocationを追加（必要な場合）

1. **「Add Location」をクリック**

2. **設定項目**:
   - **Define location**: `/` （フォルダ名は不要、`/`だけでOK）
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `9001`
   - **Custom Nginx configuration**: 空欄（WebSocket不要）

3. **「Save」をクリック**

---

## ⚠️ 重要な注意事項

### DetailsタブとCustom Locationsの関係

**Custom Locationsで`/`を設定する場合**:

- **Detailsタブの設定**: 「Forward Hostname/IP」と「Forward Port」は**空欄でもOK**
- **Custom Locationsで`: /`（ルート）のLocationが存在する**場合は、Custom Locationsの設定が優先される

**Custom Locationsで`/`が存在しない場合**:

- **Detailsタブの設定**: 「Forward Hostname/IP」と「Forward Port」が**必須**
- Detailsタブの設定が、ルートパス（`/`）の転送先として使用される

---

## 🔍 確認方法

### `/`（ルート）のLocationが存在するか確認

1. **Custom Locationsタブを開く**
2. **Locationの一覧を確認**
3. **`/`が存在するか確認**

### 存在しない場合の追加

1. **「Add Location」をクリック**
2. **Define locationに`/`を入力**（フォルダ名は不要）
3. **Forward Hostname/IPとForward Portを設定**
4. **「Save」をクリック**

---

## 📝 まとめ

- **`/`はルートパス**: フォルダ名を付ける必要はない
- **設定方法**: Define locationに`/`を入力するだけでOK
- **Detailsタブとの関係**: Custom Locationsで`/`が存在する場合、Detailsタブの設定は空欄でもOK

**現在の設定では**:
- `/` → nas-dashboard (192.168.68.110:9001)
- `/analytics` → amazon-analytics (192.168.68.110:8001)
- `/documents` → document-automation (192.168.68.110:8080)
- など

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

