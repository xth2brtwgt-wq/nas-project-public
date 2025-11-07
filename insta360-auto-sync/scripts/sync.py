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
from utils.mount_utils import MountManager

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
        self.delete_empty_dirs = self.app_config.get('sync', {}).get('delete_empty_dirs', True)
        
        # Mac接続設定（マウントチェック用）
        mac_config = self.app_config.get('mac', {})
        # 環境変数からも取得を試みる
        if not mac_config.get('ip_address'):
            mac_config['ip_address'] = os.getenv('MAC_IP', '')
        if not mac_config.get('username'):
            mac_config['username'] = os.getenv('MAC_USERNAME', '')
        if not mac_config.get('password'):
            mac_config['password'] = os.getenv('MAC_PASSWORD', '')
        if not mac_config.get('share_name'):
            mac_config['share_name'] = os.getenv('MAC_SHARE', 'Insta360')
        
        # マウントマネージャーを初期化
        # コンテナ内からはホスト側のマウントポイントを直接確認できないため、
        # マウント処理はホスト側で実行する必要がある
        # ここでは設定のみ保持し、実際のマウントチェックはホスト側で実行
        self.mount_manager = MountManager('/mnt/mac-share', mac_config)
        
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
            # マウント状態を確認・確保（同期処理の前に実行）
            self.logger.info("マウント状態を確認しています...")
            
            # コンテナ内からはホスト側のマウントポイントを直接操作できないため、
            # ソースパスの存在チェックでマウント状態を簡易確認
            source_path_obj = Path(self.source_path)
            if not source_path_obj.exists():
                # マウントされていない可能性があるため、警告を出してホスト側での再マウントを促す
                warning_msg = (
                    f"ソースパスが存在しません（マウントされていない可能性があります）: {self.source_path}\n"
                    f"ホスト側でマウントを確認してください: sudo mount -a または /usr/local/bin/check-mac-share-mount.sh"
                )
                self.logger.warning(warning_msg)
                
                # ホスト側でマウントチェックスクリプトを実行（存在する場合）
                # コンテナ内からホスト側のスクリプトを実行するには、docker execが必要
                # ここでは警告のみとし、実際のマウント処理はホスト側のsystemdタイマーまたは
                # 同期処理実行前にホスト側で実行するスクリプトに任せる
                error_msg = f"ソースパスが存在しません: {self.source_path}"
                raise FileNotFoundError(error_msg)
            
            # マウントされているがアクセスできない場合のチェック
            try:
                list(source_path_obj.iterdir())
                self.logger.info("マウントは正常に動作しています")
            except PermissionError:
                error_msg = f"ソースパスへのアクセス権限がありません: {self.source_path}"
                self.logger.error(error_msg)
                raise PermissionError(error_msg)
            except Exception as e:
                error_msg = f"ソースパスのアクセスチェック中にエラーが発生しました: {e}"
                self.logger.error(error_msg)
                raise
            
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
                                # 空ディレクトリも削除する場合
                                if self.delete_empty_dirs:
                                    dir_delete_success, dir_delete_message = file_manager.delete_empty_directories(file_info)
                                    if dir_delete_success and "削除成功" in dir_delete_message:
                                        self.logger.info(f"空ディレクトリ削除完了: {file_info['filename']} の親ディレクトリ")
                                    elif not dir_delete_success:
                                        self.logger.warning(f"空ディレクトリ削除失敗: {dir_delete_message}")
                                
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

def scheduled_sync():
    """スケジュール実行用の同期処理"""
    logger = logging.getLogger(__name__)
    try:
        sync = Insta360Sync()
        result = sync.run_sync()
        
        logger.info(f"同期完了: 成功 {result['success_files']}件, スキップ {result['skipped_files']}件, 失敗 {result['failed_files']}件")
        logger.info(f"総容量: {format_file_size(result['total_size'])}")
        logger.info(f"実行時間: {result['duration_seconds']:.2f}秒")
        
    except Exception as e:
        logger.error(f"同期処理でエラーが発生しました: {e}", exc_info=True)

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Insta360自動同期システム')
    parser.add_argument('--test', action='store_true', help='テストモードで実行')
    parser.add_argument('--dry-run', action='store_true', help='ドライランモード（実際の転送は行わない）')
    parser.add_argument('--once', action='store_true', help='1回だけ同期を実行（スケジューラーなし）')
    
    args = parser.parse_args()
    
    # ログ設定を初期化
    logger = setup_logging()
    
    try:
        sync = Insta360Sync()
        
        if args.test:
            # テストモード
            print("テストモード: 設定確認")
            print(f"ソースパス: {sync.source_path}")
            print(f"転送先パス: {sync.destination_path}")
            print(f"ファイルパターン: {sync.file_patterns}")
            print(f"ソースファイル削除: {sync.delete_source}")
            print(f"空ディレクトリ削除: {sync.delete_empty_dirs}")
            print(f"通知先メール: {sync.to_email}")
            
            # ソースパスの存在チェック（マウント状態の簡易確認）
            print("\n=== マウント状態の確認 ===")
            source_path_obj = Path(sync.source_path)
            if source_path_obj.exists():
                print(f"✅ ソースパスは存在します: {sync.source_path}")
                try:
                    file_count = len(list(source_path_obj.iterdir()))
                    print(f"   ディレクトリ内のエントリ数: {file_count}")
                except Exception as e:
                    print(f"   ⚠️  ディレクトリの読み取りエラー: {e}")
            else:
                print(f"❌ ソースパスが存在しません: {sync.source_path}")
                print("   Mac共有フォルダがマウントされているか確認してください: /mnt/mac-share")
            
            # メール接続テスト
            if sync.to_email:
                print("\nメール接続テスト中...")
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
        
        # スケジューラーモード
        logger.info("============================================================")
        logger.info("Insta360自動同期システムを起動しました")
        logger.info("スケジュール設定: 毎日 00:00")
        logger.info(f"ソースパス: {sync.source_path}")
        logger.info(f"転送先パス: {sync.destination_path}")
        logger.info("============================================================")
        logger.info("スケジュール実行を開始します...")
        
        # 毎日00:00に実行
        schedule.every().day.at("00:00").do(scheduled_sync)
        
        # スケジューラーを実行
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1分ごとにチェック
        
    except KeyboardInterrupt:
        logger.info("スケジューラーを停止しました")
        return 0
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())