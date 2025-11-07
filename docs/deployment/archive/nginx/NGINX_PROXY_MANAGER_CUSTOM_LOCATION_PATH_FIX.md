# 🔧 Nginx Proxy Manager - Custom Location Path設定修正

**作成日**: 2025-11-02  
**目的**: Custom Locationでサブフォルダ配信時のパス設定修正

---

## ⚠️ 問題

`/meetings`にアクセスするとNotFoundエラーが発生する。

**原因**: Custom Locationで`/meetings`を設定すると、転送先が`http://192.168.68.110:5002/meetings`になるが、アプリケーションは`/`（ルート）にルートを設定している。

---

## ✅ 解決方法

### 方法1: Forward Hostname/IPにパスを追加（推奨）

Custom Locationの設定で、**Forward Hostname/IPの末尾にスラッシュ（`/`）を追加**します。

#### `/meetings`の設定を修正

1. **Custom Locationの`/meetings`を編集**

2. **Forward Hostname/IPを変更**:
   - ❌ **変更前**: `192.168.68.110`
   - ✅ **変更後**: `192.168.68.110/` （末尾にスラッシュ）

3. **「Save」をクリック**

**これで**、`/meetings`へのアクセスが`http://192.168.68.110:5002/`に転送され、アプリケーションのルートパス（`/`）にアクセスできます。

---

### 方法2: すべてのCustom Locationに適用

以下のCustom Locationも同様に修正：

#### `/analytics` (amazon-analytics)
- Forward Hostname/IP: `192.168.68.110/`（末尾にスラッシュ）

#### `/documents` (document-automation)
- Forward Hostname/IP: `192.168.68.110/`（末尾にスラッシュ）

#### `/monitoring` (nas-dashboard-monitoring)
- Forward Hostname/IP: `192.168.68.110/`（末尾にスラッシュ）

#### `/meetings` (meeting-minutes-byc)
- Forward Hostname/IP: `192.168.68.110/`（末尾にスラッシュ）

#### `/youtube` (youtube-to-notion)
- Forward Hostname/IP: `192.168.68.110/`（末尾にスラッシュ）

---

## 🔍 Nginxの動作説明

### 末尾にスラッシュがある場合

```
Location: /meetings
Forward Hostname/IP: 192.168.68.110/
Forward Port: 5002
```

**結果**: 
- リクエスト: `https://yoshi-nas-sys.duckdns.org:8443/meetings`
- 転送先: `http://192.168.68.110:5002/`（`/meetings`が削除される）

### 末尾にスラッシュがない場合

```
Location: /meetings
Forward Hostname/IP: 192.168.68.110
Forward Port: 5002
```

**結果**: 
- リクエスト: `https://yoshi-nas-sys.duckdns.org:8443/meetings`
- 転送先: `http://192.168.68.110:5002/meetings`（パスがそのまま転送される）

---

## ✅ 修正後の動作確認

### 各サービスへのアクセス

```
https://yoshi-nas-sys.duckdns.org:8443/              → nas-dashboard ✅
https://yoshi-nas-sys.duckdns.org:8443/analytics     → amazon-analytics ✅
https://yoshi-nas-sys.duckdns.org:8443/documents     → document-automation ✅
https://yoshi-nas-sys.duckdns.org:8443/monitoring    → nas-dashboard-monitoring ✅
https://yoshi-nas-sys.duckdns.org:8443/meetings      → meeting-minutes-byc ✅
https://yoshi-nas-sys.duckdns.org:8443/youtube       → youtube-to-notion ✅
```

---

## 📝 チェックリスト

- [ ] `/analytics`のForward Hostname/IP: `192.168.68.110/`（末尾にスラッシュ）
- [ ] `/documents`のForward Hostname/IP: `192.168.68.110/`（末尾にスラッシュ）
- [ ] `/monitoring`のForward Hostname/IP: `192.168.68.110/`（末尾にスラッシュ）
- [ ] `/meetings`のForward Hostname/IP: `192.168.68.110/`（末尾にスラッシュ）
- [ ] `/youtube`のForward Hostname/IP: `192.168.68.110/`（末尾にスラッシュ）
- [ ] 各Locationを保存
- [ ] Proxy Host全体を保存
- [ ] 各サービスへのアクセステスト実施

---

## 📚 参考資料

- [Nginx Proxy Manager - Custom Locations設定まとめ](NGINX_PROXY_MANAGER_CUSTOM_LOCATIONS_SUMMARY.md)
- [Nginx Proxy Manager公式ドキュメント](https://nginxproxymanager.com/)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant



