# 🔐 Nginx Proxy Manager Basic認証の無効化

**作成日**: 2025-11-04  
**目的**: ダッシュボード認証統合後、Nginx Proxy ManagerのBasic認証を無効化する手順

---

## 📋 前提条件

1. ダッシュボード認証統合が正常に動作していること
2. 初期ユーザーが作成されていること
3. アプリケーション側のログインページが表示されること

---

## 🚀 Basic認証の無効化手順

### ステップ1: Nginx Proxy Managerにアクセス

1. Nginx Proxy ManagerのWeb UIにアクセス：
   - **URL**: `http://192.168.68.110:8181`
2. ログインします

### ステップ2: Proxy Hostの編集

1. **Proxy Hosts**メニューをクリック
2. `yoshi-nas-sys.duckdns.org:8443`のProxy Hostを選択
3. **Edit**ボタンをクリック

### ステップ3: Access Listの削除

1. **Access List**タブをクリック
2. 現在設定されているAccess Listを削除：
   - ドロップダウンから「None」を選択
   - または、Access Listのチェックボックスを外す
3. **Save**ボタンをクリック

### ステップ4: 動作確認

1. ブラウザでアクセス：
   - **外部アクセス**: `https://yoshi-nas-sys.duckdns.org:8443/`
2. Basic認証のダイアログが表示されないことを確認
3. ダッシュボードのログインページが表示されることを確認

---

## ✅ 動作確認

### 1. Basic認証の無効化確認

- [ ] Basic認証のダイアログが表示されない
- [ ] ダッシュボードのログインページが直接表示される
- [ ] ログインページのデザインが正しく表示される

### 2. アプリケーション側の認証確認

- [ ] 初期ユーザー（`admin`）でログインできる
- [ ] ダッシュボードにリダイレクトされる
- [ ] ナビゲーションバーに「ユーザー管理」と「ログアウト」リンクが表示される

### 3. セキュリティ確認

- [ ] ログインしていない状態でダッシュボードにアクセスできない
- [ ] ログアウト後、再度ログインページが表示される
- [ ] セッションタイムアウトが正常に動作する

---

## 🔍 トラブルシューティング

### エラー: Basic認証のダイアログが表示され続ける

**原因**: Access Listが正しく削除されていない

**解決方法**:

1. Nginx Proxy ManagerでProxy Hostを再度編集
2. **Access List**タブで「None」を選択
3. **Save**ボタンをクリック
4. ブラウザのキャッシュをクリアして再アクセス

### エラー: ログインページが表示されない

**原因**: アプリケーション側の認証が正しく動作していない

**解決方法**:

1. アプリケーションのログを確認：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose logs nas-dashboard | grep -i "認証\|auth\|session\|login"
```

2. アプリケーションを再起動：

```bash
sudo docker compose restart nas-dashboard
```

### エラー: ログインできない

**原因**: 初期ユーザーが作成されていない、またはパスワードが間違っている

**解決方法**:

1. 初期ユーザーを再作成：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python /nas-project/nas-dashboard/scripts/create_initial_user.py
```

2. 正しいパスワードでログインしてください

---

## 📝 注意事項

1. **セキュリティ**: Basic認証を無効化した後は、アプリケーション側の認証のみで保護されます
2. **セッション管理**: セッションタイムアウトは30分に設定されています
3. **パスワード管理**: パスワードはbcryptでハッシュ化されて保存されます
4. **データベース**: 認証データベースは`/home/AdminUser/nas-project-data/nas-dashboard/auth.db`に保存されます

---

## 🎯 次のステップ

Basic認証を無効化した後、以下の作業を進めます：

1. **各サービス側への認証ミドルウェア追加**
   - 各サービス（meeting-minutes-byc、amazon-analytics、など）に認証ミドルウェアを追加
   - ダッシュボード経由でのみアクセス可能にする

2. **共通認証モジュールの作成**
   - 各サービスで使用する共通認証モジュールを作成

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

