# 月次AI分析レポート修正 - デプロイチェックリスト

## 修正内容

月次AI分析レポートでAI分析が実行されない問題を修正しました。

### 修正ファイル

1. **`app.py`** - `generate_monthly_ai_report_data`関数
   - `analyze_security_data()`の代わりに`AIAnalyzer.analyze_monthly_security_data()`を使用
   - 過去30日間のBAN履歴を取得してAI分析に渡す

2. **`utils/email_sender.py`** - `_create_monthly_ai_report_body`関数
   - AI分析結果（summary、insights、recommendations）をメール本文に含める

3. **`scripts/monthly_ai_report_scheduler.py`**
   - `report_data`の重複作成を削除（`generate_monthly_ai_report_data`の返り値をそのまま使用）

## デプロイ前チェック

- [x] ローカルでテスト実行成功
- [x] AI分析結果が正しく表示されることを確認
- [x] メール送信が正常に動作することを確認

## デプロイ手順

### 1. ローカルで変更をコミット・プッシュ

```bash
cd nas-dashboard
git add app.py utils/email_sender.py scripts/monthly_ai_report_scheduler.py
git commit -m "fix: 月次AI分析レポートでAI分析が実行されない問題を修正"
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

または、デプロイスクリプトを使わない場合：

```bash
cd ~/nas-project/nas-dashboard
docker compose down
docker compose up -d --build
```

### 3. デプロイ後確認

#### コンテナの起動確認

```bash
docker compose ps
```

以下のコンテナが起動していることを確認：
- `nas-dashboard` - メインアプリケーション
- `nas-dashboard-monthly-scheduler` - 月次レポートスケジューラー

#### スケジューラーのログ確認

```bash
docker logs nas-dashboard-monthly-scheduler
```

以下のメッセージが表示されることを確認：
- "月次AI分析レポート自動送信システムを起動しました"
- "スケジュール設定: 毎月1日 10:00"

#### テスト実行（オプション）

```bash
# コンテナ内でテスト実行
docker exec -it nas-dashboard-monthly-scheduler python scripts/monthly_ai_report_scheduler.py

# 環境変数 FORCE_MONTHLY_TEST=true で強制実行
docker exec -it nas-dashboard-monthly-scheduler bash -c "FORCE_MONTHLY_TEST=true python scripts/monthly_ai_report_scheduler.py"
```

または、docker-compose.ymlに一時的に追加：

```yaml
environment:
  - FORCE_MONTHLY_TEST=true
```

## 動作確認

### 1. 次の月次レポート送信を待つ

- 毎月1日の朝10:00に自動実行されます

### 2. 手動でテスト実行（推奨）

NAS環境で以下のコマンドでテスト実行：

```bash
docker exec -it nas-dashboard-monthly-scheduler python -c "
import os
os.environ['FORCE_MONTHLY_TEST'] = 'true'
from scripts.monthly_ai_report_scheduler import send_monthly_ai_report
send_monthly_ai_report()
"
```

### 3. レポートファイルの確認

```bash
ls -lh ~/nas-project-data/nas-dashboard/reports/
```

最新のレポートファイルを確認：

```bash
cat ~/nas-project-data/nas-dashboard/reports/monthly_ai_report_*.txt | tail -50
```

以下の内容が含まれていることを確認：
- ✅ AI分析サマリー（要約文）
- ✅ リスクレベル（LOW/MEDIUM/HIGH）
- ✅ 重要な洞察（リスト）
- ✅ 推奨事項（リスト）

### 4. メール受信確認

- `EMAIL_TO`で設定したメールアドレスにレポートが届くことを確認
- AI分析結果が正しく表示されていることを確認

## トラブルシューティング

### AI分析が実行されない

1. 環境変数の確認
   ```bash
   docker exec nas-dashboard-monthly-scheduler env | grep GEMINI
   ```

2. ログの確認
   ```bash
   docker logs nas-dashboard-monthly-scheduler | grep -i "ai分析"
   ```

3. 手動実行でエラーを確認
   ```bash
   docker exec -it nas-dashboard-monthly-scheduler python scripts/monthly_ai_report_scheduler.py
   ```

### メールが送信されない

1. メール設定の確認
   ```bash
   docker exec nas-dashboard-monthly-scheduler env | grep EMAIL
   ```

2. メール送信ログの確認
   ```bash
   docker logs nas-dashboard-monthly-scheduler | grep -i "メール"
   ```

## ロールバック

問題が発生した場合：

```bash
cd ~/nas-project/nas-dashboard
git log --oneline -5  # コミット履歴を確認
git checkout <前のコミットハッシュ>  # 前のバージョンに戻る
docker compose down
docker compose up -d --build
```















