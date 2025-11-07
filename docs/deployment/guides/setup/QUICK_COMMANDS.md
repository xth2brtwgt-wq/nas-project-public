# クイックコマンド一覧

## 📋 NAS環境で実行するコマンド

### オプション1: 一括実行スクリプト（推奨）

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# スクリプトを実行
cd ~/nas-project
git pull origin main
chmod +x docs/deployment/EXECUTE_CLEANUP_COMMANDS.sh
./docs/deployment/EXECUTE_CLEANUP_COMMANDS.sh
```

### オプション2: 個別実行

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# 1. 最新コードを取得
cd ~/nas-project
git pull origin main

# 2. nas-dashboardの再デプロイ
cd ~/nas-project/nas-dashboard
docker compose down
docker compose up -d --build

# 3. 残りのクリーンアップ
cd ~/nas-project
~/nas-project/scripts/cleanup-all-projects.sh

# 4. 手動で削除（もし残っている場合）
rm -rf ~/nas-project/nas-dashboard/logs 2>/dev/null || true
rm -rf ~/nas-project/data/reports 2>/dev/null || true

# 5. amazon-analyticsの起動確認
cd ~/nas-project/amazon-analytics
if [ ! -f .env ]; then
    [ -f .env.restore ] && cp .env.restore .env || cp env.example .env
    echo "NAS_MODE=true" >> .env
fi
docker compose down
docker compose up -d --build

# 6. document-automationの起動確認
cd ~/nas-project/document-automation
if [ ! -f .env ]; then
    [ -f .env.restore ] && cp .env.restore .env || cp env.example .env
    echo "NAS_MODE=true" >> .env
fi
docker compose down
docker compose up -d --build

# 7. 最終確認
cd ~/nas-project
~/nas-project/scripts/verify-deployment.sh
~/nas-project/scripts/check-disk-usage.sh
```

### オプション3: 最小限のコマンド（既に.envがある場合）

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# 最新コードを取得
cd ~/nas-project && git pull origin main

# nas-dashboardを再デプロイ
cd ~/nas-project/nas-dashboard && docker compose up -d --build

# クリーンアップ
cd ~/nas-project && ~/nas-project/scripts/cleanup-all-projects.sh
rm -rf ~/nas-project/nas-dashboard/logs ~/nas-project/data/reports 2>/dev/null || true

# 他のプロジェクトを再デプロイ
cd ~/nas-project/amazon-analytics && docker compose up -d --build
cd ~/nas-project/document-automation && docker compose up -d --build

# 確認
cd ~/nas-project && ~/nas-project/scripts/verify-deployment.sh
```

## 📋 確認コマンド

### コンテナの状態確認

```bash
docker compose ps
```

### ログ確認

```bash
# 各プロジェクトのログを確認
docker logs amazon-analytics-web --tail 20
docker logs youtube-to-notion --tail 20
docker logs meeting-minutes-byc --tail 20
docker logs doc-automation-web --tail 20
docker logs nas-dashboard --tail 20
```

### 容量確認

```bash
# 容量確認スクリプトを実行
~/nas-project/scripts/check-disk-usage.sh

# または詳細分析
~/nas-project/scripts/analyze-project-size.sh
```

### プロジェクト内の生成物確認

```bash
# プロジェクト内に生成物がないことを確認
find ~/nas-project -type d \( -name "logs" -o -name "data" -o -name "uploads" -o -name "cache" \) | grep -v ".git" | grep -v "node_modules" | grep -v "venv"
```

### ログファイルの確認

```bash
# ログファイルが正しい場所に書き込まれているか確認
ls -lh /home/AdminUser/nas-project-data/*/logs/app.log
```

## 🔗 関連ドキュメント

- [最終クリーンアップ手順](./FINAL_CLEANUP_STEPS.md)
- [デプロイ完了サマリー](./DEPLOYMENT_COMPLETE_SUMMARY.md)

---

**作成日**: 2025年1月27日
**対象**: 全NAS環境プロジェクト
**更新**: 必要に応じて更新

