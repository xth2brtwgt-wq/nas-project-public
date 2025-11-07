# 🔐 ダッシュボード認証 初期ユーザー作成手順

**作成日**: 2025-11-04  
**目的**: ダッシュボード認証システムの初期ユーザー作成手順

---

## 📋 初期ユーザー作成方法

### 方法1: 対話形式で作成（推奨）

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python scripts/create_initial_user.py
```

スクリプトが対話形式でユーザー名とパスワードを尋ねます：

```
認証データベースを初期化しています...
認証データベースを初期化しました

初期ユーザー情報を入力してください
ユーザー名 (デフォルト: admin): 
パスワード: 
```

### 方法2: 環境変数から作成

1. `.env`ファイルに以下を追加：

```bash
# 認証設定（初期ユーザー作成用）
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=your-password-here
```

2. 初期ユーザー作成スクリプトを実行：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python scripts/create_initial_user.py
```

スクリプトが環境変数から自動的に読み込みます。

---

## ✅ 動作確認

### 1. ログの確認

```bash
sudo docker compose logs nas-dashboard | grep -i "認証"
```

以下のようなログが表示されれば正常です：

```
認証データベースを初期化しました
ユーザーがログインしました: admin (user_id: 1)
```

### 2. データベースの確認

```bash
sudo docker compose exec nas-dashboard python -c "from utils.auth_db import get_all_users; import json; print(json.dumps(get_all_users(), indent=2, default=str))"
```

ユーザー一覧が表示されます。

### 3. ログインページの確認

ブラウザで以下のURLにアクセス：

- **内部アクセス**: `http://192.168.68.110:9001/`
- **外部アクセス**: `https://yoshi-nas-sys.duckdns.org:8443/`（Nginx Proxy Manager経由の場合）

ログインページが表示され、作成した初期ユーザーでログインできることを確認します。

---

## 🔍 トラブルシューティング

### エラー: `認証データベース初期化エラー`

**原因**: データベースディレクトリが存在しない、または権限がない

**解決方法**:

```bash
# データベースディレクトリを作成
sudo mkdir -p /home/AdminUser/nas-project-data/nas-dashboard
sudo chown -R 1000:1000 /home/AdminUser/nas-project-data/nas-dashboard
```

### エラー: `ユーザー名が既に存在します`

**原因**: 既に同じユーザー名が存在する

**解決方法**:

1. 既存のユーザーを確認：

```bash
sudo docker compose exec nas-dashboard python -c "from utils.auth_db import get_all_users; print(get_all_users())"
```

2. 別のユーザー名で作成するか、既存のユーザーを使用してください。

### エラー: `ログインページが表示されない`

**原因**: 認証チェックが正しく動作していない

**解決方法**:

1. アプリケーションのログを確認：

```bash
sudo docker compose logs nas-dashboard
```

2. 認証データベースが初期化されているか確認：

```bash
sudo docker compose exec nas-dashboard python -c "from utils.auth_db import init_auth_db; init_auth_db(); print('認証データベースを初期化しました')"
```

---

## 📝 注意事項

1. **初期ユーザー**: 最初のユーザーは必ず作成してください。初期ユーザーがないと、ログインできません。
2. **パスワード**: パスワードはbcryptでハッシュ化されて保存されます。平文で保存されることはありません。
3. **データベースの場所**: `/home/AdminUser/nas-project-data/nas-dashboard/auth.db`
4. **セキュリティ**: 初期ユーザーのパスワードは強力なものを使用してください。

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

