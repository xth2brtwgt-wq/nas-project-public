# 🔧 ダッシュボードタイトルが更新されない場合の対処法

**作成日**: 2025-11-04  
**目的**: タイトル変更が反映されない問題の解決

---

## 🔍 問題

タイトルを「NAS-System」に変更したが、ブラウザで表示されない。

---

## ✅ 解決手順

### ステップ1: NAS上のファイル内容を確認

まず、NAS上のファイルが正しく更新されているか確認します：

```bash
cd ~/nas-project/nas-dashboard

# login.html の内容を確認
grep -n "NAS" templates/login.html | head -5

# dashboard.html の内容を確認
grep -n "NAS" templates/dashboard.html | head -5

# users.html の内容を確認
grep -n "NAS" templates/users.html | head -5
```

「NAS統合管理ダッシュボード」が表示される場合は、ファイルが更新されていません。  
「NAS-System」が表示される場合は、ファイルは正しく更新されています。

### ステップ2: Gitの状態を確認

```bash
cd ~/nas-project/nas-dashboard
git status
git log --oneline -5
```

最新のコミット（「fix: タイトルを「NAS-System」に統一」）が表示されることを確認してください。

### ステップ3: 最新コードを取得

```bash
cd ~/nas-project/nas-dashboard
git pull origin feature/monitoring-fail2ban-integration
```

### ステップ4: Dockerコンテナ内のファイルを確認

コンテナ内のファイルが正しくマウントされているか確認します：

```bash
cd ~/nas-project/nas-dashboard

# コンテナ内のlogin.htmlを確認
sudo docker compose exec nas-dashboard cat /nas-project/nas-dashboard/templates/login.html | grep -A 2 "NAS"

# または、コンテナ内で直接確認
sudo docker compose exec nas-dashboard bash -c "grep 'NAS' /nas-project/nas-dashboard/templates/login.html | head -3"
```

### ステップ5: 完全な再ビルド（推奨）

ファイルが正しく更新されているにもかかわらずタイトルが変わらない場合、Dockerイメージを完全に再ビルドします：

```bash
cd ~/nas-project/nas-dashboard

# コンテナを停止・削除
sudo docker compose down

# キャッシュを使わずにイメージを再ビルド
sudo docker compose build --no-cache

# 新しいイメージでコンテナを起動
sudo docker compose up -d

# 起動ログを確認
sudo docker compose logs nas-dashboard | tail -20
```

### ステップ6: ブラウザのキャッシュを完全にクリア

1. **シークレットモード/プライベートブラウジング**でアクセス：
   - Safari: `Cmd + Shift + N`
   - Chrome/Edge: `Cmd + Shift + N`

2. **強制リロード**:
   - `Cmd + Shift + R` (Mac) または `Ctrl + Shift + R` (Windows)

3. **開発者ツールでキャッシュを無効化**:
   - `Cmd + Option + I` (開発者ツールを開く)
   - Networkタブで「Disable cache」をチェック
   - ページをリロード

### ステップ7: 確認

以下のURLにアクセスし、タイトルが「NAS-System」になっていることを確認してください：

- 外部アクセス: `https://yoshi-nas-sys.duckdns.org:8443/`
- 内部アクセス: `http://192.168.68.110:9001/`

---

## 🔍 トラブルシューティング

### ファイルが更新されていない場合

```bash
cd ~/nas-project/nas-dashboard

# 手動でファイルを確認
cat templates/login.html | grep "NAS-System"

# もし「NAS統合管理ダッシュボード」が表示される場合
# ファイルを直接編集するか、Gitから正しいバージョンを取得
git checkout feature/monitoring-fail2ban-integration -- templates/login.html
git checkout feature/monitoring-fail2ban-integration -- templates/dashboard.html
git checkout feature/monitoring-fail2ban-integration -- templates/users.html
git checkout feature/monitoring-fail2ban-integration -- templates/users_add.html
git checkout feature/monitoring-fail2ban-integration -- templates/users_edit.html
git checkout feature/monitoring-fail2ban-integration -- templates/log_viewer.html
```

### コンテナ内のファイルが更新されていない場合

Docker Composeのボリュームマウント設定を確認：

```bash
cd ~/nas-project/nas-dashboard
cat docker-compose.yml | grep -A 5 volumes
```

`/home/AdminUser/nas-project`が`/nas-project:ro`としてマウントされていることを確認してください。

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

