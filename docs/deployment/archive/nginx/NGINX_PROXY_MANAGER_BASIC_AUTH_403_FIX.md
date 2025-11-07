# 🔧 Nginx Proxy Manager - Basic認証 403エラー解決ガイド

**作成日**: 2025-11-02  
**目的**: Basic認証設定後に403エラーが発生する問題を解決

---

## ⚠️ 問題の症状

Basic認証を設定した後、以下のエラーが表示される：

- **403 Forbidden**
- 認証ダイアログが表示されない
- 正しい認証情報を入力してもアクセスできない

---

## 🔍 原因と解決方法

### 1. Accessタブで「deny all」が設定されている（最も多い原因）

**症状**: Basic認証を設定したのに403エラーが発生する

**確認方法**:
1. Nginx Proxy ManagerのWeb UIにアクセス: `http://192.168.68.110:8181`
2. 「Access Lists」タブを開く
3. 作成したAccess Listを編集
4. 「Access」タブを開く
5. 「deny all」が設定されていないか確認

**解決方法**:

**方法1: 「Satisfy Any」を有効にする（推奨）**

1. Access Listを編集
2. **「Details」タブを開く**
3. **「Satisfy Any」のトグルスイッチをオン（右側にスライド）にする**
4. 「Save」をクリック

**方法2: 「deny all」を削除する（「Satisfy Any」が使えない場合）**

1. Access Listを編集
2. 「Access」タブを開く
3. 「deny all」の行を削除（「×」ボタンや「Remove」ボタンをクリック）
4. IP制限が必要ない場合は、このタブの設定を空にする
5. 「Save」をクリック

**注意**: 「deny all」が削除できない場合、必ず「Satisfy Any」をオンにしてください。

---

### 2. Access Listにユーザーが追加されていない

**症状**: 403エラーが表示され、認証ダイアログが表示されない

**確認方法**:
1. Nginx Proxy ManagerのWeb UIにアクセス: `http://192.168.68.110:8181`
2. 「Access Lists」タブを開く
3. 作成したAccess Listを確認
4. 「Authorization」タブでユーザーが追加されているか確認

**解決方法**:
1. Access Listを編集
2. 「Authorization」タブを開く
3. ユーザー名とパスワードを入力
4. 「Add」ボタンをクリックしてユーザーを追加
5. 「Save」をクリック

---

### 2. Access Listが空（ユーザーが0人）

**症状**: Access Listは作成されているが、ユーザーが1人も追加されていない

**解決方法**:
1. Access Listを編集
2. 必ず1人以上のユーザーを追加
3. ユーザー名とパスワードを正しく入力
4. 「Save」をクリック

---

### 3. Proxy HostにAccess Listが正しく適用されていない

**症状**: Access Listは作成されているが、Proxy Hostの設定で選択されていない

**確認方法**:
1. 「Proxy Hosts」タブを開く
2. `yoshi-nas-sys.duckdns.org`のProxy Hostを編集
3. 「Access List」ドロップダウンを確認
4. 作成したAccess Listが選択されているか確認

**解決方法**:
1. Proxy Hostの編集画面を開く
2. 「Access List」ドロップダウンで、作成したAccess Listを選択
3. 「Save」をクリック
4. 設定が反映されるまで数秒待つ

---

### 4. Access Listの名前が間違っている

**症状**: 複数のAccess Listがある場合、間違ったものを選択している可能性

**解決方法**:
1. 「Access Lists」タブで、正しいAccess Listの名前を確認
2. Proxy Hostの編集画面で、「Access List」ドロップダウンから正しいAccess Listを選択
3. 「Save」をクリック

---

### 5. 認証情報が間違っている

**症状**: 認証ダイアログは表示されるが、認証に失敗する

**確認方法**:
1. Access Listを編集して、ユーザー名とパスワードを再確認
2. パスワードに特殊文字が含まれている場合、正しく入力されているか確認

**解決方法**:
1. パスワードを一度変更してみる（簡単なパスワードでテスト）
2. ユーザー名にスペースや特殊文字が含まれていないか確認
3. 新しいユーザーを追加してテスト

---

### 6. Nginx Proxy Managerの設定が反映されていない

**症状**: 設定を変更しても、エラーが解消されない

**解決方法**:
1. Proxy Hostの設定を一度削除して再作成
2. または、Nginx Proxy Managerコンテナを再起動:
   ```bash
   docker restart nginx-proxy-manager
   ```

---

## 🔄 再設定手順（推奨）

### ステップ1: Access Listを再作成

1. **「Access Lists」タブを開く**
2. **既存のAccess Listを削除**（問題がある場合）
3. **「Add Access List」をクリック**
4. **設定を入力**:
   - **Name**: `nas-dashboard-auth`
   - **Username**: `admin`（例）
   - **Password**: `your_strong_password`（強力なパスワード）
5. **「Save」をクリック**
6. **「Users」セクションにユーザーが追加されていることを確認**

---

### ステップ2: Proxy Hostの設定を確認・修正

1. **「Proxy Hosts」タブを開く**
2. **`yoshi-nas-sys.duckdns.org`のProxy Hostを編集**
3. **「Access List」ドロップダウンを確認**
4. **作成したAccess Listを選択**
5. **その他の設定を確認**:
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `9001`
   - **Scheme**: `http`
6. **「Save」をクリック**

---

### ステップ3: 動作確認

1. **ブラウザのキャッシュをクリア**
   - `Cmd+Shift+R`（Mac）または `Ctrl+Shift+R`（Windows）

2. **外部ネットワークからアクセス**（モバイルデータ通信など）

3. **`https://yoshi-nas-sys.duckdns.org:8443/` にアクセス**

4. **認証ダイアログが表示されることを確認**

5. **正しい認証情報を入力**

6. **nas-dashboardにアクセスできることを確認**

---

## 🧪 テスト手順

### テスト1: 内部ネットワークからアクセス

```bash
# 内部ネットワークから直接アクセス（認証なし）
curl -I http://192.168.68.110:9001

# 正常に応答することを確認
```

### テスト2: Basic認証付きでアクセス

```bash
# Basic認証付きでアクセス
curl -u admin:your_password -I https://yoshi-nas-sys.duckdns.org:8443/

# 正常に応答することを確認
```

### テスト3: 認証なしでアクセス（403エラーが出ることを確認）

```bash
# 認証なしでアクセス
curl -I https://yoshi-nas-sys.duckdns.org:8443/

# 401または403エラーが返ることを確認
```

---

## 📋 チェックリスト

403エラーが発生した場合、以下を確認：

- [ ] Access Listにユーザーが追加されている
- [ ] ユーザー名とパスワードが正しく設定されている
- [ ] Proxy HostでAccess Listが選択されている
- [ ] Proxy Hostの転送先設定（Forward Hostname/IP、Forward Port）が正しい
- [ ] Nginx Proxy Managerコンテナが正常に動作している
- [ ] 内部ネットワークから直接アクセス（`http://192.168.68.110:9001`）できる
- [ ] ブラウザのキャッシュをクリアした

---

## 🔍 詳細なトラブルシューティング

### Nginx Proxy Managerのログを確認

```bash
# Nginx Proxy Managerコンテナのログを確認
docker logs nginx-proxy-manager --tail 100 | grep -i "403\|auth\|access"

# エラーログを確認
docker logs nginx-proxy-manager --tail 100 | grep -i error
```

### 設定ファイルの確認

```bash
# Nginx Proxy Managerの設定ファイルを確認
docker exec nginx-proxy-manager cat /data/nginx/proxy_host/*/conf.d/*.conf | grep -A 10 "auth_basic"
```

### Access Listファイルの確認

```bash
# Access Listの設定を確認
docker exec nginx-proxy-manager ls -la /data/nginx/access_lists/
```

---

## ⚠️ よくある間違い

### 間違い1: Accessタブで「deny all」が設定されている（最も多い原因）

**症状**: Basic認証を設定したのに403エラーが発生する

**原因**: Access Listの「Access」タブで「deny all」が設定されているため、すべてのIPアドレスからのアクセスが拒否される

**解決方法（「deny all」が編集できない場合）**:

**方法1: 「Satisfy Any」を有効にする（推奨・最も簡単）**

「deny all」が削除できない場合、「Satisfy Any」をオンにすることで、Basic認証が成功すればアクセスできるようになります。

1. **Access Listを編集**
2. **「Details」タブを開く**
3. **「Satisfy Any」のトグルスイッチをオン（右側にスライド）にする**
   - デフォルトではオフ（左側）になっている
4. **「Save」をクリック**

**説明**: 
- 「Satisfy Any」がオフの場合、Basic認証とIP制限の**両方**を満たす必要があります（deny allがあるためアクセス拒否）
- 「Satisfy Any」がオンの場合、Basic認証**または**IP制限の**どちらか一方**を満たせばアクセスできます
- つまり、「Satisfy Any」をオンにすれば、Basic認証が成功すれば、「deny all」があってもアクセスできます

---

**方法2: Access Listを再作成（方法1が動作しない場合）**

1. **既存のAccess Listを削除**:
   - 「Access Lists」タブで`nas-dashboard-auth`を削除（ゴミ箱アイコンをクリック）
   
2. **新しいAccess Listを作成**:
   - 「Add Access List」をクリック
   - 「Details」タブ: 
     - **Name**: `nas-dashboard-auth`
     - **「Satisfy Any」のトグルスイッチをオンにする**
   - 「Authorization」タブ: ユーザー名とパスワードを入力 → **「Add」ボタンをクリック**
   - 「Access」タブには何も追加しない（「deny all」がデフォルトで入っていても問題なし）
   - 「Save」をクリック

3. **Proxy Hostに再度適用**:
   - 「Proxy Hosts」タブで`yoshi-nas-sys.duckdns.org`を編集
   - 「Access List」で新しいAccess Listを選択
   - 「Save」をクリック

**注意**: Basic認証のみでアクセス制御を行う場合は、「Satisfy Any」をオンにすることで、「deny all」があってもBasic認証でアクセスできます。

---

### 間違い2: Access Listを削除してしまった

**症状**: Access Listが存在しないため、403エラーが発生

**解決方法**: 新しいAccess Listを作成し、Proxy Hostに再適用

---

### 間違い3: パスワードに特殊文字が含まれている

**症状**: 認証ダイアログで正しいパスワードを入力しても認証に失敗

**解決方法**: パスワードを変更（特殊文字を避けるか、正しくエスケープ）

---

### 間違い4: 複数のProxy Hostがある場合、間違ったProxy Hostに設定

**症状**: Access Listは正しく設定されているが、別のProxy Hostに設定されている

**解決方法**: 正しいProxy Host（`yoshi-nas-sys.duckdns.org`）にAccess Listを適用

---

## 📚 参考資料

- [Nginx Proxy Manager - Basic認証設定ガイド](NGINX_PROXY_MANAGER_BASIC_AUTH_SETUP.md)
- [Nginx Proxy Manager公式ドキュメント - Access Lists](https://nginxproxymanager.com/guide/#access-lists)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

