#!/bin/bash
# YouTube音声ファイル定期クリーンアップスクリプト
# 使用方法: ./cleanup_audio.sh [--dry-run] [--archive]

set -e

# 設定
UPLOAD_DIR="~/nas-project-data/youtube-to-notion/uploads"
ARCHIVE_DIR="~/nas-project-data/youtube-to-notion/archive"
MAX_AGE_HOURS=168  # 1週間（168時間）
MAX_FILES=50       # 最大50ファイルまで保持

# 引数解析
DRY_RUN=false
ARCHIVE_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --archive)
            ARCHIVE_MODE=true
            shift
            ;;
        *)
            echo "不明な引数: $1"
            echo "使用方法: $0 [--dry-run] [--archive]"
            exit 1
            ;;
    esac
done

# ログ設定
LOG_FILE="~/nas-project-data/youtube-to-notion/logs/cleanup_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "YouTube音声ファイルクリーンアップ開始"
log "アップロードディレクトリ: $UPLOAD_DIR"
log "ドライランモード: $DRY_RUN"
log "アーカイブモード: $ARCHIVE_MODE"

# ディレクトリ存在確認
if [ ! -d "$UPLOAD_DIR" ]; then
    log "エラー: アップロードディレクトリが存在しません: $UPLOAD_DIR"
    exit 1
fi

# アーカイブディレクトリ作成
if [ "$ARCHIVE_MODE" = true ]; then
    mkdir -p "$ARCHIVE_DIR"
    log "アーカイブディレクトリ: $ARCHIVE_DIR"
fi

# 音声ファイル検索
AUDIO_FILES=($(find "$UPLOAD_DIR" -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.webm" -o -name "*.m4a" -o -name "*.ogg" \) -printf '%T@ %p\n' | sort -n | cut -d' ' -f2-))

if [ ${#AUDIO_FILES[@]} -eq 0 ]; then
    log "クリーンアップ対象の音声ファイルが見つかりません"
    exit 0
fi

log "発見された音声ファイル数: ${#AUDIO_FILES[@]}"

# ファイル処理
PROCESSED_COUNT=0
FREED_SPACE=0

for file_path in "${AUDIO_FILES[@]}"; do
    filename=$(basename "$file_path")
    file_size=$(stat -c%s "$file_path" 2>/dev/null || echo "0")
    file_age_hours=$(( ($(date +%s) - $(stat -c%Y "$file_path")) / 3600 ))
    
    # 年齢チェック
    if [ $file_age_hours -gt $MAX_AGE_HOURS ] || [ $PROCESSED_COUNT -ge $MAX_FILES ]; then
        if [ "$DRY_RUN" = true ]; then
            log "[DRY RUN] 処理予定: $filename (${file_size} bytes, ${file_age_hours}時間前)"
        else
            if [ "$ARCHIVE_MODE" = true ]; then
                # アーカイブ
                archive_path="$ARCHIVE_DIR/$filename"
                mv "$file_path" "$archive_path"
                log "アーカイブ: $filename -> $archive_path"
            else
                # 削除
                rm "$file_path"
                log "削除: $filename"
            fi
        fi
        
        PROCESSED_COUNT=$((PROCESSED_COUNT + 1))
        FREED_SPACE=$((FREED_SPACE + file_size))
    else
        log "保持: $filename (${file_age_hours}時間前)"
    fi
done

# 結果サマリー
log "クリーンアップ完了"
log "処理ファイル数: $PROCESSED_COUNT"
log "解放容量: $(($FREED_SPACE / 1024 / 1024)) MB"

# 古いログファイルのクリーンアップ（30日以上前）
find "$(dirname "$LOG_FILE")" -name "cleanup_*.log" -type f -mtime +30 -delete 2>/dev/null || true

log "YouTube音声ファイルクリーンアップ終了"
