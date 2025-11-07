#!/bin/bash
# Insta360自動同期 - cronジョブ設定スクリプト

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../" && pwd)"
SYNC_SCRIPT="${PROJECT_DIR}/scripts/sync-with-mount-check.sh"
LOG_FILE="${PROJECT_DIR}/../nas-project-data/insta360-auto-sync/logs/cron.log"

echo "=== Insta360自動同期 - cronジョブ設定 ==="
echo ""

# 同期スクリプトの存在確認
if [ ! -f "${SYNC_SCRIPT}" ]; then
    echo "エラー: 同期スクリプトが見つかりません: ${SYNC_SCRIPT}"
    exit 1
fi

# 実行権限を確認・付与
if [ ! -x "${SYNC_SCRIPT}" ]; then
    echo "実行権限を付与します: ${SYNC_SCRIPT}"
    chmod +x "${SYNC_SCRIPT}"
fi

# ログディレクトリの作成
LOG_DIR="$(dirname "${LOG_FILE}")"
if [ ! -d "${LOG_DIR}" ]; then
    echo "ログディレクトリを作成します: ${LOG_DIR}"
    mkdir -p "${LOG_DIR}"
fi

# 既存のcronジョブを取得
echo "既存のcronジョブを確認しています..."
TEMP_CRON=$(mktemp /tmp/crontab.XXXXXX)
trap "rm -f ${TEMP_CRON}" EXIT

# 既存のcrontabを取得（エラーは無視）
crontab -l > "${TEMP_CRON}" 2>/dev/null || touch "${TEMP_CRON}"

# 既存のinsta360関連のエントリを削除
grep -v "insta360-auto-sync" "${TEMP_CRON}" | grep -v "sync-with-mount-check.sh" | grep -v "sync.py" > "${TEMP_CRON}.new" || touch "${TEMP_CRON}.new"

# 新しいcronジョブを追加（毎日00:00に実行）
CRON_ENTRY="0 0 * * * ${SYNC_SCRIPT} >> ${LOG_FILE} 2>&1"
echo "${CRON_ENTRY}" >> "${TEMP_CRON}.new"

# cronジョブを設定（一時ファイルから読み込み）
echo "cronジョブを設定しています..."
crontab "${TEMP_CRON}.new"

# 一時ファイルを削除
rm -f "${TEMP_CRON}" "${TEMP_CRON}.new"

# 設定されたcronジョブを確認
echo ""
echo "=== 設定されたcronジョブ ==="
crontab -l | grep -E "insta360|sync" || echo "cronジョブが見つかりません"

echo ""
echo "✅ cronジョブの設定が完了しました"
echo ""
echo "設定内容:"
echo "  実行時刻: 毎日 00:00"
echo "  実行スクリプト: ${SYNC_SCRIPT}"
echo "  ログファイル: ${LOG_FILE}"
echo ""
echo "手動実行でテスト:"
echo "  ${SYNC_SCRIPT}"

