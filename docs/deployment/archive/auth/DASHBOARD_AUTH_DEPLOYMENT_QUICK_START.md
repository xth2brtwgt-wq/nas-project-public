# 🔐 ダッシュボード認証統合 クイックスタートガイド

**作成日**: 2025-11-04  
**目的**: ダッシュボード認証統合機能の簡単なデプロイメント手順

---

## 📋 NAS環境でのデプロイメント手順

### ステップ1: プロジェクトディレクトリに移動

```bash
cd ~/nas-project/nas-dashboard
```

### ステップ2: コードのプル（既に完了している場合）

```bash
cd ~/nas-project
git pull origin feature/monitoring-fail2ban-integration
cd nas-dashboard
```

### ステップ3: コンテナの状態確認

```bash
sudo docker compose ps
```

コンテナが起動していない場合は、起動します：

```bash
sudo docker compose up -d
```

### ステップ4: 依存関係のインストール（bcrypt）

サービス名は`nas-dashboard`です（`web`ではありません）：

```bash
sudo docker compose exec nas-dashboard pip install bcrypt==4.0.1
```

または、コンテナを再ビルドする場合：

```bash
sudo docker compose build
sudo docker compose up -d
```

### ステップ5: コンテナの再起動（docker-compose.ymlの変更を反映）

```bash
sudo docker compose restart nas-dashboard
```

### ステップ6: 初期ユーザーの作成

```bash
sudo docker compose exec nas-dashboard python scripts/create_initial_user.py
```

スクリプトが対話形式でユーザー名とパスワードを尋ねます：

```
ユーザー名 (デフォルト: admin): 
パスワード: 
```

### ステップ7: ログの確認

```bash
sudo docker compose logs nas-dashboard | grep -i "認証"
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

---

## 🔍 トラブルシューティング

### エラー: `service "web" is not running`

**原因**: サービス名が間違っている、またはコンテナが起動していない

**解決方法**:

1. コンテナの状態を確認：

```bash
sudo docker compose ps
```

2. コンテナが起動していない場合は起動：

```bash
sudo docker compose up -d
```

3. 正しいサービス名を使用：

```bash
# サービス名は nas-dashboard です
sudo docker compose exec nas-dashboard pip install bcrypt==4.0.1
```

### エラー: `ModuleNotFoundError: No module named 'bcrypt'`

**原因**: `bcrypt`がインストールされていない

**解決方法**:

```bash
sudo docker compose exec nas-dashboard pip install bcrypt==4.0.1
sudo docker compose restart nas-dashboard
```

### エラー: `認証データベース初期化エラー`

**原因**: データベースディレクトリが存在しない、または権限がない

**解決方法**:

```bash
# データベースディレクトリを作成
sudo mkdir -p /home/AdminUser/nas-project-data/nas-dashboard
sudo chown -R 1000:1000 /home/AdminUser/nas-project-data/nas-dashboard
```

---

## 📝 注意事項

1. **サービス名**: `docker-compose.yml`のサービス名は`nas-dashboard`です（`web`ではありません）
2. **コンテナ名**: コンテナ名も`nas-dashboard`です
3. **データベースの場所**: `/home/AdminUser/nas-project-data/nas-dashboard/auth.db`
4. **初期ユーザー**: 最初のユーザーは必ず作成してください

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

