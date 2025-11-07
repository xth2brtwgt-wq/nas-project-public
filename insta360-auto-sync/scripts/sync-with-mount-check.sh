#!/bin/bash
# Insta360自動同期 - マウントチェック付きラッパースクリプト
# 同期処理実行前にマウント状態を確認・再マウント

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../" && pwd)"
CONFIG_DIR="${PROJECT_DIR}/config"
MOUNT_POINT="/mnt/mac-share"
CONTAINER_NAME="insta360-auto-sync"

# 設定ファイルからMac接続情報を読み込む
load_mac_config() {
    # 環境変数から読み込み（優先）
    MAC_IP="${MAC_IP:-}"
    MAC_USERNAME="${MAC_USERNAME:-}"
    MAC_PASSWORD="${MAC_PASSWORD:-}"
    MAC_SHARE="${MAC_SHARE:-}"
    
    # 環境変数ファイルから読み込み（.envのみを使用）
    # 注意: SYNC_SCHEDULEなどの変数がコマンドとして解釈されないように、
    # 必要な変数だけを抽出して設定する
    # .env.restoreは実行時には使用しない（バックアップ用のみ）
    if [ -f "${PROJECT_DIR}/.env" ]; then
        # .envファイルから必要な変数のみを抽出
        while IFS='=' read -r key value || [ -n "$key" ]; do
            # コメント行と空行をスキップ
            [[ "$key" =~ ^#.*$ ]] && continue
            [[ -z "$key" ]] && continue
            
            # 必要な変数のみを設定
            case "$key" in
                MAC_IP|MAC_USERNAME|MAC_PASSWORD|MAC_SHARE)
                    eval "export ${key}=\"${value}\""
                    ;;
            esac
        done < "${PROJECT_DIR}/.env"
    fi
    
    # config/app.jsonから読み込み（環境変数が設定されていない場合）
    if [ -z "${MAC_IP}" ] && [ -f "${CONFIG_DIR}/app.json" ]; then
        if command -v jq >/dev/null 2>&1; then
            MAC_IP=$(jq -r '.mac.ip_address // ""' "${CONFIG_DIR}/app.json" 2>/dev/null || echo "")
            MAC_USERNAME=$(jq -r '.mac.username // ""' "${CONFIG_DIR}/app.json" 2>/dev/null || echo "")
            MAC_PASSWORD=$(jq -r '.mac.password // ""' "${CONFIG_DIR}/app.json" 2>/dev/null || echo "")
            MAC_SHARE=$(jq -r '.mac.share_name // "Insta360"' "${CONFIG_DIR}/app.json" 2>/dev/null || echo "Insta360")
        else
            # jqがない場合は環境変数から取得
            MAC_IP="${MAC_IP:-}"
            MAC_USERNAME="${MAC_USERNAME:-}"
            MAC_PASSWORD="${MAC_PASSWORD:-}"
            MAC_SHARE="${MAC_SHARE:-Insta360}"
        fi
    fi
    
    # デフォルト値の設定（環境変数または設定ファイルから取得）
    MAC_IP="${MAC_IP:-}"
    MAC_USERNAME="${MAC_USERNAME:-}"
    MAC_PASSWORD="${MAC_PASSWORD:-}"
    MAC_SHARE="${MAC_SHARE:-Insta360}"
    
    # マウントソースとオプションを構築
    MOUNT_SOURCE="//${MAC_IP}/${MAC_SHARE}"
    
    # マウントオプションを構築
    MOUNT_OPTIONS="username=${MAC_USERNAME}"
    if [ -n "${MAC_PASSWORD}" ]; then
        MOUNT_OPTIONS="${MOUNT_OPTIONS},password=${MAC_PASSWORD}"
    fi
    MOUNT_OPTIONS="${MOUNT_OPTIONS},uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755"
}

# 設定を読み込む
load_mac_config

# ログ出力用関数
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1"
}

log_warning() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1"
}

# マウント状態をチェック
check_mount() {
    if mount | grep -q "${MOUNT_POINT}"; then
        # マウントされている場合はアクセス可能か確認
        if [ -d "${MOUNT_POINT}" ] && [ -r "${MOUNT_POINT}" ]; then
            return 0
        else
            log_warning "マウントはされていますが、アクセスできません"
            return 1
        fi
    else
        return 1
    fi
}

# マウントを実行
do_mount() {
    log_info "マウントを実行します: ${MOUNT_SOURCE} -> ${MOUNT_POINT}"
    
    # マウントポイントが存在しない場合は作成
    if [ ! -d "${MOUNT_POINT}" ]; then
        log_info "マウントポイントを作成します: ${MOUNT_POINT}"
        sudo mkdir -p "${MOUNT_POINT}"
    fi
    
    # マウント実行
    if sudo mount -t cifs "${MOUNT_SOURCE}" "${MOUNT_POINT}" -o "${MOUNT_OPTIONS}"; then
        log_info "マウントが成功しました"
        return 0
    else
        log_error "マウントに失敗しました"
        return 1
    fi
}

# メイン処理
main() {
    log_info "=== Insta360自動同期（マウントチェック付き）を開始します ==="
    
    # マウント状態をチェック
    if check_mount; then
        log_info "マウントは正常に動作しています"
    else
        log_info "マウントされていないため、再マウントを実行します"
        if ! do_mount; then
            log_error "マウントに失敗したため、同期処理をスキップします"
            exit 1
        fi
    fi
    
    # コンテナが実行中か確認
    if ! docker ps | grep -q "${CONTAINER_NAME}"; then
        log_error "コンテナが実行されていません: ${CONTAINER_NAME}"
        exit 1
    fi
    
    # 同期処理を実行
    log_info "同期処理を開始します"
    docker exec "${CONTAINER_NAME}" python /app/scripts/sync.py --once
    
    exit_code=$?
    if [ ${exit_code} -eq 0 ]; then
        log_info "=== 同期処理が正常に完了しました ==="
    else
        log_error "=== 同期処理でエラーが発生しました（終了コード: ${exit_code}） ==="
    fi
    
    exit ${exit_code}
}

# スクリプト実行
main "$@"

