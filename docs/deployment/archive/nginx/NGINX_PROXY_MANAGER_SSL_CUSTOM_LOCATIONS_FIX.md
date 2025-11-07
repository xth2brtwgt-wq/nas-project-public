# 🔧 Nginx Proxy Manager - Custom Locations使用時のSSL設定修正

**作成日**: 2025-11-02  
**対象**: Custom Locationsを使用している場合のSSL設定問題の解決

---

## 📋 問題

Custom Locationsを追加した後、SSL接続エラーが発生する。

---

## 🔍 原因

Custom Locationsを使用している場合、**メインのProxy Host設定（Detailsタブ）のSSL設定が適用されない可能性**があります。

**解決方法**: Custom Locationsを使用している場合でも、DetailsタブのSSL設定が正しく適用されることを確認する必要があります。

---

## 🔧 解決方法

### 方法1: Detailsタブの設定を確認

1. **Proxy Hostsタブを開く**
2. **`yoshi-nas-sys.duckdns.org`の設定を開く**
3. **「Details」タブを確認**:
   - **Domain Names**: `yoshi-nas-sys.duckdns.org` が設定されているか
   - **Forward Hostname/IP**: 空欄または設定されているか
   - **Forward Port**: 空欄または設定されているか

4. **「SSL」タブを確認**:
   - **SSL Certificate**: Let's Encrypt証明書が選択されているか
   - **Force SSL**: ✅オンになっているか

5. **「Save」をクリック**

---

### 方法2: Custom Locationsの各LocationにSSL設定を追加（必要な場合）

Custom Locationsを使用している場合、各LocationにもSSL設定が必要になる場合があります。

**通常は不要**ですが、問題が続く場合は以下を試してください：

1. **Custom Locationsタブを開く**
2. **各Locationの歯車アイコン（⚙️）をクリック**
3. **詳細設定でSSL設定を確認**（通常は親Proxy Hostの設定が継承される）

---

### 方法3: Nginx設定を確認

Nginx設定ファイルが正しく生成されているか確認：

```bash
docker exec nginx-proxy-manager nginx -t
```

**期待される結果**: `syntax is ok` と `test is successful`

---

### 方法4: Proxy Hostを再作成（最終手段）

問題が続く場合、Proxy Hostを再作成する必要があるかもしれません：

1. **既存のProxy Hostを削除**
2. **新しいProxy Hostを作成**:
   - Domain Names: `yoshi-nas-sys.duckdns.org`
   - Detailsタブで転送先を設定
   - SSLタブで証明書を設定
   - Custom Locationsタブで各Locationを追加

---

## ✅ 確認事項

### Detailsタブの設定

- **Domain Names**: `yoshi-nas-sys.duckdns.org` ✅
- **Forward Hostname/IP**: 設定されているか（または空欄でもOK） ✅
- **Forward Port**: 設定されているか（または空欄でもOK） ✅

### SSLタブの設定

- **SSL Certificate**: Let's Encrypt証明書が選択されている ✅
- **Force SSL**: ✅オン ✅
- **HTTP/2 Support**: ✅オン ✅
- **HSTS Enabled**: ✅オン ✅

---

## 🔍 トラブルシューティング

### 証明書が選択されているのに接続できない場合

**原因**: Nginx設定が正しく生成されていない、または再読み込みされていない

**対処法**:
1. Proxy Hostの設定を再保存（「Save」をクリック）
2. Nginx Proxy Managerコンテナを再起動
3. Nginx設定を確認: `docker exec nginx-proxy-manager nginx -t`

### Custom LocationsでSSLエラーが発生する場合

**原因**: Custom Locationsを使用している場合、SSL設定が正しく継承されていない

**対処法**:
1. DetailsタブのSSL設定を確認
2. SSLタブで「Force SSL」がオンになっていることを確認
3. 設定を再保存

---

## 📝 まとめ

Custom Locationsを使用している場合のSSL設定：

1. **Detailsタブ**: Domain Names、Forward Hostname/IP、Forward Portを設定
2. **SSLタブ**: SSL証明書を選択し、「Force SSL」をオンにする
3. **Custom Locationsタブ**: 各Locationを追加（SSL設定は親Proxy Hostから継承される）

**重要なポイント**:
- Custom Locationsを使用している場合でも、DetailsタブとSSLタブの設定が重要
- 設定を変更したら必ず「Save」をクリック
- 問題が続く場合はNginx Proxy Managerコンテナを再起動

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

