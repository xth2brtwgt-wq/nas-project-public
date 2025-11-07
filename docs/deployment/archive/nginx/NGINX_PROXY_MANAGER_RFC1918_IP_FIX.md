# 🔧 Nginx Proxy Manager - RFC1918 IP エラー解決ガイド

**作成日**: 2025-11-02  
**目的**: 「Rejected request from RFC1918 IP to public server address」エラーを解決

---

## ⚠️ 問題の症状

以下のエラーが表示される：

- **403 Forbidden**
- **エラーメッセージ**: "Rejected request from RFC1918 IP to public server address"
- 内部ネットワーク（192.168.x.xなど）からアクセスできない

---

## 🔍 原因

Nginx Proxy Managerが、内部ネットワーク（RFC1918 IP）からのパブリックサーバーアドレスへのアクセスを拒否している。

**RFC1918 IPとは**:
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

これらのIPアドレスは、内部ネットワーク（プライベートネットワーク）で使用されるIPアドレスです。

---

## ✅ 解決方法

### 方法1: Access Listの「Satisfy Any」を有効にする（推奨）

1. **Nginx Proxy ManagerのWeb UIにアクセス**: `http://192.168.68.110:8181`

2. **「Access Lists」タブを開く**

3. **作成したAccess Listを編集**（例: `nas-dashboard-auth`）

4. **「Details」タブを開く**

5. **「Satisfy Any」のトグルスイッチをオン（右側にスライド）にする**
   - デフォルトではオフ（左側）になっている
   - これにより、Basic認証が成功すれば、内部ネットワークからのアクセスも許可されます

6. **「Save」をクリック**

---

### 方法2: Access Listの「Access」タブで内部ネットワークを許可

1. **Nginx Proxy ManagerのWeb UIにアクセス**: `http://192.168.68.110:8181`

2. **「Access Lists」タブを開く**

3. **作成したAccess Listを編集**

4. **「Access」タブを開く**

5. **「allow」セクションに内部ネットワークを追加**:
   - **IP**: `192.168.0.0/16`（すべての内部ネットワークを許可）
   - または、特定のネットワーク: `192.168.68.0/24`（192.168.68.xのみ許可）
   - **「Add」ボタンをクリック**

6. **「Save」をクリック**

**注意**: 「deny all」が設定されている場合は、「Satisfy Any」を有効にする必要があります。

---

### 方法3: Proxy HostのAdvancedタブで設定を追加

1. **Nginx Proxy ManagerのWeb UIにアクセス**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブを開く**

3. **`yoshi-nas-sys.duckdns.org`のProxy Hostを編集**

4. **「Advanced」タブを開く**

5. **「Custom Nginx Configuration」に以下を追加**:

```nginx
# 内部ネットワーク（RFC1918 IP）からのアクセスを許可
set_real_ip_from 192.168.0.0/16;
set_real_ip_from 10.0.0.0/8;
set_real_ip_from 172.16.0.0/12;
```

6. **「Save」をクリック**

---

## 🔄 推奨される設定手順

### ステップ1: Access Listを確認・修正

1. **「Access Lists」タブを開く**
2. **作成したAccess Listを編集**
3. **「Details」タブで「Satisfy Any」をオンにする**
4. **「Access」タブで内部ネットワークを許可**（オプション）
5. **「Save」をクリック**

### ステップ2: Proxy Hostの設定を確認

1. **「Proxy Hosts」タブを開く**
2. **`yoshi-nas-sys.duckdns.org`のProxy Hostを編集**
3. **「Access List」ドロップダウンで、作成したAccess Listが選択されていることを確認**
4. **「Save」をクリック**

### ステップ3: 動作確認

1. **内部ネットワークからアクセス**: `https://yoshi-nas-sys.duckdns.org:8443/`
2. **認証ダイアログが表示されることを確認**
3. **正しい認証情報を入力**
4. **アクセスできることを確認**

---

## 🔍 トラブルシューティング

### エラーが解消しない場合

1. **Nginx Proxy Managerコンテナを再起動**:

```bash
docker restart nginx-proxy-manager
```

2. **Nginx設定を再読み込み**:

```bash
docker exec nginx-proxy-manager nginx -t
docker exec nginx-proxy-manager nginx -s reload
```

3. **ログを確認**:

```bash
docker logs nginx-proxy-manager --tail 100 | grep -i "403\|rfc1918\|denied"
```

---

## 📋 チェックリスト

RFC1918 IPエラーが発生した場合、以下を確認：

- [ ] Access Listの「Satisfy Any」がオンになっている
- [ ] Access Listの「Access」タブで内部ネットワークが許可されている（オプション）
- [ ] Proxy HostでAccess Listが選択されている
- [ ] Nginx Proxy Managerコンテナが正常に動作している
- [ ] ブラウザのキャッシュをクリアした

---

## ⚠️ 注意事項

### セキュリティについて

内部ネットワークからのアクセスを許可する場合、セキュリティに注意してください：

1. **Basic認証を有効にする**（推奨）
2. **必要に応じてIP制限を追加**
3. **HTTPSを使用する**（推奨）

### 内部アクセスと外部アクセスの違い

- **内部アクセス**: `http://192.168.68.110:9001`（直接アクセス、認証不要）
- **外部アクセス**: `https://yoshi-nas-sys.duckdns.org:8443/`（Nginx Proxy Manager経由、Basic認証必要）

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

