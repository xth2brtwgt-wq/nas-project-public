#!/bin/bash
# YouTube音声ファイル定期クリーンアップ用cron設定スクリプト
# 毎日午前2時に1週間経過したMP3ファイルを削除

set -e

SCRIPT_DIR="/home/YOUR_USERNAME/nas-project/youtube-to-notion/scripts"
CLEANUP_SCRIPT="$SCRIPT_DIR/cleanup_audio.sh"
CRON_LOG="/home/YOUR_USERNAME/nas-project-data/youtube-to-notion/logs/cron_cleanup.log"

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "YouTube音声ファイル定期クリーンアップ用cron設定開始"

# スクリプトの実行権限確認
if [ ! -x "$CLEANUP_SCRIPT" ]; then
    log "実行権限を付与: $CLEANUP_SCRIPT"
    chmod +x "$CLEANUP_SCRIPT"
fi

# ログディレクトリ作成
mkdir -p "$(dirname "$CRON_LOG")"

# 既存のcronエントリを削除
log "既存のcronエントリを削除中..."
crontab -l 2>/dev/null | grep -v "cleanup_audio.sh" | crontab - 2>/dev/null || true

# 新しいcronエントリを追加
log "新しいcronエントリを追加中..."
(crontab -l 2>/dev/null; echo "0 2 * * * $CLEANUP_SCRIPT >> $CRON_LOG 2>&1") | crontab -

# cron設定確認
log "設定されたcronエントリ:"
crontab -l | grep "cleanup_audio.sh"

log "YouTube音声ファイル定期クリーンアップ用cron設定完了"
log "実行スケジュール: 毎日午前2時"
log "ログファイル: $CRON_LOG"
