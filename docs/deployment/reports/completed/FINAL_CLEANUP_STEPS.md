# 最終クリーンアップ手順

## 📋 概要

残りのクリーンアップと最終確認の手順です。

## 🚀 NAS環境で実行する手順

### 1. 最新コードを取得

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# プロジェクトディレクトリに移動
cd ~/nas-project

# 最新のコードを取得
git pull origin main
```

### 2. nas-dashboardの再デプロイ

```bash
# nas-dashboardディレクトリに移動
cd ~/nas-project/nas-dashboard

# コンテナを停止
docker compose down

# 再ビルド・起動
docker compose up -d --build

# 動作確認
sleep 5
docker compose ps
```

### 3. 残りのクリーンアップ

```bash
# プロジェクトディレクトリに戻る
cd ~/nas-project

# 全プロジェクトのクリーンアップスクリプトを実行
~/nas-project/scripts/cleanup-all-projects.sh
```

このスクリプトで以下が削除されます：
- ルートレベルの`data/reports`ディレクトリ（nas-project-data/nas-dashboard/reportsに移行）
- 残っている生成物ディレクトリ

### 4. 手動で削除（もし残っている場合）

```bash
# nas-dashboard/logsを削除（もし残っている場合）
rm -rf ~/nas-project/nas-dashboard/logs

# data/reportsを削除（もし残っている場合）
rm -rf ~/nas-project/data/reports
```

### 5. amazon-analyticsとdocument-automationの起動確認

#### amazon-analytics

```bash
cd ~/nas-project/amazon-analytics

# .envファイルを確認
ls -la .env .env.restore

# .envファイルがない場合は作成
if [ ! -f .env ]; then
    if [ -f .env.restore ]; then
        cp .env.restore .env
    elif [ -f env.example ]; then
        cp env.example .env
        echo "NAS_MODE=true" >> .env
    fi
fi

# コンテナを再起動
docker compose down
docker compose up -d --build

# ログを確認
docker compose logs -f web
```

#### document-automation

```bash
cd ~/nas-project/document-automation

# .envファイルを確認
ls -la .env .env.restore

# .envファイルがない場合は作成
if [ ! -f .env ]; then
    if [ -f .env.restore ]; then
        cp .env.restore .env
    elif [ -f env.example ]; then
        cp env.example .env
        echo "NAS_MODE=true" >> .env
    fi
fi

# コンテナを再起動
docker compose down
docker compose up -d --build

# ログを確認
docker compose logs -f web
```

### 6. 最終確認

```bash
# デプロイ確認スクリプトを実行
~/nas-project/scripts/verify-deployment.sh

# 容量確認スクリプトを実行
~/nas-project/scripts/check-disk-usage.sh

# プロジェクト内に生成物がないことを確認
find ~/nas-project -type d \( -name "logs" -o -name "data" -o -name "uploads" -o -name "cache" \) | grep -v ".git" | grep -v "node_modules" | grep -v "venv"

# ログファイルが正しい場所に書き込まれているか確認
ls -lh /home/AdminUser/nas-project-data/*/logs/app.log
```

## 📋 チェックリスト

- [ ] 最新コードを取得（git pull）
- [ ] nas-dashboardの再デプロイ
- [ ] 残りのクリーンアップスクリプトを実行
- [ ] 手動で残りの生成物を削除（もし残っている場合）
- [ ] amazon-analyticsの起動確認
- [ ] document-automationの起動確認
- [ ] デプロイ確認スクリプトを実行
- [ ] 容量確認スクリプトを実行
- [ ] プロジェクト内に生成物がないことを確認
- [ ] ログファイルが正しい場所に書き込まれていることを確認

## ✅ 完了確認

以下の条件をすべて満たしていれば完了です：

1. ✅ 全プロジェクトのコードが修正済み
2. ✅ 全プロジェクトが再デプロイ済み
3. ✅ プロジェクト内に生成物がない
4. ✅ ログファイルがnas-project-dataに正しく書き込まれている
5. ✅ 全コンテナが正常に起動している

## 🔗 関連ドキュメント

- [デプロイ完了サマリー](./DEPLOYMENT_COMPLETE_SUMMARY.md)
- [全プロジェクトの生成物をプロジェクト外に保存する修正](./ALL_PROJECTS_DATA_EXTERNAL_FIX.md)
- [データ外部化の確認](./DATA_EXTERNAL_CONFIRMATION.md)

---

**作成日**: 2025年1月27日
**対象**: 全NAS環境プロジェクト
**更新**: 必要に応じて更新

