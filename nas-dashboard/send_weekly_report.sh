#!/bin/bash
# 週次レポート送信スクリプト
# 作成日: Fri Oct 24 18:43:00 JST 2025

cd ~/nas-project/nas-dashboard

# ログファイル
LOG_FILE="~/nas-project/nas-dashboard/logs/weekly_report.log"

# ログディレクトリ作成
mkdir -p ~/nas-project/nas-dashboard/logs

# ログ出力関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "週次レポート送信開始"

# メインサービスが起動しているか確認
if ! docker ps | grep -q "nas-dashboard"; then
    log "エラー: nas-dashboardサービスが起動していません"
    exit 1
fi

# 週次レポート送信
RESPONSE=$(curl -s -X POST http://localhost:9001/api/reports/weekly \
  -H 'Content-Type: application/json' \
  -d '{"send_email": true}' \
  --max-time 30)

if [ $? -eq 0 ]; then
    log "週次レポート送信成功: $RESPONSE"
else
    log "エラー: 週次レポート送信に失敗しました"
    exit 1
fi

log "週次レポート送信完了"
