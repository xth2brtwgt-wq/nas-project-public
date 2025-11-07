# 🔒 Nginx Proxy Manager - Basic認証設定ガイド

**作成日**: 2025-11-02  
**目的**: 外部アクセスにBasic認証を追加してセキュリティを強化

---

## ⚠️ 現在の状態

**URLを知っている人は誰でもアクセスできます**

- `https://yoshi-nas-sys.duckdns.org:8443/` → 認証なしでアクセス可能
- nas-dashboard自体には認証機能がありません

---

## 🔐 Basic認証の設定手順

### ステップ1: Nginx Proxy ManagerのWeb UIにアクセス

```bash
# 内部ネットワークからアクセス
http://192.168.68.110:8181
```

**ログイン情報**:
- メールアドレス: `admin@example.com`（初期設定）
- パスワード: 設定時に作成したパスワード

---

### ステップ2: Access List（アクセスリスト）を作成

1. **左メニューから「Access Lists」をクリック**

2. **「Add Access List」をクリック**

3. **「Details」タブで名前を設定**:
   - **Name**: `nas-dashboard-auth`（任意の名前）
   - **「Satisfy Any」のトグルスイッチをオン（右側にスライド）にする**
     - **重要**: 「deny all」が削除できない場合、この設定によりBasic認証でアクセスできます
   - 「Save」をクリック

4. **「Authorization」タブでユーザーを追加**:
   - **Username**: 任意のユーザー名（例: `admin`）
   - **Password**: **強力なパスワード**を入力
     - 推奨: 12文字以上、大文字・小文字・数字・記号を含む
   - **「Add」ボタンをクリック**（ユーザーを追加）
   - **重要**: 「Authorization」タブの「Add」ボタンをクリックしないと、ユーザーが追加されません

5. **「Access」タブを確認**:
   - **「Access」タブに「deny all」が表示されている場合**:
     - **重要**: 「deny all」が削除できない場合は、**「Details」タブの「Satisfy Any」をオンにしてください**
     - 「Satisfy Any」がオンの場合、Basic認証が成功すれば「deny all」があってもアクセスできます
   - IP制限が必要な場合のみ、このタブで設定してください
   - Basic認証のみでアクセス制御を行う場合は、このタブの設定は無視して問題ありません（「Satisfy Any」がオンであれば）

6. **「Save」をクリック**

---

### ステップ3: Proxy HostにAccess Listを適用

1. **左メニューから「Proxy Hosts」をクリック**

2. **「yoshi-nas-sys.duckdns.org」のProxy Hostをクリック**（または歯車アイコンで編集）

3. **「Access List」ドロップダウンを開く**

4. **作成したAccess List（`nas-dashboard-auth`）を選択**

5. **「Save」をクリック**

---

### ステップ4: 動作確認

1. **外部ネットワークからアクセス**（モバイルデータ通信など）

2. **ブラウザで `https://yoshi-nas-sys.duckdns.org:8443/` を開く**

3. **認証ダイアログが表示されることを確認**

4. **設定したユーザー名とパスワードを入力**

5. **nas-dashboardにアクセスできることを確認**

---

## ✅ 設定完了後の動作

### 認証が有効になった場合

- **初回アクセス時**: ブラウザが認証ダイアログを表示
- **認証成功後**: ブラウザが認証情報を保存（セッション期間中）
- **再アクセス時**: ブラウザが自動的に認証情報を送信

### 認証失敗時

- **401 Unauthorized**: 認証が必要
- **403 Forbidden**: アクセス拒否

---

## 🔧 複数ユーザーの追加

複数のユーザーにアクセスを許可したい場合：

1. **「Access Lists」で既存のAccess Listを編集**

2. **「Add User」をクリック**

3. **新しいユーザー名とパスワードを入力**

4. **「Save」をクリック**

---

## 🔄 Access Listの管理

### Access Listの編集

1. **「Access Lists」で対象のAccess Listをクリック**
2. **ユーザーの追加・削除・パスワード変更が可能**

### Access Listの無効化

1. **Proxy Hostの編集画面を開く**
2. **「Access List」を「None」に変更**
3. **「Save」をクリック**

---

## ⚠️ 注意事項

### Basic認証の制限事項

1. **パスワードが平文で送信される**
   - ⚠️ **HTTPSを使用しているため、通信は暗号化されています**
   - ✅ 現在の設定（HTTPS）では問題ありません

2. **ブラウザが認証情報を保存する**
   - セキュリティ上の懸念がある場合は、定期的にパスワードを変更

3. **セッション管理がブラウザ依存**
   - ログアウト機能がない（ブラウザを閉じるだけではログアウトできない）

### より強力な認証が必要な場合

- **OAuth2 / OIDC認証**: Nginx Proxy Manager Proで利用可能
- **アプリケーションレベルの認証**: nas-dashboardにログイン機能を実装

---

## 🔐 追加のセキュリティ対策

Basic認証と併用して、以下の対策も実施することを推奨します：

### 1. IP制限（特定のIPからのみアクセス）

詳細は`docs/deployment/NGINX_PROXY_MANAGER_IP_RESTRICTION.md`を参照。

### 2. セキュリティヘッダーの設定

詳細は`docs/deployment/EXTERNAL_ACCESS_SECURITY.md`の「3. Nginx Proxy Managerでのセキュリティヘッダー設定」を参照。

### 3. Fail2banの設定

詳細は`docs/deployment/EXTERNAL_ACCESS_SECURITY.md`の「2. Fail2banの設定」を参照。

---

## 📝 チェックリスト

Basic認証設定前の確認：

- [ ] Nginx Proxy ManagerのWeb UIにアクセスできる
- [ ] Proxy Hostが正常に動作している
- [ ] 強力なパスワードを用意した

Basic認証設定後の確認：

- [ ] Access Listが作成された
- [ ] Proxy HostにAccess Listが適用された
- [ ] 外部からアクセスして認証ダイアログが表示される
- [ ] 正しい認証情報でアクセスできる
- [ ] 間違った認証情報でアクセスできない

---

## 🧪 トラブルシューティング

### 403エラーが発生する場合

**詳細なトラブルシューティングガイド**:
- [Nginx Proxy Manager - Basic認証 403エラー解決ガイド](NGINX_PROXY_MANAGER_BASIC_AUTH_403_FIX.md)

**よくある原因**:
1. Access Listにユーザーが追加されていない
2. Access ListがProxy Hostに正しく適用されていない
3. 認証情報が間違っている

---

### 認証ダイアログが表示されない

1. **Proxy Hostの設定を確認**
   - 「Access List」が選択されているか確認

2. **ブラウザのキャッシュをクリア**
   - 一度アクセスした後は、ブラウザが認証情報をキャッシュしている可能性

3. **Nginx Proxy Managerの設定を再保存**
   - Proxy Hostを一度編集して「Save」をクリック

---

### 認証に成功してもアクセスできない

1. **Proxy Hostの転送先を確認**
   - 「Forward Hostname/IP」と「Forward Port」が正しいか確認

2. **内部ネットワークから直接アクセス**
   - `http://192.168.68.110:9001` が正常に動作するか確認

---

### 複数ユーザーでアクセスできない

1. **Access Listに複数ユーザーが追加されているか確認**
2. **各ユーザーのパスワードが正しいか確認**

---

## 📚 参考資料

- [Nginx Proxy Manager公式ドキュメント - Access Lists](https://nginxproxymanager.com/guide/#access-lists)
- [外部アクセス時のセキュリティ対策ガイド](EXTERNAL_ACCESS_SECURITY.md)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

