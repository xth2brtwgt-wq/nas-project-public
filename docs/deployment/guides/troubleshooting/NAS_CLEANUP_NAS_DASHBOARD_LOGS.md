# NAS環境でのnas-dashboard/logs削除手順

## 📋 問題

NAS環境で`nas-dashboard/logs/`ディレクトリが残っています（4.0K）。

## 🔧 対処方法

### 1. nas-dashboard/logsを削除

```bash
# NAS環境で実行
cd ~/nas-project
rm -rf nas-dashboard/logs
```

### 2. nas-dashboardを再デプロイ

```bash
cd ~/nas-project/nas-dashboard
docker compose up -d --build
```

### 3. 再確認

```bash
# 確認スクリプトを実行
cd ~/nas-project
./scripts/check-nas-project-clean.sh

# または手動で確認
ls -la nas-dashboard/logs 2>/dev/null || echo "✅ logsディレクトリは存在しません"

# nas-project-data配下に正しく保存されていることを確認
ls -lh ~/nas-project-data/nas-dashboard/logs/ 2>/dev/null
```

## ✅ 期待される結果

削除後、再デプロイしても`nas-dashboard/logs/`は作成されず、すべてのログは`~/nas-project-data/nas-dashboard/logs/`に保存されます。

---

**更新日**: 2025年11月7日

