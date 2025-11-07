# Permission deniedエラーの修正手順

## 📋 問題

`nas-dashboard/logs/app.log`の削除でPermission deniedエラーが発生しています。

```bash
rm: cannot remove 'logs/app.log': Permission denied
```

## 🔍 原因

- Dockerコンテナが実行中に作成したファイルは、通常rootユーザーで作成される
- ファイルの所有者がrootになっている可能性がある
- コンテナを停止しても、ファイルの所有者は変更されない

## ✅ 解決策

### オプション1: sudo権限で削除（推奨）

```bash
# NAS環境で実行
cd ~/nas-project/nas-dashboard

# コンテナを停止
docker compose down

# sudo権限で削除
sudo rm -rf logs/

# コンテナを再起動
docker compose up -d
```

### オプション2: ファイルの所有者を変更してから削除

```bash
# NAS環境で実行
cd ~/nas-project/nas-dashboard

# コンテナを停止
docker compose down

# ファイルの所有者を変更
sudo chown -R AdminUser:admin logs/

# 削除
rm -rf logs/

# コンテナを再起動
docker compose up -d
```

### オプション3: ファイルの権限を変更してから削除

```bash
# NAS環境で実行
cd ~/nas-project/nas-dashboard

# コンテナを停止
docker compose down

# ファイルの権限を変更
sudo chmod -R 755 logs/
sudo chown -R AdminUser:admin logs/

# 削除
rm -rf logs/

# コンテナを再起動
docker compose up -d
```

## 🔧 推奨手順

```bash
# NAS環境で実行
cd ~/nas-project/nas-dashboard

# 1. コンテナを停止
docker compose down

# 2. ログファイルを削除（sudo権限で）
sudo rm -rf logs/

# 3. コンテナを再起動
docker compose up -d

# 4. 確認
ls -la logs/ 2>/dev/null || echo "✅ logsディレクトリが削除されました"
```

## 📋 確認方法

削除後、以下で確認：

```bash
# プロジェクト内にlogsディレクトリがないことを確認
ls -la ~/nas-project/nas-dashboard/logs 2>/dev/null || echo "✅ logsディレクトリが削除されました"

# または、確認スクリプトを実行
cd ~/nas-project
~/nas-project/scripts/verify-deployment.sh
```

## ⚠️ 注意事項

- コンテナを停止してから削除する必要があります
- ファイルの所有者がrootの場合は、sudo権限が必要です
- 削除後、コンテナを再起動すると、新しいログファイルは`nas-project-data/nas-dashboard/logs/`に保存されます

## 🔗 関連ドキュメント

- [残りの問題の修正手順](./FIX_REMAINING_ISSUES.md)
- [最終ステータスと残りのクリーンアップ](./FINAL_STATUS_AND_CLEANUP.md)

---

**作成日**: 2025年11月6日
**対象**: nas-dashboard
**更新**: 必要に応じて更新

