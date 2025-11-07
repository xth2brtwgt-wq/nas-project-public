# NASデプロイ クイックガイド

## 修正内容

月次AI分析レポートでAI分析が実行されない問題を修正しました。

### 修正ファイル

1. `app.py` - `generate_monthly_ai_report_data`関数を修正
2. `utils/email_sender.py` - `_create_monthly_ai_report_body`関数を修正
3. `scripts/monthly_ai_report_scheduler.py` - `report_data`の渡し方を修正
4. `deploy.sh` - 月次レポートスケジューラーの確認を追加

## デプロイ手順

### 1. ローカルでコミット・プッシュ

```bash
cd /Users/Yoshi/nas-project/nas-dashboard

# 変更をコミット
git add app.py utils/email_sender.py scripts/monthly_ai_report_scheduler.py deploy.sh DEPLOY_CHECKLIST.md scripts/test_monthly_report.py
git commit -m "fix: 月次AI分析レポートでAI分析が実行されない問題を修正

- generate_monthly_ai_report_dataでAIAnalyzerを使用するように修正
- 過去30日間のBAN履歴を取得してAI分析に渡す
- メール本文にAI分析結果を正しく表示
- デプロイスクリプトに月次レポートスケジューラーの確認を追加"

git push origin feature/monitoring-fail2ban-integration
```

### 2. NASでデプロイ

```bash
# NASに接続
ssh -p 23456 YOUR_USERNAME@YOUR_IP_ADDRESS110

# 最新コードを取得
cd ~/nas-project
git pull origin feature/monitoring-fail2ban-integration

# nas-dashboardをデプロイ
cd nas-dashboard
./deploy.sh
```

## デプロイ後確認

### コンテナの起動確認

```bash
docker compose ps
```

以下が起動していることを確認：
- `nas-dashboard` ✅
- `nas-dashboard-monthly-scheduler` ✅

### ログ確認

```bash
docker logs nas-dashboard-monthly-scheduler | tail -30
```

以下のメッセージが表示されることを確認：
```
月次AI分析レポート自動送信システムを起動しました
スケジュール設定: 毎月1日 10:00
```

### テスト実行（オプション）

```bash
# 手動でテスト実行
docker exec -it nas-dashboard-monthly-scheduler python -c "
import os
os.environ['FORCE_MONTHLY_TEST'] = 'true'
from scripts.monthly_ai_report_scheduler import send_monthly_ai_report
send_monthly_ai_report()
"
```

### レポートファイル確認

```bash
ls -lh ~/nas-project-data/nas-dashboard/reports/
cat ~/nas-project-data/nas-dashboard/reports/monthly_ai_report_*.txt | tail -50
```

以下の内容が含まれていることを確認：
- ✅ AI分析サマリー（要約文）
- ✅ リスクレベル（LOW/MEDIUM/HIGH）
- ✅ 重要な洞察（リスト）
- ✅ 推奨事項（リスト）

## トラブルシューティング

### AI分析が実行されない

```bash
# 環境変数の確認
docker exec nas-dashboard-monthly-scheduler env | grep GEMINI

# ログの確認
docker logs nas-dashboard-monthly-scheduler | grep -i "ai分析"
```

### メールが送信されない

```bash
# メール設定の確認
docker exec nas-dashboard-monthly-scheduler env | grep EMAIL

# メール送信ログの確認
docker logs nas-dashboard-monthly-scheduler | grep -i "メール"
```















