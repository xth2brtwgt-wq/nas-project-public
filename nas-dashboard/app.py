#!/usr/bin/env python3
"""
NAS統合管理ダッシュボード
複数のWebアプリケーションとシステム監視を統合管理
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file
import subprocess
import json
import os
import psutil
import requests
from datetime import datetime, timedelta
import logging
from pathlib import Path
import shutil
import zipfile
import tempfile
import re
from version import get_version, get_version_string, get_full_version_info
from utils.email_sender import EmailSender
from utils.ai_analyzer import AIAnalyzer


# ログ設定
log_dir = os.getenv('LOG_DIR', './logs')
os.makedirs(log_dir, exist_ok=True)

# ファイルハンドラーを追加
log_file = os.path.join(log_dir, 'app.log')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        file_handler,
        logging.StreamHandler()  # 標準出力も維持
    ]
)
logger = logging.getLogger(__name__)

def get_ip_location(ip):
    """IPアドレスの地理的位置情報を取得"""
    try:
        # プライベートIPアドレスの場合は「ローカル」を返す
        if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
            return "ローカル"
        
        # 外部APIを使用して地理的位置情報を取得
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                country = data.get('country', 'Unknown')
                region = data.get('regionName', '')
                city = data.get('city', '')
                
                location_parts = [part for part in [city, region, country] if part]
                return ', '.join(location_parts) if location_parts else 'Unknown'
        
        return "Unknown"
    except Exception as e:
        logger.warning(f"IP位置情報取得エラー ({ip}): {e}")
        return "Unknown"

def get_monthly_ban_history():
    """過去30日間のBAN履歴を取得（月次レポート用）"""
    try:
        if os.getenv('NAS_MODE'):
            logger.info("月次レポート用BAN履歴を取得中")
            ban_history = []
            
            # 過去30日間の日付を計算
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            thirty_days_ago_str = thirty_days_ago.strftime('%Y-%m-%d')
            
            logger.info(f"過去30日間のBAN履歴を取得中 (from: {thirty_days_ago_str})")
            
            try:
                # Dockerログから全履歴を取得
                result = subprocess.run([
                    'docker', 'logs', 'fail2ban'
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # BAN実行ログを解析
                    for line in result.stdout.split('\n'):
                        if 'Ban ' in line and 'NOTICE' in line:
                            try:
                                # タイムスタンプを抽出
                                timestamp_part = line.split(' fail2ban.actions')[0]
                                timestamp_str = timestamp_part.split(' ')[0] + ' ' + timestamp_part.split(' ')[1].split(',')[0]
                                
                                # 日付を解析して30日間フィルタを適用
                                log_date_str = timestamp_part.split(' ')[0]
                                log_date = datetime.strptime(log_date_str, '%Y-%m-%d')
                                
                                # 過去30日間のログのみを処理
                                if log_date >= thirty_days_ago:
                                    # Jail名を抽出
                                    jail_start = line.find('[') + 1
                                    jail_end = line.find(']', jail_start)
                                    jail = line[jail_start:jail_end]
                                    
                                    # IPアドレスを抽出
                                    ip_start = line.find('Ban ') + 4
                                    ip = line[ip_start:].strip()
                                    
                                    logger.info(f"月次BAN履歴追加: IP={ip}, Jail={jail}, Time={timestamp_str}")
                                    ban_history.append({
                                        'timestamp': timestamp_str,
                                        'ip': ip,
                                        'jail': jail,
                                        'action': 'Ban'
                                    })
                                else:
                                    logger.debug(f"30日間範囲外のログをスキップ: {log_date_str}")
                            except Exception as parse_error:
                                logger.warning(f"BANログ解析エラー: {parse_error}, Line: {line}")
                                continue
                    
                    # タイムスタンプでソート（新しい順）
                    ban_history.sort(key=lambda x: x['timestamp'], reverse=True)
                    logger.info(f"月次BAN履歴取得完了: {len(ban_history)}件")
                    
                else:
                    logger.error(f"Dockerログ取得エラー: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Dockerログ取得エラー: {e}")
                
            return ban_history
        else:
            # ローカル環境ではモックデータを返す
            return [
                {
                    'timestamp': '2025-10-20 10:30:00',
                    'ip': '192.168.1.100',
                    'jail': 'sshd',
                    'action': 'Ban'
                },
                {
                    'timestamp': '2025-10-18 15:45:00',
                    'ip': '10.0.0.50',
                    'jail': 'nginx-http-auth',
                    'action': 'Ban'
                }
            ]
    except Exception as e:
        logger.error(f"月次BAN履歴取得エラー: {e}")
        return []

def get_ban_history_simple():
    """BAN履歴を取得（位置情報なし）"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境ではFail2banログから過去7日間のBAN履歴を取得
            ban_history = []
            
            logger.info("BAN履歴をログから取得中")
            
            try:
                # 過去7日間の日付を計算
                from datetime import datetime, timedelta
                seven_days_ago = datetime.now() - timedelta(days=7)
                seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d')
                
                logger.info(f"過去7日間のBAN履歴を取得中 (from: {seven_days_ago_str})")
                
                # Fail2banログから全履歴を取得（--sinceが動作しないため）
                result = subprocess.run([
                    'docker', 'logs', 'fail2ban'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    # BAN実行ログを解析
                    for line in result.stdout.split('\n'):
                        if 'Ban ' in line and 'NOTICE' in line:
                            # 例: 2025-10-24 15:21:50,993 fail2ban.actions [1]: NOTICE [sshd] Ban 183.66.17.82
                            try:
                                # タイムスタンプを抽出
                                timestamp_part = line.split(' fail2ban.actions')[0]
                                timestamp_str = timestamp_part.split(' ')[0] + ' ' + timestamp_part.split(' ')[1].split(',')[0]
                                
                                # 日付を解析して7日間フィルタを適用
                                log_date_str = timestamp_part.split(' ')[0]
                                log_date = datetime.strptime(log_date_str, '%Y-%m-%d')
                                
                                # 過去7日間のログのみを処理
                                if log_date >= seven_days_ago:
                                    # Jail名を抽出
                                    jail_start = line.find('[') + 1
                                    jail_end = line.find(']', jail_start)
                                    jail = line[jail_start:jail_end]
                                    
                                    # IPアドレスを抽出
                                    ip_start = line.find('Ban ') + 4
                                    ip = line[ip_start:].strip()
                                    
                                    logger.info(f"BAN履歴追加: IP={ip}, Jail={jail}, Time={timestamp_str}")
                                    ban_history.append({
                                        'timestamp': timestamp_str,
                                        'ip': ip,
                                        'jail': jail,
                                        'action': 'Ban'
                                    })
                                else:
                                    logger.debug(f"7日間範囲外のログをスキップ: {log_date_str}")
                            except Exception as parse_error:
                                logger.warning(f"BANログ解析エラー: {parse_error}, Line: {line}")
                                continue
                
                # 過去7日間のUNBAN実行も取得
                for line in result.stdout.split('\n'):
                    if 'Unban ' in line and 'NOTICE' in line:
                        # 例: 2025-10-24 16:12:50,302 fail2ban.actions [1]: NOTICE [sshd] Unban 196.251.70.164
                        try:
                            # タイムスタンプを抽出
                            timestamp_part = line.split(' fail2ban.actions')[0]
                            timestamp_str = timestamp_part.split(' ')[0] + ' ' + timestamp_part.split(' ')[1].split(',')[0]
                            
                            # 日付を解析して7日間フィルタを適用
                            log_date_str = timestamp_part.split(' ')[0]
                            log_date = datetime.strptime(log_date_str, '%Y-%m-%d')
                            
                            # 過去7日間のログのみを処理
                            if log_date >= seven_days_ago:
                                # Jail名を抽出
                                jail_start = line.find('[') + 1
                                jail_end = line.find(']', jail_start)
                                jail = line[jail_start:jail_end]
                                
                                # IPアドレスを抽出
                                ip_start = line.find('Unban ') + 6
                                ip = line[ip_start:].strip()
                                
                                logger.info(f"UNBAN履歴追加: IP={ip}, Jail={jail}, Time={timestamp_str}")
                                ban_history.append({
                                    'timestamp': timestamp_str,
                                    'ip': ip,
                                    'jail': jail,
                                    'action': 'Unban'
                                })
                            else:
                                logger.debug(f"7日間範囲外のUNBANログをスキップ: {log_date_str}")
                        except Exception as parse_error:
                            logger.warning(f"UNBANログ解析エラー: {parse_error}, Line: {line}")
                            continue
                
                # タイムスタンプでソート（新しい順）
                ban_history.sort(key=lambda x: x['timestamp'], reverse=True)
                
                logger.info(f"BAN履歴取得完了: {len(ban_history)}件")
                return ban_history
                
            except Exception as log_error:
                logger.error(f"Fail2banログ取得エラー: {log_error}")
                return []
        else:
            # ローカル環境ではモックデータを返す
            return [
                {
                    'timestamp': '2025-10-24 15:21:50',
                    'ip': '183.66.17.82',
                    'jail': 'sshd',
                    'action': 'Ban'
                },
                {
                    'timestamp': '2025-10-24 16:18:47',
                    'ip': '220.154.129.88',
                    'jail': 'sshd',
                    'action': 'Ban'
                },
                {
                    'timestamp': '2025-10-24 17:40:06',
                    'ip': '196.251.70.164',
                    'jail': 'sshd',
                    'action': 'Ban'
                }
            ]
    except Exception as e:
        logger.error(f"BAN履歴取得エラー: {e}")
        return []

app = Flask(__name__)
app.secret_key = 'nas-dashboard-secret-key-2025'

# 設定
class Config:
    # サービス設定
    SERVICES = {
        'meeting_minutes': {
            'name': '議事録生成システム',
            'url': 'http://YOUR_NAS_IP:5002' if os.getenv('NAS_MODE') else 'http://localhost:5002',
            'description': '音声ファイルから自動で議事録を生成',
            'icon': 'fas fa-microphone-alt',
            'color': 'primary'
        },
        'document_automation': {
            'name': 'ドキュメント自動処理',
            'url': 'http://YOUR_NAS_IP:8080' if os.getenv('NAS_MODE') else 'http://localhost:8080',
            'description': 'PDF・画像からOCR、AI要約、自動分類',
            'icon': 'fas fa-file-alt',
            'color': 'success'
        },
        'amazon_analytics': {
            'name': 'Amazon購入分析',
            'url': 'http://YOUR_NAS_IP:8001' if os.getenv('NAS_MODE') else 'http://localhost:8001',
            'description': 'Amazon購入履歴の分析と可視化、AI活用',
            'icon': 'fas fa-shopping-cart',
            'color': 'warning'
        },
        'youtube_to_notion': {
            'name': 'YouTube-to-Notion自動投稿',
            'url': 'http://YOUR_NAS_IP:8111' if os.getenv('NAS_MODE') else 'http://localhost:8111',
            'description': 'YouTube動画の自動要約とNotion投稿、コメント分析',
            'icon': 'fab fa-youtube',
            'color': 'danger'
        },
        'insta360_sync': {
            'name': 'Insta360自動同期',
            'url': '#',  # WebUIがないため、ダッシュボード内で制御
            'description': 'Insta360ファイルの自動同期とログ確認（ダッシュボード内で制御）',
            'icon': 'fas fa-camera',
            'color': 'info',
            'external': False  # 外部リンクではない
        },
        'fail2ban': {
            'name': 'Fail2Ban監視',
            'url': '#',  # WebUIがないため、ダッシュボード内で監視
            'description': 'セキュリティ監視とBAN管理（ダッシュボード内で確認）',
            'icon': 'fas fa-shield-alt',
            'color': 'warning',
            'external': False  # 外部リンクではない
        }
    }
    
    # システム監視設定
    SYSTEM_MONITORING = {
        'disk_threshold': 80,  # ディスク使用率の警告閾値（%）
        'memory_threshold': 85,  # メモリ使用率の警告閾値（%）
        'cpu_threshold': 90   # CPU使用率の警告閾値（%）
    }

@app.route('/')
def dashboard():
    """メインダッシュボード"""
    version_info = get_version()
    return render_template('dashboard.html', 
                         services=Config.SERVICES, 
                         version=version_info)

@app.route('/logs')
def log_viewer():
    """ログ監視専用画面"""
    return render_template('log_viewer.html')



@app.route('/api/version')
def version_info():
    """バージョン情報を取得"""
    return jsonify(get_version())

# バックアップ関連のAPIエンドポイント
@app.route('/api/backup/create', methods=['POST'])
def create_backup():
    """バックアップを作成"""
    try:
        # バックアップディレクトリを設定
        if os.getenv('NAS_MODE'):
            backup_dir = Path('/app/backups')
            project_dir = Path('/nas-project')
        else:
            backup_dir = Path('/Users/Yoshi/nas-project/data/backups')
            project_dir = Path('/Users/Yoshi/nas-project')
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # バックアップファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"nas-project-backup-{timestamp}.zip"
        backup_path = backup_dir / backup_filename
        
        # プロジェクトディレクトリをZIP圧縮
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_dir):
                # 除外するディレクトリ
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
                
                for file in files:
                    # 除外するファイル
                    if file.endswith(('.pyc', '.pyo', '.log', '.tmp')):
                        continue
                    
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(project_dir)
                    zipf.write(file_path, arcname)
        
        # バックアップファイルのサイズを取得
        backup_size = backup_path.stat().st_size
        
        return jsonify({
            'success': True,
            'message': f'バックアップが作成されました: {backup_filename}',
            'filename': backup_filename,
            'size': backup_size,
            'path': str(backup_path)
        })
        
    except Exception as e:
        logger.error(f"バックアップ作成エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'バックアップの作成に失敗しました: {str(e)}'
        }), 500

@app.route('/api/backup/list')
def list_backups():
    """バックアップ一覧を取得"""
    try:
        # バックアップディレクトリを設定
        if os.getenv('NAS_MODE'):
            backup_dir = Path('/app/backups')
        else:
            backup_dir = Path('/Users/Yoshi/nas-project/data/backups')
        
        if not backup_dir.exists():
            return jsonify([])
        
        backups = []
        for backup_file in backup_dir.glob('*.zip'):
            stat = backup_file.stat()
            backups.append({
                'name': backup_file.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # 作成日時でソート（新しい順）
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify(backups)
        
    except Exception as e:
        logger.error(f"バックアップ一覧取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/download/<path:filename>')
def download_backup(filename):
    """バックアップファイルをダウンロード"""
    try:
        # バックアップディレクトリを設定
        if os.getenv('NAS_MODE'):
            backup_dir = Path('/app/backups')
        else:
            backup_dir = Path('/Users/Yoshi/nas-project/data/backups')
        
        backup_path = backup_dir / filename
        
        if not backup_path.exists():
            return jsonify({'error': 'バックアップファイルが見つかりません'}), 404
        
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        logger.error(f"バックアップダウンロードエラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/delete/<path:filename>', methods=['DELETE'])
def delete_backup(filename):
    """バックアップファイルを削除"""
    try:
        # バックアップディレクトリを設定
        if os.getenv('NAS_MODE'):
            backup_dir = Path('/app/backups')
        else:
            backup_dir = Path('/Users/Yoshi/nas-project/data/backups')
        
        backup_path = backup_dir / filename
        
        if not backup_path.exists():
            return jsonify({'error': 'バックアップファイルが見つかりません'}), 404
        
        backup_path.unlink()
        
        return jsonify({
            'success': True,
            'message': f'バックアップ「{filename}」が削除されました'
        })
        
    except Exception as e:
        logger.error(f"バックアップ削除エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'バックアップの削除に失敗しました: {str(e)}'
        }), 500

@app.route('/api/system/status')
def system_status():
    """システム状態を取得"""
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # メモリ使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # ディスク使用率
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # ネットワーク統計
        network = psutil.net_io_counters()
        
        # システム情報
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        status = {
            'cpu': {
                'percent': cpu_percent,
                'status': 'warning' if cpu_percent > Config.SYSTEM_MONITORING['cpu_threshold'] else 'success'
            },
            'memory': {
                'percent': memory_percent,
                'used': memory.used,
                'total': memory.total,
                'status': 'warning' if memory_percent > Config.SYSTEM_MONITORING['memory_threshold'] else 'success'
            },
            'disk': {
                'percent': disk_percent,
                'used': disk.used,
                'total': disk.total,
                'status': 'warning' if disk_percent > Config.SYSTEM_MONITORING['disk_threshold'] else 'success'
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            },
            'uptime': {
                'days': uptime.days,
                'hours': uptime.seconds // 3600,
                'minutes': (uptime.seconds % 3600) // 60
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"システム状態取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/services/status')
def services_status():
    """各サービスの稼働状況を確認"""
    services_status = {}
    
    for service_id, service_config in Config.SERVICES.items():
        try:
            # Fail2Banの場合は特別処理（WebUIがないため）
            if service_id == 'fail2ban':
                services_status[service_id] = {
                    'name': service_config['name'],
                    'status': 'running',  # Fail2Banは常に稼働中として表示
                    'url': service_config['url'],
                    'response_time': None,
                    'note': 'ダッシュボード内で監視'
                }
                continue
            
            # その他のサービスはHTTPリクエストで確認
            if service_config['url'] != '#':
                try:
                    # Dockerコンテナ内からのアクセスのため、localhostを使用
                    if os.getenv('NAS_MODE'):
                        # NAS環境ではlocalhostでアクセス
                        if 'YOUR_NAS_IP' in service_config['url']:
                            local_url = service_config['url'].replace('YOUR_NAS_IP', 'localhost')
                        else:
                            local_url = service_config['url']
                    else:
                        local_url = service_config['url']
                    
                    response = requests.get(f"{local_url}/", timeout=3)
                    services_status[service_id] = {
                        'name': service_config['name'],
                        'status': 'running' if response.status_code == 200 else 'error',
                        'url': service_config['url'],
                        'response_time': response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None
                    }
                except requests.exceptions.RequestException as e:
                    # HTTPリクエストが失敗した場合、Dockerコンテナの状態を確認
                    if os.getenv('NAS_MODE'):
                        try:
                            # Dockerコンテナの状態を確認
                            # サービスIDに応じて適切なコンテナ名を設定
                            if service_id == 'document_automation':
                                container_name = 'doc-automation-web'
                            elif service_id == 'meeting_minutes':
                                container_name = 'meeting-minutes-byc'
                            elif service_id == 'youtube_to_notion':
                                container_name = 'youtube-to-notion'
                            else:
                                container_name = service_id.replace('_', '-')
                            
                            result = subprocess.run([
                                'docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Status}}'
                            ], capture_output=True, text=True, timeout=5)
                            
                            if result.returncode == 0 and result.stdout.strip():
                                # コンテナが稼働している場合
                                services_status[service_id] = {
                                    'name': service_config['name'],
                                    'status': 'running',
                                    'url': service_config['url'],
                                    'response_time': None,
                                    'note': 'コンテナ稼働中（HTTP接続不可）'
                                }
                            else:
                                services_status[service_id] = {
                                    'name': service_config['name'],
                                    'status': 'stopped',
                                    'url': service_config['url'],
                                    'response_time': None
                                }
                        except subprocess.TimeoutExpired:
                            services_status[service_id] = {
                                'name': service_config['name'],
                                'status': 'unknown',
                                'url': service_config['url'],
                                'response_time': None
                            }
                    else:
                        services_status[service_id] = {
                            'name': service_config['name'],
                            'status': 'stopped',
                            'url': service_config['url'],
                            'response_time': None
                        }
            else:
                services_status[service_id] = {
                    'name': service_config['name'],
                    'status': 'unknown',
                    'url': service_config['url'],
                    'response_time': None
                }
        except requests.exceptions.RequestException:
            services_status[service_id] = {
                'name': service_config['name'],
                'status': 'stopped',
                'url': service_config['url'],
                'response_time': None
            }
        except Exception as e:
            logger.error(f"サービス {service_id} の状態確認エラー: {e}")
            services_status[service_id] = {
                'name': service_config['name'],
                'status': 'error',
                'url': service_config['url'],
                'response_time': None
            }
    
    return jsonify(services_status)

@app.route('/api/fail2ban/status')
def fail2ban_status():
    """Fail2Banの状態を取得"""
    try:
        # NAS環境では実際のFail2Banコンテナに接続
        if os.getenv('NAS_MODE'):
            # Dockerコンテナ経由でFail2Banの状態を取得
            result = subprocess.run([
                'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # アクティブなjailを取得
                jail_lines = [line for line in result.stdout.split('\n') if 'Jail list:' in line]
                if jail_lines:
                    jails = jail_lines[0].split('Jail list:')[1].strip().split(',')
                    jails = [jail.strip() for jail in jails if jail.strip()]
                else:
                    jails = []
                
                # 各jailの詳細情報を取得
                jail_details = {}
                for jail in jails:
                    jail_result = subprocess.run([
                        'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status', jail
                    ], capture_output=True, text=True, timeout=5)
                    
                    if jail_result.returncode == 0:
                        # BANされたIP数を抽出
                        banned_count = 0
                        for line in jail_result.stdout.split('\n'):
                            if 'Currently banned:' in line:
                                banned_count = int(line.split('Currently banned:')[1].strip())
                                break
                        
                        jail_details[jail] = {
                            'banned_count': banned_count,
                            'status': 'active'
                        }
                
                return jsonify({
                    'status': 'running',
                    'jails': jail_details,
                    'total_banned': sum(jail['banned_count'] for jail in jail_details.values())
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Fail2Banコンテナが起動していません'
                })
        else:
            # ローカル環境ではモックデータを返す
            return jsonify({
                'status': 'mock',
                'message': 'ローカル環境のため、モックデータを表示しています',
                'jails': {
                    'sshd': {'banned_count': 3, 'status': 'active'},
                    'nginx-http-auth': {'banned_count': 1, 'status': 'active'}
                },
                'total_banned': 4
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'status': 'error',
            'message': 'Fail2Banへの接続がタイムアウトしました'
        })
    except Exception as e:
        logger.error(f"Fail2Ban状態取得エラー: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/fail2ban/jails')
def fail2ban_jails():
    """Fail2Banのjail詳細情報を取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のFail2Banデータを取得
            result = subprocess.run([
                'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # アクティブなjailを取得
                jail_lines = [line for line in result.stdout.split('\n') if 'Jail list:' in line]
                if jail_lines:
                    jails = jail_lines[0].split('Jail list:')[1].strip().split(',')
                    jails = [jail.strip() for jail in jails if jail.strip()]
                else:
                    jails = []
                
                # 各jailの詳細情報を取得
                jail_details = {}
                for jail in jails:
                    jail_result = subprocess.run([
                        'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status', jail
                    ], capture_output=True, text=True, timeout=5)
                    
                    if jail_result.returncode == 0:
                        # BANされたIP数を抽出
                        banned_count = 0
                        for line in jail_result.stdout.split('\n'):
                            if 'Currently banned:' in line:
                                banned_count = int(line.split('Currently banned:')[1].strip())
                                break
                        
                        jail_details[jail] = {
                            'banned_count': banned_count,
                            'status': 'active',
                            'last_ban': 'N/A'  # 詳細な情報は別途取得が必要
                        }
                
                return jsonify({
                    'status': 'success',
                    'jails': jail_details,
                    'total_jails': len(jails)
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Fail2Banコンテナが起動していません',
                    'jails': {}
                })
        else:
            # ローカル環境ではモックデータを返す
            return jsonify({
                'status': 'mock',
                'jails': {
                    'sshd': {
                        'banned_count': 3,
                        'status': 'active',
                        'last_ban': '2024-01-15 14:30:00'
                    },
                    'nginx-http-auth': {
                        'banned_count': 1,
                        'status': 'active',
                        'last_ban': '2024-01-15 13:45:00'
                    },
                    'apache-auth': {
                        'banned_count': 0,
                        'status': 'inactive',
                        'last_ban': 'N/A'
                    }
                },
                'total_jails': 3
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'status': 'error',
            'message': 'Fail2Banへの接続がタイムアウトしました',
            'jails': {}
        })
    except Exception as e:
        logger.error(f"Fail2Ban jail詳細取得エラー: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'jails': {}
        })

@app.route('/api/fail2ban/ban-history')
def fail2ban_ban_history():
    """Fail2BanのBAN履歴を取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では現在BANされているIPアドレスを履歴として取得
            ban_history = []
            
            # シンプルなアプローチ: 直接的にBAN履歴を取得
            logger.info("BAN履歴を直接取得中")
            jails = ['sshd', 'nginx-http-auth', 'nginx-req-limit']
            
            for jail in jails:
                try:
                    result = subprocess.run([
                        'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status', jail
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'Banned IP list:' in line:
                                ip_line = line.split('Banned IP list:')[1].strip()
                                if ip_line and ip_line != '':
                                    banned_ips = [ip.strip() for ip in ip_line.split() if ip.strip()]
                                    
                                    for ip in banned_ips:
                                        location = get_ip_location(ip)
                                        logger.info(f"BAN履歴追加: IP={ip}, Location={location}")
                                        ban_history.append({
                                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                            'ip': ip,
                                            'jail': jail,
                                            'action': 'Ban',
                                            'location': location
                                        })
                                break
                except Exception as e:
                    logger.warning(f"jail {jail} の情報取得エラー: {e}")
                    continue
            
            # 表示件数を制限（最新20件）
            MAX_BAN_HISTORY_DISPLAY = 20
            limited_ban_history = ban_history[:MAX_BAN_HISTORY_DISPLAY]
            
            return jsonify({
                'status': 'success',
                'ban_history': limited_ban_history,
                'total_bans': len(ban_history),
                'displayed_bans': len(limited_ban_history),
                'has_more': len(ban_history) > MAX_BAN_HISTORY_DISPLAY
            })
        else:
            # ローカル環境ではモックデータを返す
            return jsonify({
                'status': 'mock',
                'ban_history': [
                    {
                        'timestamp': '2024-01-15 14:30:15',
                        'ip': '203.0.113.100',
                        'jail': 'sshd',
                        'action': 'Ban'
                    },
                    {
                        'timestamp': '2024-01-15 13:45:22',
                        'ip': '198.51.100.50',
                        'jail': 'sshd',
                        'action': 'Ban'
                    },
                    {
                        'timestamp': '2024-01-15 12:20:10',
                        'ip': '192.0.2.25',
                        'jail': 'sshd',
                        'action': 'Ban'
                    },
                    {
                        'timestamp': '2024-01-15 11:15:30',
                        'ip': '203.0.113.200',
                        'jail': 'nginx-http-auth',
                        'action': 'Ban'
                    }
                ],
                'total_bans': 4,
                'displayed_bans': 4,
                'has_more': False
            })
            
    except Exception as e:
        logger.error(f"Fail2Ban BAN履歴取得エラー: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'ban_history': []
        })

@app.route('/api/fail2ban/unban', methods=['POST'])
def fail2ban_unban():
    """Fail2BanでIPアドレスのBANを解除"""
    try:
        data = request.get_json()
        ip_address = data.get('ip')
        jail_name = data.get('jail', 'all')
        
        if not ip_address:
            return jsonify({
                'success': False,
                'message': 'IPアドレスが指定されていません'
            }), 400
        
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のFail2Banコマンドを実行
            if jail_name == 'all':
                # 全jailからBAN解除
                result = subprocess.run([
                    'docker', 'exec', 'fail2ban', 'fail2ban-client', 'unban', ip_address
                ], capture_output=True, text=True, timeout=10)
            else:
                # 特定のjailからBAN解除
                result = subprocess.run([
                    'docker', 'exec', 'fail2ban', 'fail2ban-client', 'set', jail_name, 'unbanip', ip_address
                ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': f'IPアドレス {ip_address} のBANを解除しました'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'BAN解除に失敗しました: {result.stderr}'
                }), 500
        else:
            # ローカル環境ではモックレスポンス
            return jsonify({
                'success': True,
                'message': f'IPアドレス {ip_address} のBANを解除しました（モック）'
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': 'BAN解除処理がタイムアウトしました'
        }), 500
    except Exception as e:
        logger.error(f"Fail2Ban BAN解除エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'BAN解除に失敗しました: {str(e)}'
        }), 500

@app.route('/api/backup/list')
def backup_list():
    """バックアップ一覧を取得"""
    try:
        # NAS環境かどうかでパスを切り替え
        if os.getenv('NAS_MODE'):
            backup_dir = Path('/app/backups')
        else:
            backup_dir = Path('/Users/Yoshi/nas-project/data/backups')
        
        if not backup_dir.exists():
            backup_dir.mkdir(parents=True, exist_ok=True)
        
        backups = []
        for backup_file in backup_dir.glob('backup_*.tar.gz'):
            stat = backup_file.stat()
            backups.append({
                'name': backup_file.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'path': str(backup_file)
            })
        
        # 作成日時でソート（新しい順）
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify(backups)
        
    except Exception as e:
        logger.error(f"バックアップ一覧取得エラー: {e}")
        return jsonify({'error': str(e)}), 500


def get_system_status_data():
    """システム状態データを取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のシステムデータを取得
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'timestamp': datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            }
        else:
            # ローカル環境ではモックデータを返す
            return {
                'cpu_percent': 25.5,
                'memory_percent': 68.2,
                'memory_available_gb': 2.1,
                'disk_percent': 45.8,
                'disk_free_gb': 15.3,
                'timestamp': datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            }
    except Exception as e:
        logger.error(f"システムデータ取得エラー: {e}")
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'memory_available_gb': 0,
            'disk_percent': 0,
            'disk_free_gb': 0,
            'timestamp': datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'),
            'error': str(e)
        }

def get_fail2ban_status_data():
    """Fail2Ban状態データを取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のFail2Banデータを取得
            result = subprocess.run([
                'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status'
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                # アクティブなjailを取得
                jail_lines = [line for line in result.stdout.split('\n') if 'Jail list:' in line]
                if jail_lines:
                    jails = jail_lines[0].split('Jail list:')[1].strip().split(',')
                    jails = [jail.strip() for jail in jails if jail.strip()]
                else:
                    jails = []

                # 各jailの詳細情報を取得
                jail_details = {}
                total_banned = 0
                for jail in jails:
                    jail_result = subprocess.run([
                        'docker', 'exec', 'fail2ban', 'fail2ban-client', 'status', jail
                    ], capture_output=True, text=True, timeout=5)

                    if jail_result.returncode == 0:
                        banned_count = 0
                        for line in jail_result.stdout.split('\n'):
                            if 'Currently banned:' in line:
                                banned_count = int(line.split('Currently banned:')[1].strip())
                                break

                        jail_details[jail] = {
                            'banned_count': banned_count,
                            'status': 'active'
                        }
                        total_banned += banned_count

                return {
                    'status': 'running',
                    'jails': jail_details,
                    'total_banned': total_banned,
                    'active_jails': len(jails)
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Fail2Banコンテナが起動していません',
                    'total_banned': 0,
                    'active_jails': 0
                }
        else:
            # ローカル環境ではモックデータを返す
            return {
                'status': 'mock',
                'jails': {
                    'sshd': {'banned_count': 3, 'status': 'active'},
                    'nginx-http-auth': {'banned_count': 1, 'status': 'active'}
                },
                'total_banned': 4,
                'active_jails': 2
            }
    except Exception as e:
        logger.error(f"Fail2Banデータ取得エラー: {e}")
        return {
            'status': 'error',
            'message': str(e),
            'total_banned': 0,
            'active_jails': 0
        }

def get_docker_status_data():
    """Docker状態データを取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のDockerデータを取得
            result = subprocess.run([
                'docker', 'ps', '--format', 'json'
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        container_info = json.loads(line)
                        containers.append({
                            'name': container_info['Names'],
                            'image': container_info['Image'],
                            'status': container_info['Status']
                        })

                running_count = len([c for c in containers if 'Up' in c['status']])
                return {
                    'total_containers': len(containers),
                    'running_containers': running_count,
                    'stopped_containers': len(containers) - running_count,
                    'containers': containers
                }
            else:
                return {
                    'total_containers': 0,
                    'running_containers': 0,
                    'stopped_containers': 0,
                    'containers': [],
                    'error': 'Dockerコンテナ情報の取得に失敗しました'
                }
        else:
            # ローカル環境ではモックデータを返す
            return {
                'total_containers': 3,
                'running_containers': 3,
                'stopped_containers': 0,
                'containers': [
                    {'name': 'nas-dashboard', 'image': 'nas-dashboard:latest', 'status': 'Up 2 hours'},
                    {'name': 'meeting-minutes-byc', 'image': 'meeting-minutes-byc:latest', 'status': 'Up 1 day'},
                    {'name': 'doc-automation-web', 'image': 'document-automation-web:latest', 'status': 'Up 1 day'}
                ]
            }
    except Exception as e:
        logger.error(f"Dockerデータ取得エラー: {e}")
        return {
            'total_containers': 0,
            'running_containers': 0,
            'stopped_containers': 0,
            'containers': [],
            'error': str(e)
        }

def generate_report_content(system_data, fail2ban_data, docker_data, ban_history_data=None):
    """レポート内容を生成"""
    timestamp = system_data['timestamp']
    
    # システム状況の評価
    cpu_status = "正常" if system_data['cpu_percent'] < 80 else "注意" if system_data['cpu_percent'] < 95 else "危険"
    memory_status = "正常" if system_data['memory_percent'] < 80 else "注意" if system_data['memory_percent'] < 95 else "危険"
    disk_status = "正常" if system_data['disk_percent'] < 80 else "注意" if system_data['disk_percent'] < 95 else "危険"
    
    # 推奨事項の生成
    recommendations = []
    if system_data['cpu_percent'] > 80:
        recommendations.append("- CPU使用率が高いため、プロセスの確認を推奨")
    if system_data['memory_percent'] > 80:
        recommendations.append("- メモリ使用率が高いため、メモリの最適化を推奨")
    if system_data['disk_percent'] > 80:
        recommendations.append("- ディスク使用率が高いため、不要ファイルの削除を推奨")
    if fail2ban_data['total_banned'] > 10:
        recommendations.append("- 攻撃が多発しているため、セキュリティ設定の見直しを推奨")
    if docker_data['running_containers'] < docker_data['total_containers']:
        recommendations.append("- 停止中のコンテナがあるため、サービスの確認を推奨")
    
    if not recommendations:
        recommendations.append("- システムは正常に稼働しています")
        recommendations.append("- 定期的なバックアップの実行を推奨")
        recommendations.append("- セキュリティアップデートの適用を推奨")
    
    # Fail2Banの詳細情報
    fail2ban_details = ""
    if fail2ban_data['status'] == 'running' and 'jails' in fail2ban_data:
        fail2ban_details = "\n".join([
            f"- {jail}: {details['banned_count']}件" 
            for jail, details in fail2ban_data['jails'].items()
        ])
    elif fail2ban_data['status'] == 'error':
        fail2ban_details = f"- エラー: {fail2ban_data.get('message', '不明なエラー')}"
    else:
        fail2ban_details = "- データ取得不可"
    
    # BANされたIPの詳細情報を取得
    banned_ips_details = ""
    if ban_history_data:
        if ban_history_data:
            banned_ips_details = "\n".join([
                f"- {ban['ip']} | {ban['jail']} | {ban['timestamp']}"
                for ban in ban_history_data[:10]  # 最新10件
            ])
        else:
            banned_ips_details = "- BANされたIPなし"
    else:
        banned_ips_details = "- BANされたIP取得不可"
    
    # Dockerコンテナの詳細情報
    docker_details = ""
    if docker_data['containers']:
        docker_details = "\n".join([
            f"- {container['name']}: {container['status']}" 
            for container in docker_data['containers']
        ])
    else:
        docker_details = "- コンテナ情報取得不可"
    
    # 週番号を計算
    from datetime import datetime
    week_num = datetime.now().isocalendar()[1]
    year = datetime.now().year
    
    # BAN履歴の詳細情報を準備
    ban_activity = ""
    if ban_history_data:
        ban_activity = "\n".join([f"- {ban['ip']} | {ban['jail']} | {ban['timestamp']} | {ban['action']}" for ban in ban_history_data[:20]])
    else:
        ban_activity = "なし"
    
    # 攻撃元TOP5を準備
    attack_sources = ""
    if ban_history_data:
        # BAN実行のみを抽出
        ban_actions = [ban for ban in ban_history_data if ban['action'] == 'Ban']
        attack_sources = "\n".join([f"- {ban['ip']} ({ban['jail']})" for ban in ban_actions[:5]])
    else:
        attack_sources = "なし"
    
    # 推奨事項を準備
    recommendations_text = "\n".join(recommendations)
    
    # BANされたIPリストを準備
    banned_ip_list = ""
    if ban_history_data:
        # 現在BANされているIPのみを抽出
        current_banned = [ban for ban in ban_history_data if ban['action'] == 'Ban']
        banned_ip_list = " ".join([ban['ip'] for ban in current_banned[:20]])
    else:
        banned_ip_list = "なし"
    
    # Jailリストを準備
    jail_list = fail2ban_details.replace('- ', '').replace('件', '').replace('\n', ', ')
    
    # 統計情報を計算
    ban_count = 0
    unban_count = 0
    if ban_history_data:
        ban_count = len([ban for ban in ban_history_data if ban['action'] == 'Ban'])
        unban_count = len([ban for ban in ban_history_data if ban['action'] == 'Unban'])
    
    report_content = f"""
===================================================
Fail2ban 週次セキュリティレポート
週: {year}-W{week_num:02d}
作成日時: {timestamp}
サーバー: DXP2800
===================================================

【現在のセキュリティ状況】
Status
|- Number of jail:	{fail2ban_data['active_jails']}
`- Jail list:	{jail_list}

【各Jailの詳細】

[SSH保護]
Status for the jail: sshd
|- Filter
|  |- Currently failed:	0
|  |- Total failed:	{fail2ban_data.get('total_failed', 0)}
|  `- File list:	/var/log/auth.log
`- Actions
  |- Currently banned:	{fail2ban_data['total_banned']}
  |- Total banned:	{fail2ban_data['total_banned']}
  `- Banned IP list:	{banned_ip_list}

[Web認証保護]
Status for the jail: nginx-http-auth
|- Filter
|  |- Currently failed:	0
|  |- Total failed:	0
|  `- File list:	/var/log/nginx/error.log
`- Actions
  |- Currently banned:	0
  |- Total banned:	0
  `- Banned IP list:	

[レート制限保護]
Status for the jail: nginx-req-limit
|- Filter
|  |- Currently failed:	0
|  |- Total failed:	0
|  `- File list:	/var/log/nginx/error.log
`- Actions
  |- Currently banned:	0
  |- Total banned:	0
  `- Banned IP list:	

【過去7日間のBAN活動（最新20件）】
{ban_activity}

【統計】
今週のBAN実行回数: {ban_count} 回
今週のUNBAN実行回数: {unban_count} 回

【攻撃元TOP5】
{attack_sources}

【セキュリティ設定】
- SSH BAN期間: 7日間、最大試行回数: 3回
- Web認証 BAN期間: 24時間、最大試行回数: 2回
- レート制限 BAN期間: 1時間、最大試行回数: 5回

【システム状況】
- CPU使用率: {system_data['cpu_percent']:.1f}% ({cpu_status})
- メモリ使用率: {system_data['memory_percent']:.1f}% ({memory_status})
- ディスク使用率: {system_data['disk_percent']:.1f}% ({disk_status})

【推奨事項】
{recommendations_text}
        """
    
    return report_content

def generate_monthly_report_content(system_data, fail2ban_data, docker_data, ban_history_data, ai_analysis):
    """月次AI分析レポート内容を生成"""
    timestamp = system_data['timestamp']
    
    # 月番号を計算
    from datetime import datetime
    month_num = datetime.now().month
    year = datetime.now().year
    
    # AI分析結果を取得
    summary = ai_analysis.get('summary', '分析結果なし')
    insights = ai_analysis.get('insights', [])
    recommendations = ai_analysis.get('recommendations', [])
    risk_level = ai_analysis.get('risk_level', 'UNKNOWN')
    trends = ai_analysis.get('trends', {})
    
    # 統計情報を準備
    ban_count = len(ban_history_data) if ban_history_data else 0
    unban_count = 0  # UNBANは現在未実装
    
    # 攻撃元TOP5を準備
    attack_sources = ""
    if ban_history_data:
        attack_sources = "\n".join([f"- {ban['ip']} ({ban['jail']})" for ban in ban_history_data[:5]])
    else:
        attack_sources = "なし"
    
    # 推奨事項を準備
    recommendations_text = "\n".join([f"- {rec}" for rec in recommendations])
    
    # 洞察を準備
    insights_text = "\n".join([f"- {insight}" for insight in insights])
    
    # トレンド情報を準備
    ban_trend = trends.get('ban_trend', '不明')
    attack_patterns = trends.get('attack_patterns', '分析中')
    system_health = trends.get('system_health', '良好')
    
    report_content = f"""
===================================================
Fail2ban 月次AI分析セキュリティレポート
月: {year}-{month_num:02d}
作成日時: {timestamp}
サーバー: DXP2800
===================================================

【AI分析サマリー】
{summary}

【リスクレベル】
{risk_level}

【重要な洞察】
{insights_text}

【AI推奨事項】
{recommendations_text}

【セキュリティ統計】
- 今月のBAN実行回数: {ban_count} 回
- 今月のUNBAN実行回数: {unban_count} 回
- アクティブなJail数: {fail2ban_data['active_jails']} 個
- 総BAN数: {fail2ban_data['total_banned']} 件

【攻撃元TOP5】
{attack_sources}

【トレンド分析】
- BAN傾向: {ban_trend}
- 攻撃パターン: {attack_patterns}
- システム健全性: {system_health}

【システム状況】
- CPU使用率: {system_data['cpu_percent']:.1f}%
- メモリ使用率: {system_data['memory_percent']:.1f}%
- ディスク使用率: {system_data['disk_percent']:.1f}%

【過去30日間のBAN活動（最新20件）】
{chr(10).join([f"- {ban['ip']} | {ban['jail']} | {ban['timestamp']}" for ban in ban_history_data[:20]]) if ban_history_data else "なし"}

【Dockerコンテナ状況】
- 稼働中コンテナ: {docker_data['running_containers']}/{docker_data['total_containers']} 個
- 停止中コンテナ: {docker_data['stopped_containers']} 個

【AI分析詳細】
- 分析モデル: Gemini 2.0 Flash
- 分析期間: 過去30日間
- データソース: Fail2banログ、システム統計

===================================================
このレポートはAI分析により自動生成されました。
NAS統合管理システム
===================================================
    """
    
    return report_content

@app.route('/api/reports/monthly', methods=['POST'])
def generate_monthly_report():
    """月次AI分析レポートを生成"""
    try:
        # 過去30日間のデータを取得
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # システムデータを取得
        system_data = get_system_status_data()
        fail2ban_data = get_fail2ban_status_data()
        docker_data = get_docker_status_data()
        
        # 過去30日間のBAN履歴を取得
        logger.info("月次レポート用BAN履歴取得開始")
        ban_history_data = get_monthly_ban_history()
        logger.info(f"月次BAN履歴データ取得完了: {len(ban_history_data) if ban_history_data else 0}件")
        
        # AI分析用データを準備
        security_data = {
            'ban_history': ban_history_data,
            'system_stats': system_data,
            'fail2ban_stats': fail2ban_data,
            'docker_stats': docker_data,
            'period': thirty_days_ago.strftime('%Y-%m')
        }
        
        # AI分析実行
        logger.info("AI分析開始")
        ai_analyzer = AIAnalyzer()
        ai_analysis = ai_analyzer.analyze_monthly_security_data(security_data)
        logger.info("AI分析完了")
        
        # 月次レポート内容を生成
        report_content = generate_monthly_report_content(system_data, fail2ban_data, docker_data, ban_history_data, ai_analysis)
        
        # レポートファイルを保存
        if os.getenv('NAS_MODE'):
            report_dir = Path('/app/reports')
        else:
            report_dir = Path('/Users/Yoshi/nas-project/data/reports')
        
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f"monthly_report_{timestamp}.txt"
        report_file.write_text(report_content, encoding='utf-8')
        
        # メール送信のオプション
        send_email = request.json.get('send_email', False) if request.is_json else False
        
        if send_email:
            try:
                email_to = os.getenv('EMAIL_TO')
                if email_to:
                    email_sender = EmailSender()
                    email_sender.send_monthly_report(email_to, report_content, ai_analysis)
                    logger.info("月次AI分析レポートメール送信完了")
                else:
                    logger.warning("EMAIL_TO環境変数が設定されていません")
            except Exception as email_error:
                logger.error(f"メール送信エラー: {email_error}")
        
        return jsonify({
            'success': True,
            'message': f'月次AI分析レポートが生成されました: {report_file.name}',
            'output': report_content,
            'ai_analysis': ai_analysis,
            'email_sent': send_email and os.getenv('EMAIL_TO') is not None
        })
            
    except Exception as e:
        logger.error(f"月次AI分析レポート生成エラー: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/reports/weekly', methods=['POST'])
def generate_weekly_report():
    """週次レポートを生成"""
    try:
        # 実際のシステムデータを取得
        system_data = get_system_status_data()
        fail2ban_data = get_fail2ban_status_data()
        docker_data = get_docker_status_data()
        
        # BAN履歴を取得（位置情報なし）
        logger.info("BAN履歴取得開始")
        ban_history_data = get_ban_history_simple()
        logger.info(f"BAN履歴データ取得完了: {len(ban_history_data) if ban_history_data else 0}件")
        if ban_history_data:
            for ban in ban_history_data:
                logger.info(f"BAN履歴: {ban['ip']} | {ban['jail']} | {ban['timestamp']}")
        
        # レポート内容を生成
        report_content = generate_report_content(system_data, fail2ban_data, docker_data, ban_history_data)
        
        # レポートファイルを保存
        if os.getenv('NAS_MODE'):
            report_dir = Path('/app/reports')
        else:
            report_dir = Path('/Users/Yoshi/nas-project/data/reports')
        
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f"weekly_report_{timestamp}.txt"
        report_file.write_text(report_content, encoding='utf-8')
        
        # メール送信のオプション
        send_email = request.json.get('send_email', False) if request.is_json else False
        
        if send_email:
            try:
                email_to = os.getenv('EMAIL_TO')
                if email_to:
                    email_sender = EmailSender()
                    report_data = {
                        'system_data': system_data,
                        'fail2ban_data': fail2ban_data,
                        'docker_data': docker_data,
                        'ban_history_data': ban_history_data
                    }
                    email_sender.send_weekly_report(email_to, report_content, report_data)
                    logger.info("週次レポートメール送信完了")
                else:
                    logger.warning("EMAIL_TO環境変数が設定されていません")
            except Exception as email_error:
                logger.error(f"メール送信エラー: {email_error}")
        
        return jsonify({
            'success': True,
            'message': f'週次レポートが生成されました: {report_file.name}',
            'output': report_content,
            'email_sent': send_email and os.getenv('EMAIL_TO') is not None
        })
            
    except Exception as e:
        logger.error(f"週次レポート生成エラー: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/docker/containers')
def docker_containers():
    """Dockerコンテナの状態を取得"""
    try:
        # NAS環境では実際のDockerコンテナ情報を取得
        if os.getenv('NAS_MODE'):
            result = subprocess.run([
                'docker', 'ps', '--format', 'json'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        container_info = json.loads(line)
                        containers.append({
                            'id': container_info['ID'],
                            'name': container_info['Names'],
                            'image': container_info['Image'],
                            'status': container_info['Status'],
                            'ports': container_info['Ports']
                        })
                
                return jsonify(containers)
            else:
                return jsonify({'error': 'Dockerコンテナ情報の取得に失敗しました'}), 500
        else:
            # ローカル環境ではモックデータを返す
            return jsonify([
                {
                    'id': 'mock-container-1',
                    'name': 'nas-dashboard',
                    'image': 'nas-dashboard:latest',
                    'status': 'Up 2 hours',
                    'ports': '9000/tcp'
                },
                {
                    'id': 'mock-container-2', 
                    'name': 'meeting-minutes-byc',
                    'image': 'meeting-minutes-byc:latest',
                    'status': 'Up 1 day',
                    'ports': '5002/tcp'
                }
            ])
            
    except Exception as e:
        logger.error(f"Dockerコンテナ情報取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

# Insta360自動同期システム関連のAPIエンドポイント
@app.route('/api/insta360/status')
def insta360_status():
    """Insta360自動同期システムの状態を取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のDockerコンテナの状態を確認
            result = subprocess.run([
                'docker', 'ps', '--filter', 'name=insta360-auto-sync', '--format', '{{.Status}}'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                # コンテナが稼働している場合
                return jsonify({
                    'status': 'running',
                    'container_status': result.stdout.strip(),
                    'message': 'Insta360自動同期システムが稼働中です'
                })
            else:
                return jsonify({
                    'status': 'stopped',
                    'container_status': 'Not running',
                    'message': 'Insta360自動同期システムが停止しています'
                })
        else:
            # ローカル環境ではモックデータを返す
            return jsonify({
                'status': 'mock',
                'container_status': 'Up 1 day',
                'message': 'ローカル環境のため、モックデータを表示しています'
            })
            
    except Exception as e:
        logger.error(f"Insta360状態取得エラー: {e}")
        return jsonify({
            'status': 'error',
            'message': f'状態取得に失敗しました: {str(e)}'
        }), 500


@app.route('/api/insta360/logs')
def insta360_logs():
    """Insta360同期ログを取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のログファイルを読み取り
            log_paths = [
                '/app/logs/insta360_sync.log',
                '/app/logs/cleanup.log'
            ]
            
            logs = []
            for log_path in log_paths:
                if os.path.exists(log_path):
                    try:
                        # 最後の100行を取得
                        with open(log_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            recent_lines = lines[-100:] if len(lines) > 100 else lines
                            
                            logs.append({
                                'filename': os.path.basename(log_path),
                                'path': log_path,
                                'size': os.path.getsize(log_path),
                                'lines': len(lines),
                                'recent_lines': recent_lines,
                                'last_modified': datetime.fromtimestamp(os.path.getmtime(log_path)).isoformat()
                            })
                    except Exception as e:
                        logger.warning(f"ログファイル読み取りエラー {log_path}: {e}")
                        continue
            
            return jsonify({
                'success': True,
                'logs': logs,
                'total_logs': len(logs),
                'timestamp': datetime.now().isoformat()
            })
        else:
            # ローカル環境ではモックデータを返す
            return jsonify({
                'success': True,
                'logs': [
                    {
                        'filename': 'insta360_sync.log',
                        'path': '/app/logs/insta360_sync.log',
                        'size': 1024,
                        'lines': 50,
                        'recent_lines': [
                            '2024-01-15 14:30:15 - INFO - Insta360ファイル同期を開始します\n',
                            '2024-01-15 14:30:16 - INFO - 転送対象ファイル: 3件\n',
                            '2024-01-15 14:30:20 - INFO - ファイル転送完了: VID_20240115_143020.mp4\n',
                            '2024-01-15 14:30:25 - INFO - Insta360ファイル同期が完了しました\n'
                        ],
                        'last_modified': datetime.now().isoformat()
                    }
                ],
                'total_logs': 1,
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Insta360ログ取得エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'ログ取得に失敗しました: {str(e)}',
            'logs': [],
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/insta360/test-connection')
def insta360_test_connection():
    """Insta360同期システムの接続テスト"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のテストを実行
            result = subprocess.run([
                'docker', 'exec', 'insta360-auto-sync', 'python', '/app/scripts/sync.py', '--test'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': '接続テストが成功しました',
                    'output': result.stdout,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'接続テストでエラーが発生しました: {result.stderr}',
                    'output': result.stdout,
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }), 500
        else:
            # ローカル環境ではモックレスポンス
            return jsonify({
                'success': True,
                'message': '接続テストが成功しました（モック）',
                'output': 'モック環境のため、実際のテストは実行されませんでした',
                'timestamp': datetime.now().isoformat()
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': '接続テストがタイムアウトしました',
            'timestamp': datetime.now().isoformat()
        }), 500
    except Exception as e:
        logger.error(f"Insta360接続テストエラー: {e}")
        return jsonify({
            'success': False,
            'message': f'接続テストに失敗しました: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500








@app.route('/api/docker/containers')
def get_docker_containers():
    """Dockerコンテナ一覧を取得"""
    try:
        if os.getenv('NAS_MODE'):
            # NAS環境では実際のDockerコンテナを取得
            result = subprocess.run([
                'docker', 'ps', '-a', '--format', 'json'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            container_data = json.loads(line)
                            containers.append({
                                'id': container_data.get('ID', ''),
                                'name': container_data.get('Names', ''),
                                'image': container_data.get('Image', ''),
                                'status': container_data.get('Status', ''),
                                'state': container_data.get('State', ''),
                                'created': container_data.get('CreatedAt', ''),
                                'ports': container_data.get('Ports', '')
                            })
                        except json.JSONDecodeError:
                            continue
                
                return jsonify({
                    'success': True,
                    'containers': containers,
                    'total_containers': len(containers),
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Dockerコンテナ取得に失敗しました: {result.stderr}',
                    'containers': [],
                    'timestamp': datetime.now().isoformat()
                }), 500
        else:
            # ローカル環境でも実際のDockerコンテナを取得を試行
            try:
                result = subprocess.run([
                    'docker', 'ps', '-a', '--format', 'json'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    containers = []
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            try:
                                container_data = json.loads(line)
                                containers.append({
                                    'id': container_data.get('ID', ''),
                                    'name': container_data.get('Names', ''),
                                    'image': container_data.get('Image', ''),
                                    'status': container_data.get('Status', ''),
                                    'state': container_data.get('State', ''),
                                    'created': container_data.get('CreatedAt', ''),
                                    'ports': container_data.get('Ports', '')
                                })
                            except json.JSONDecodeError:
                                continue
                    
                    return jsonify({
                        'success': True,
                        'containers': containers,
                        'total_containers': len(containers),
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    # Dockerコンテナが見つからない場合はモックデータを返す
                    return jsonify({
                        'success': True,
                        'containers': [
                            {
                                'id': 'abc123def456',
                                'name': 'nas-dashboard',
                                'image': 'nas-dashboard:latest',
                                'status': 'Up 2 hours',
                                'state': 'running',
                                'created': '2024-01-15T12:00:00Z',
                                'ports': '9001->9000/tcp'
                            },
                            {
                                'id': 'def456ghi789',
                                'name': 'amazon-analytics',
                                'image': 'amazon-analytics:latest',
                                'status': 'Up 1 hour',
                                'state': 'running',
                                'created': '2024-01-15T13:00:00Z',
                                'ports': '8000->8000/tcp'
                            }
                        ],
                        'total_containers': 2,
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                # Dockerコマンドが失敗した場合はモックデータを返す
                return jsonify({
                    'success': True,
                    'containers': [
                        {
                            'id': 'abc123def456',
                            'name': 'nas-dashboard',
                            'image': 'nas-dashboard:latest',
                            'status': 'Up 2 hours',
                            'state': 'running',
                            'created': '2024-01-15T12:00:00Z',
                            'ports': '9001->9000/tcp'
                        }
                    ],
                    'total_containers': 1,
                    'timestamp': datetime.now().isoformat()
                })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': 'Dockerコンテナ取得がタイムアウトしました',
            'containers': [],
            'timestamp': datetime.now().isoformat()
        }), 500
    except Exception as e:
        logger.error(f"Dockerコンテナ取得エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'Dockerコンテナ取得に失敗しました: {str(e)}',
            'containers': [],
            'timestamp': datetime.now().isoformat()
        }), 500






@app.route('/api/docker/logs/<container_name>')
def get_docker_logs(container_name):
    """特定のDockerコンテナのログを取得（シンプル実装）"""
    try:
        result = subprocess.run([
            'docker', 'logs', '--tail', '100', container_name
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            logs = result.stdout.split('\n')
            # 空行と空文字列をフィルタリング
            filtered_logs = [log.strip() for log in logs if log.strip()]
            
            # ログが空の場合はメッセージを追加
            if not filtered_logs:
                filtered_logs = [f"コンテナ '{container_name}' にはログがありません"]
            
            return jsonify({
                'success': True,
                'logs': filtered_logs,
                'container_name': container_name,
                'total_lines': len(filtered_logs),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': f'ログ取得に失敗しました: {result.stderr}',
                'logs': [],
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Dockerログ取得エラー ({container_name}): {e}")
        return jsonify({
            'success': False,
            'message': f'ログ取得に失敗しました: {str(e)}',
            'logs': [],
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/logs/text')
def get_text_logs():
    """テキストログ一覧を取得（システム別）"""
    try:
        if os.getenv('NAS_MODE') and os.path.exists('/nas-project-data'):
            # NAS環境では実際のログファイルを読み取り
            log_systems = {
                'meeting-minutes-byc': {
                    'name': 'Meeting Minutes BYC',
                    'log_file': '/nas-project-data/meeting-minutes-byc/logs/app.log'
                },
                'amazon-analytics': {
                    'name': 'Amazon Analytics',
                    'log_file': '/nas-project-data/amazon-analytics/logs/app.log'
                },
                'document-automation': {
                    'name': 'Document Automation',
                    'log_file': '/nas-project-data/document-automation/logs/app.log'
                },
                'youtube-to-notion': {
                    'name': 'YouTube to Notion',
                    'log_file': '/nas-project-data/youtube-to-notion/logs/app.log'
                },
                'nas-dashboard': {
                    'name': 'NAS Dashboard',
                    'log_file': '/nas-project-data/nas-dashboard/logs/app.log'
                }
            }
        else:
            # Dockerコンテナ内ではマウントされたパスを使用
            log_systems = {
                'nas-dashboard': {
                    'name': 'NAS Dashboard',
                    'log_file': '/app/logs/app.log'
                }
            }
        
        systems = []
        for system_id, system_info in log_systems.items():
            if os.path.exists(system_info['log_file']):
                try:
                    with open(system_info['log_file'], 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        # 最新の10行を取得
                        recent_lines = lines[-10:] if len(lines) > 10 else lines
                        logs = [line.strip() for line in recent_lines if line.strip()]
                        systems.append({
                            'id': system_id,
                            'name': system_info['name'],
                            'logs': logs,
                            'total_lines': len(logs)
                        })
                except Exception as e:
                    logger.warning(f"ログファイル読み取りエラー {system_info['log_file']}: {e}")
                    continue
        
        return jsonify({
            'success': True,
            'systems': systems,
            'total_systems': len(systems),
            'timestamp': datetime.now().isoformat()
        })
            
    except Exception as e:
        logger.error(f"テキストログ取得エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'ログ取得に失敗しました: {str(e)}',
            'systems': [],
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/logs/text/<system_id>')
def get_text_logs_by_system(system_id):
    """特定システムのテキストログを取得"""
    try:
        if os.getenv('NAS_MODE') and os.path.exists('/nas-project-data'):
            # NAS環境では実際のログファイルを読み取り
            log_files = {
                'meeting-minutes-byc': '/nas-project-data/meeting-minutes-byc/logs/app.log',
                'amazon-analytics': '/nas-project-data/amazon-analytics/logs/app.log',
                'document-automation': '/nas-project-data/document-automation/logs/app.log',
                'youtube-to-notion': '/nas-project-data/youtube-to-notion/logs/app.log',
                'nas-dashboard': '/nas-project-data/nas-dashboard/logs/app.log'
            }
        else:
            # Dockerコンテナ内ではマウントされたパスを使用
            log_files = {
                'nas-dashboard': '/app/logs/app.log'
            }
        
        if system_id not in log_files:
            return jsonify({
                'success': False,
                'message': f'システム {system_id} が見つかりません',
                'logs': [],
                'timestamp': datetime.now().isoformat()
            }), 404
        
        log_file = log_files[system_id]
        if not os.path.exists(log_file):
            return jsonify({
                'success': False,
                'message': f'ログファイルが見つかりません: {log_file}',
                'logs': [],
                'timestamp': datetime.now().isoformat()
            }), 404
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                # 最新の50行を取得
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                logs = [line.strip() for line in recent_lines if line.strip()]
            
            return jsonify({
                'success': True,
                'logs': logs,
                'total_lines': len(logs),
                'system_id': system_id,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"ログファイル読み取りエラー {log_file}: {e}")
            return jsonify({
                'success': False,
                'message': f'ログファイル読み取りエラー: {str(e)}',
                'logs': [],
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"テキストログ取得エラー: {e}")
        return jsonify({
            'success': False,
            'message': f'ログ取得に失敗しました: {str(e)}',
            'logs': [],
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
