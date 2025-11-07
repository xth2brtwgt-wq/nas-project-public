# 🚫 Nginx Proxy ManagerでAccess Listsを使ってIPアドレスをブロックする方法

**作成日**: 2025-11-07  
**対象**: WebUIでブラックリストIPを管理する方法

---

## 📋 概要

Nginx Proxy Managerの「Access Lists」機能を使用して、WebUIから直接IPアドレスをブラックリストに追加・管理する方法です。

---

## ✅ 実装方法

### ステップ1: ブラックリスト用のAccess Listを作成

1. **Nginx Proxy ManagerのWeb UIにアクセス**: `http://192.168.68.110:8181`

2. **「Access Lists」タブを開く**

3. **「Add Access List」をクリック**

4. **「Details」タブで設定**:
   - **Name**: `blacklist-ips`（任意の名前）
   - **「Satisfy Any」**: オフ（デフォルト）

5. **「Access」タブを開く**

6. **「deny」セクションにIPアドレスを追加**:
   - **IPアドレス**: `51.159.103.26`
   - **「Add」ボタンをクリック**
   
   **複数のIPアドレスを追加する場合**:
   - 各IPアドレスを1つずつ追加
   - または、IPアドレス範囲（例: `192.168.1.0/24`）を追加

7. **「Save」をクリック**

---

### ステップ2: Proxy HostにAccess Listを適用

1. **「Proxy Hosts」タブを開く**

2. **`yoshi-nas-sys.duckdns.org`のProxy Hostを編集**

3. **「Access Lists」タブを開く**

4. **「Access List」ドロップダウンで`blacklist-ips`を選択**

5. **「Save」をクリック**

---

## 📝 設定例

### 複数のIPアドレスをブロックする場合

「Access」タブの「deny」セクションに以下を追加：

- `51.159.103.26` (フランス・Scaleway) - 2025-11-07: 404エラー21回を検出
- `192.168.1.100` (例)
- `10.0.0.50` (例)

### IPアドレス範囲をブロックする場合

- `192.168.1.0/24` (192.168.1.0 ～ 192.168.1.255)
- `10.0.0.0/8` (10.0.0.0 ～ 10.255.255.255)

---

## 🔍 動作確認

### ブロックされたIPアドレスからのアクセス

ブロックされたIPアドレスからアクセスすると、以下のエラーが返されます：

- **ステータスコード**: `403 Forbidden`
- **エラーメッセージ**: "403 Forbidden" または "Access denied"

### ログで確認

```bash
# Nginx Proxy Managerのアクセスログを確認
docker logs nginx-proxy-manager --tail 100 | grep "51.159.103.26"

# 403エラーが記録されていることを確認
```

---

## 🔄 管理方法

### ブラックリストIPの追加

1. **「Access Lists」タブを開く**
2. **`blacklist-ips`のAccess Listを編集**
3. **「Access」タブを開く**
4. **「deny」セクションにIPアドレスを追加**
5. **「Add」ボタンをクリック**
6. **「Save」をクリック**

### ブラックリストIPの削除

1. **「Access Lists」タブを開く**
2. **`blacklist-ips`のAccess Listを編集**
3. **「Access」タブを開く**
4. **削除したいIPアドレスの「×」ボタンをクリック**
5. **「Save」をクリック**

---

## ⚠️ 注意事項

### Basic認証との併用

- Basic認証とAccess Listを併用する場合、「Satisfy Any」の設定に注意してください
- 「Satisfy Any」がオフの場合、Basic認証とIP制限の**両方**を満たす必要があります
- 「Satisfy Any」がオンの場合、Basic認証**または**IP制限の**どちらか一方**を満たせばアクセスできます

### 誤ってブロックした場合

1. **「Access Lists」タブを開く**
2. **`blacklist-ips`のAccess Listを編集**
3. **「Access」タブを開く**
4. **誤ってブロックしたIPアドレスの「×」ボタンをクリック**
5. **「Save」をクリック**

---

## 📊 現在ブロックされているIPアドレス

- **51.159.103.26** (フランス・Scaleway) - 2025-11-07: 404エラー21回を検出

---

## 🔗 関連ドキュメント

- [Nginx Proxy Manager Basic認証設定](NGINX_PROXY_MANAGER_BASIC_AUTH_SETUP.md)
- [Nginx Proxy Manager Basic認証 403エラー解決](NGINX_PROXY_MANAGER_BASIC_AUTH_403_FIX.md)
- [Nginxアクセスログ監視](NGINX_ACCESS_LOG_MONITORING.md)

