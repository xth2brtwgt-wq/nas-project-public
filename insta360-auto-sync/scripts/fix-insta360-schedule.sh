#!/bin/bash
# INSTA360自動同期のスケジュール問題を修正するスクリプト

set -e

echo "=========================================="
echo "INSTA360自動同期 スケジュール修正"
echo "=========================================="
echo ""

# スクリプトのディレクトリを基準にプロジェクトルートに移動
cd "$(dirname "$0")/.."

# 1. バックアップ作成
echo "Step 1: バックアップを作成中..."
cp scripts/sync.py scripts/sync.py.backup.$(date +%Y%m%d_%H%M%S)
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ バックアップ完了"
echo ""

# 2. sync.pyを完全に書き換え
echo "Step 2: scripts/sync.pyを修正中..."
cat > scripts/sync.py << 'SYNC_PY_EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insta360自動同期システム - メイン同期スクリプト
"""

import os
import sys
import logging
import argparse
import time
import schedule
from datetime import datetime
from pathlib import Path

# パスを追加してutilsモジュールをインポート可能にする
sys.path.append('/app')
sys.path.append('/app/utils')

from utils.config_utils import ConfigManager, load_environment_config
from utils.file_utils import FileManager, format_file_size
from utils.email_sender import EmailSender

# ログ設定
def setup_logging():
    """ログ設定を初期化"""
    log_dir = Path('/app/logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / 'insta360_sync.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

class Insta360Sync:
    """Insta360自動同期クラス"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.config_manager = ConfigManager('/app/config')
        self.email_sender = EmailSender()
        
        # 設定を読み込み
        self.app_config = self.config_manager.load_config('app')
        self.env_config = load_environment_config()
        
        # 設定値を取得
        self.source_path = self.env_config.get('sync', {}).get('source_path', '/source')
        self.destination_path = self.env_config.get('sync', {}).get('destination_path', '/volume2/data/insta360')
        self.file_patterns = self.app_config.get('sync', {}).get('file_patterns', [
            'VID_*.mp4', '*.insv', '*.insp', '*.jpg', '*.dng', '*.raw'
        ])
        self.delete_source = self.app_config.get('sync', {}).get('delete_source', False)
        
        # メール設定
        self.to_email = self.env_config.get('email', {}).get('to_email', '')
        self.send_success = self.app_config.get('notification', {}).get('send_success', True)
        self.send_error = self.app_config.get('notification', {}).get('send_error', True)
        self.send_no_files = self.app_config.get('notification', {}).get('send_no_files', False)
        
        self.logger.info("Insta360自動同期システムを初期化しました")
    
    def run_sync(self) -> dict:
        """同期処理を実行"""
        start_time = datetime.now()
        self.logger.info("Insta360ファイル同期を開始します")
        
        try:
            # ファイルマネージャーを初期化
            file_manager = FileManager(
                self.source_path,
                self.destination_path,
                self.file_patterns
            )
            
            # Insta360ファイルを検索
            files = file_manager.find_insta360_files()
            
            if not files:
                self.logger.info("転送対象のInsta360ファイルは見つかりませんでした")
                result = self._create_sync_result(start_time, files, [], [], [])
                
                if self.send_no_files and self.to_email:
                    self._send_notification(result, "no_files")
                
                return result
            
            self.logger.info(f"転送対象ファイル: {len(files)}件")
            
            # ファイル転送を実行
            success_list, skipped_list, failed_list = self._transfer_files(file_manager, files)
            
            # 結果を作成
            result = self._create_sync_result(start_time, files, success_list, skipped_list, failed_list)
            
            # メール通知を送信
            if self.to_email:
                if (success_list or skipped_list) and self.send_success:
                    self._send_notification(result, "success")
                elif failed_list and self.send_error:
                    self._send_notification(result, "error")
            
            self.logger.info("Insta360ファイル同期が完了しました")
            return result
            
        except Exception as e:
            self.logger.error(f"同期処理でエラーが発生しました: {e}", exc_info=True)
            
            # エラー通知を送信
            if self.to_email and self.send_error:
                try:
                    self.email_sender.send_error_notification(
                        self.to_email,
                        str(e),
                        f"同期処理中にエラーが発生しました。詳細はログファイルを確認してください。"
                    )
                except Exception as email_error:
                    self.logger.error(f"エラー通知メール送信失敗: {email_error}")
            
            raise
    
    def _transfer_files(self, file_manager: FileManager, files: list) -> tuple:
        """ファイル転送を実行"""
        success_list = []
        skipped_list = []
        failed_list = []
        
        for file_info in files:
            try:
                self.logger.info(f"ファイル転送開始: {file_info['filename']}")
                
                # ファイルをコピー（スキップ処理有効）
                copy_success, copy_message = file_manager.copy_file(file_info, skip_existing=True)
                
                if copy_success:
                    if "スキップ" in copy_message:
                        # スキップされた場合
                        skipped_list.append({
                            'filename': file_info['filename'],
                            'size': file_info['size'],
                            'message': copy_message
                        })
                        self.logger.info(f"ファイルをスキップ: {file_info['filename']}")
                    else:
                        # 正常にコピーされた場合
                        if self.delete_source:
                            # ソースファイルを削除
                            delete_success, delete_message = file_manager.delete_source_file(file_info)
                            
                            if delete_success:
                                success_list.append({
                                    'filename': file_info['filename'],
                                    'size': file_info['size'],
                                    'message': '転送完了（元ファイル削除）'
                                })
                                self.logger.info(f"ファイル転送完了: {file_info['filename']}")
                            else:
                                failed_list.append({
                                    'filename': file_info['filename'],
                                    'size': file_info['size'],
                                    'error': f"削除失敗: {delete_message}"
                                })
                                self.logger.error(f"ソースファイル削除失敗: {file_info['filename']} - {delete_message}")
                        else:
                            # 削除をスキップ
                            success_list.append({
                                'filename': file_info['filename'],
                                'size': file_info['size'],
                                'message': 'コピー完了（元ファイル保持）'
                            })
                            self.logger.info(f"ファイルコピー完了: {file_info['filename']} （元ファイル保持）")
                else:
                    failed_list.append({
                        'filename': file_info['filename'],
                        'size': file_info['size'],
                        'error': f"コピー失敗: {copy_message}"
                    })
                    self.logger.error(f"ファイルコピー失敗: {file_info['filename']} - {copy_message}")
                    
            except Exception as e:
                failed_list.append({
                    'filename': file_info['filename'],
                    'size': file_info['size'],
                    'error': str(e)
                })
                self.logger.error(f"ファイル転送エラー: {file_info['filename']} - {e}")
        
        return success_list, skipped_list, failed_list
    
    def _create_sync_result(self, start_time: datetime, files: list, success_list: list, skipped_list: list, failed_list: list) -> dict:
        """同期結果を作成"""
        end_time = datetime.now()
        total_size = sum(file['size'] for file in files)
        
        return {
            'execution_date': start_time.strftime('%Y/%m/%d'),
            'execution_time': start_time.strftime('%H:%M:%S'),
            'total_files': len(files),
            'total_size': total_size,
            'success_files': len(success_list),
            'skipped_files': len(skipped_list),
            'failed_files': len(failed_list),
            'success_list': success_list,
            'skipped_list': skipped_list,
            'failed_list': failed_list,
            'duration_seconds': (end_time - start_time).total_seconds(),
            'timestamp': end_time.isoformat()
        }
    
    def _send_notification(self, result: dict, notification_type: str):
        """通知を送信"""
        try:
            if notification_type == "success":
                self.email_sender.send_sync_report(self.to_email, result)
            elif notification_type == "error":
                error_message = f"転送失敗: {result['failed_files']}件"
                error_details = f"成功: {result['success_files']}件, スキップ: {result['skipped_files']}件, 失敗: {result['failed_files']}件"
                self.email_sender.send_error_notification(self.to_email, error_message, error_details)
            elif notification_type == "no_files":
                # ファイルなし通知（簡易版）
                self.email_sender.send_sync_report(self.to_email, result)
                
        except Exception as e:
            self.logger.error(f"通知送信エラー: {e}")

def run_scheduled_sync():
    """スケジュール実行用の同期関数"""
    try:
        sync = Insta360Sync()
        result = sync.run_sync()
        
        # 結果をログに出力
        sync.logger.info(f"同期完了: 成功 {result['success_files']}件, スキップ {result['skipped_files']}件, 失敗 {result['failed_files']}件")
        sync.logger.info(f"総容量: {format_file_size(result['total_size'])}")
        sync.logger.info(f"実行時間: {result['duration_seconds']:.2f}秒")
        
    except Exception as e:
        logging.error(f"スケジュール実行エラー: {e}", exc_info=True)

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Insta360自動同期システム')
    parser.add_argument('--test', action='store_true', help='テストモードで実行')
    parser.add_argument('--once', action='store_true', help='1回だけ実行（スケジュール実行しない）')
    parser.add_argument('--schedule', type=str, help='スケジュール設定（例: 00:00, 毎日深夜0時）')
    
    args = parser.parse_args()
    
    try:
        sync = Insta360Sync()
        
        if args.test:
            # テストモード
            print("テストモード: 設定確認")
            print(f"ソースパス: {sync.source_path}")
            print(f"転送先パス: {sync.destination_path}")
            print(f"ファイルパターン: {sync.file_patterns}")
            print(f"通知先メール: {sync.to_email}")
            
            # メール接続テスト
            if sync.to_email:
                print("メール接続テスト中...")
                if sync.email_sender.test_connection():
                    print("メール接続テスト: 成功")
                else:
                    print("メール接続テスト: 失敗")
            
            return 0
        
        if args.once:
            # 1回だけ実行
            result = sync.run_sync()
            
            # 結果を表示
            print(f"同期完了: 成功 {result['success_files']}件, スキップ {result['skipped_files']}件, 失敗 {result['failed_files']}件")
            print(f"総容量: {format_file_size(result['total_size'])}")
            print(f"実行時間: {result['duration_seconds']:.2f}秒")
            
            return 0 if result['failed_files'] == 0 else 1
        
        # スケジュール実行モード
        schedule_time = args.schedule or os.getenv('SYNC_SCHEDULE_TIME', '00:00')
        
        sync.logger.info("=" * 60)
        sync.logger.info("Insta360自動同期システムを起動しました")
        sync.logger.info(f"スケジュール設定: 毎日 {schedule_time}")
        sync.logger.info(f"ソースパス: {sync.source_path}")
        sync.logger.info(f"転送先パス: {sync.destination_path}")
        sync.logger.info("=" * 60)
        
        # スケジュールを設定
        schedule.every().day.at(schedule_time).do(run_scheduled_sync)
        
        # 起動時に1回実行するかどうか
        run_on_startup = os.getenv('RUN_ON_STARTUP', 'false').lower() == 'true'
        if run_on_startup:
            sync.logger.info("起動時の同期を実行します...")
            run_scheduled_sync()
        
        # スケジュール実行ループ
        sync.logger.info("スケジュール実行を開始します...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1分ごとにチェック
        
    except KeyboardInterrupt:
        print("\nスケジュール実行を停止しました")
        return 0
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        logging.error(f"メイン処理エラー: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
SYNC_PY_EOF

chmod +x scripts/sync.py
echo "✅ sync.py 修正完了"
echo ""

# 3. docker-compose.ymlを修正
echo "Step 3: docker-compose.ymlを修正中..."
cat > docker-compose.yml << 'COMPOSE_EOF'
services:
  insta360-auto-sync:
    build: .
    container_name: insta360-auto-sync
    user: root
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
      - /volume2/data/insta360:/volume2/data/insta360
      - /mnt/mac-share:/source
    env_file:
      - .env
    environment:
      - TZ=Asia/Tokyo
      - DEBUG=false
      - SOURCE_PATH=/source
      - DESTINATION_PATH=/volume2/data/insta360
      - SYNC_SCHEDULE_TIME=00:00
      - RUN_ON_STARTUP=false
    restart: unless-stopped
    labels:
      - "com.docker.compose.project=insta360-auto-sync"
      - "com.docker.compose.service=insta360-auto-sync"
      - "traefik.enable=false"
    networks:
      - default
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  default:
    name: insta360-auto-sync-network
    driver: bridge
COMPOSE_EOF

echo "✅ docker-compose.yml 修正完了"
echo ""

# 4. コンテナを再起動
echo "Step 4: コンテナを再起動中..."
docker compose down
docker compose build
docker compose up -d

sleep 3

echo ""
echo "=========================================="
echo "✅ 修正完了！"
echo "=========================================="
echo ""
echo "ログを確認:"
echo "  docker compose logs -f"
echo ""
