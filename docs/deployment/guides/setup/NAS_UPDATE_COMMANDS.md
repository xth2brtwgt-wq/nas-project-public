# NAS既存プロジェクトの更新手順

## 🔄 既存プロジェクトを最新版に更新

既にプロジェクトがある場合は、git pullで更新します。

---

## NASで実行するコマンド

```bash
# プロジェクトディレクトリに移動
cd ~/nas-project

# 現在のブランチを確認
git branch

# リモートの最新を取得
git fetch origin

# ローカルの変更を確認（あれば保存）
git status

# ローカルの変更を退避（必要な場合）
git stash

# 最新版にアップデート
git pull origin main

# 更新内容を確認
git log --oneline -10

# 最新のファイル構造を確認
ls -la
```

---

## ✅ 実行後の確認

以下のファイル・フォルダが存在するはず：

```
- amazon-analytics/      (新規)
- document-automation/   (既存)
- insta360-auto-sync/    (既存)
- meeting-minutes-byc/   (更新済み)
- docs/                  (新規)
- QUICK_DEPLOY.md        (新規)
- FINAL_CLEANUP_REPORT.md (新規)
```

以下は削除されているはず：

```
✗ app.py (ルート - meeting-minutes-byc/に統合済み)
✗ check_models.py (削除済み)
✗ .env (ルート - 各プロジェクトに移動済み)
✗ deploy-nas.sh (ルート - meeting-minutes-byc/に移動予定)
✗ version.py (ルート - 削除済み)
✗ scripts/ (ルート - insta360-auto-sync/に移動済み)
✗ nas-dashboard/ (削除済み)
```

