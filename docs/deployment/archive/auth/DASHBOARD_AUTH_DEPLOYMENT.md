# 🔐 ダッシュボード認証統合 デプロイメント手順

**作成日**: 2025-11-04  
**目的**: ダッシュボード認証統合機能のデプロイメントと動作確認

---

## 📋 前提条件

1. NAS環境で`nas-dashboard`プロジェクトが稼働していること
2. `bcrypt==4.0.1`がインストールされていること（`requirements.txt`に追加済み）
3. 認証データベース用のディレクトリが存在すること（`/home/AdminUser/nas-project-data/nas-dashboard/`）

---

## 🚀 デプロイメント手順

### ステップ1: コードのプル

NAS環境で最新のコードをプルします：

```bash
cd /nas-project
git pull origin feature/monitoring-fail2ban-integration
```

### ステップ2: 依存関係のインストール

`bcrypt`をインストールします：

```bash
cd /nas-project/nas-dashboard
sudo docker compose exec web pip install bcrypt==4.0.1
```

または、コンテナを再ビルドする場合：

```bash
cd /nas-project/nas-dashboard
sudo docker compose build
sudo docker compose up -d
```

### ステップ3: 認証データベースの初期化

認証データベースは、アプリケーション起動時に自動的に初期化されます。

ただし、手動で初期化する場合は：

```bash
cd /nas-project/nas-dashboard
sudo docker compose exec web python -c "from utils.auth_db import init_auth_db; init_auth_db(); print('認証データベースを初期化しました')"
```

### ステップ4: 初期ユーザーの作成

初期ユーザーを作成する方法は2つあります：

#### 方法1: 環境変数から作成（推奨）

1. `.env`ファイルに以下を追加：

```bash
# 認証設定（初期ユーザー作成用）
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=your-password-here
```

2. 初期ユーザー作成スクリプトを実行：

```bash
cd /nas-project/nas-dashboard
sudo docker compose exec web python scripts/create_initial_user.py
```

#### 方法2: 対話形式で作成

```bash
cd /nas-project/nas-dashboard
sudo docker compose exec web python scripts/create_initial_user.py
```

スクリプトが対話形式でユーザー名とパスワードを尋ねます。

### ステップ5: アプリケーションの再起動

変更を反映するために、アプリケーションを再起動します：

```bash
cd /nas-project/nas-dashboard
sudo docker compose restart web
```

### ステップ6: ログの確認

アプリケーションのログを確認して、認証データベースが正常に初期化されたことを確認します：

```bash
cd /nas-project/nas-dashboard
sudo docker compose logs web | grep -i "認証"
```

以下のようなログが表示されれば正常です：

```
認証データベースを初期化しました
```

---

## ✅ 動作確認

### 1. ログインページの確認

ブラウザで以下のURLにアクセス：

- **内部アクセス**: `http://192.168.68.110:9001/`
- **外部アクセス**: `https://yoshi-nas-sys.duckdns.org:8443/`（Nginx Proxy Manager経由の場合）

ログインページが表示されることを確認します。

### 2. ログイン機能の確認

1. 初期ユーザーでログインします
2. ダッシュボードにリダイレクトされることを確認します
3. ナビゲーションバーに「ユーザー管理」と「ログアウト」リンクが表示されることを確認します

### 3. ユーザー管理画面の確認

1. ナビゲーションバーの「ユーザー管理」をクリック
2. ユーザー一覧が表示されることを確認します
3. 「ユーザー追加」ボタンをクリックして、新しいユーザーを追加します
4. 追加したユーザーが一覧に表示されることを確認します

### 4. ユーザー追加機能の確認

1. 「ユーザー追加」ボタンをクリック
2. ユーザー名とパスワードを入力してユーザーを追加します
3. ユーザー一覧に戻り、追加したユーザーが表示されることを確認します

### 5. ユーザー編集機能の確認

1. ユーザー一覧で「編集」ボタンをクリック
2. ユーザー名を変更して保存します
3. 変更が反映されることを確認します

### 6. ログアウト機能の確認

1. ナビゲーションバーの「ログアウト」をクリック
2. ログインページにリダイレクトされることを確認します

### 7. セッション管理の確認

1. ログイン後、30分間何もしない状態を維持します
2. 30分後にページをリロードします
3. ログインページにリダイレクトされることを確認します（セッションタイムアウト）

---

## 🔍 トラブルシューティング

### エラー: `ModuleNotFoundError: No module named 'bcrypt'`

**原因**: `bcrypt`がインストールされていない

**解決方法**:

```bash
cd /nas-project/nas-dashboard
sudo docker compose exec web pip install bcrypt==4.0.1
sudo docker compose restart web
```

### エラー: `認証データベース初期化エラー`

**原因**: データベースディレクトリが存在しない、または権限がない

**解決方法**:

```bash
# データベースディレクトリを作成
sudo mkdir -p /home/AdminUser/nas-project-data/nas-dashboard
sudo chown -R 1000:1000 /home/AdminUser/nas-project-data/nas-dashboard
```

### エラー: `ログイン失敗`

**原因**: ユーザーが存在しない、またはパスワードが間違っている

**解決方法**:

1. 初期ユーザーが作成されているか確認：

```bash
cd /nas-project/nas-dashboard
sudo docker compose exec web python scripts/create_initial_user.py
```

2. データベースを直接確認：

```bash
cd /nas-project/nas-dashboard
sudo docker compose exec web python -c "from utils.auth_db import get_all_users; print(get_all_users())"
```

### エラー: `ログインページが表示されない`

**原因**: 認証チェックが正しく動作していない

**解決方法**:

1. アプリケーションのログを確認：

```bash
cd /nas-project/nas-dashboard
sudo docker compose logs web
```

2. 認証データベースが初期化されているか確認：

```bash
cd /nas-project/nas-dashboard
sudo docker compose exec web python -c "from utils.auth_db import init_auth_db; init_auth_db()"
```

---

## 📝 注意事項

1. **セッションタイムアウト**: デフォルトで30分に設定されています。変更する場合は`app.py`の`timedelta(minutes=30)`を修正してください。

2. **パスワード管理**: パスワードはbcryptでハッシュ化されて保存されます。平文で保存されることはありません。

3. **データベースの場所**: 
   - NAS環境: `/home/AdminUser/nas-project-data/nas-dashboard/auth.db`
   - ローカル環境: `nas-dashboard/data/auth.db`

4. **初期ユーザー**: 最初のユーザーは必ず作成してください。初期ユーザーがないと、ログインできません。

---

## 🎯 次のステップ

動作確認が完了したら、以下の作業を進めます：

1. **共通認証モジュールの作成**（`common/auth_middleware.py`）
2. **各サービス側への認証ミドルウェア追加**
3. **Nginx Proxy ManagerのBasic認証の削除**（トークン認証が正常に動作することを確認後）

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

