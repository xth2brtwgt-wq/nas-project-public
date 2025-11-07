#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insta360自動同期システム - マウント管理ユーティリティ
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional, Tuple
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MountManager:
    """マウント管理クラス"""
    
    def __init__(self, mount_point: str, mac_config: Optional[Dict[str, Any]] = None):
        """
        初期化
        
        Args:
            mount_point: マウントポイントのパス（例: /mnt/mac-share）
            mac_config: Mac接続設定（IP、ユーザー名、パスワードなど）
        """
        self.mount_point = Path(mount_point)
        self.mac_config = mac_config or {}
        
        # Mac接続設定
        self.mac_ip = self.mac_config.get('ip_address', '')
        self.mac_username = self.mac_config.get('username', '')
        self.mac_password = self.mac_config.get('password', '')
        self.mac_share = self.mac_config.get('share_name', 'Insta360')
    
    def is_mounted(self) -> bool:
        """
        マウントされているかチェック
        
        Returns:
            bool: マウントされている場合True
        """
        try:
            # mountコマンドでマウント状態を確認
            result = subprocess.run(
                ['mount'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.warning(f"mountコマンドの実行に失敗しました: {result.stderr}")
                return False
            
            # マウントポイントがmountコマンドの出力に含まれているか確認
            mount_output = result.stdout
            mount_point_str = str(self.mount_point)
            
            # マウントポイントが含まれているか確認
            for line in mount_output.split('\n'):
                if mount_point_str in line and 'cifs' in line:
                    logger.debug(f"マウントが確認されました: {line.strip()}")
                    return True
            
            return False
            
        except subprocess.TimeoutExpired:
            logger.error("mountコマンドの実行がタイムアウトしました")
            return False
        except Exception as e:
            logger.error(f"マウント状態の確認中にエラーが発生しました: {e}")
            return False
    
    def check_mount_point_exists(self) -> bool:
        """
        マウントポイントのディレクトリが存在するかチェック
        
        Returns:
            bool: ディレクトリが存在する場合True
        """
        return self.mount_point.exists() and self.mount_point.is_dir()
    
    def check_mount_accessible(self) -> Tuple[bool, str]:
        """
        マウントポイントがアクセス可能かチェック
        
        Returns:
            Tuple[bool, str]: (アクセス可能か, メッセージ)
        """
        if not self.check_mount_point_exists():
            return False, f"マウントポイントが存在しません: {self.mount_point}"
        
        try:
            # ディレクトリの読み取りを試みる
            list(self.mount_point.iterdir())
            return True, "マウントポイントはアクセス可能です"
        except PermissionError:
            return False, f"マウントポイントへのアクセス権限がありません: {self.mount_point}"
        except Exception as e:
            return False, f"マウントポイントのアクセスチェック中にエラーが発生しました: {e}"
    
    def verify_mount(self) -> Tuple[bool, str]:
        """
        マウントの状態を総合的に確認
        
        Returns:
            Tuple[bool, str]: (正常か, メッセージ)
        """
        # マウント状態を確認
        if not self.is_mounted():
            return False, f"マウントされていません: {self.mount_point}"
        
        # アクセス可能性を確認
        accessible, message = self.check_mount_accessible()
        if not accessible:
            return False, message
        
        return True, "マウントは正常に動作しています"
    
    def get_mount_info(self) -> Optional[Dict[str, str]]:
        """
        マウント情報を取得
        
        Returns:
            Optional[Dict[str, str]]: マウント情報（マウントされていない場合はNone）
        """
        try:
            result = subprocess.run(
                ['mount'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            mount_point_str = str(self.mount_point)
            for line in result.stdout.split('\n'):
                if mount_point_str in line and 'cifs' in line:
                    # マウント情報を解析
                    parts = line.split()
                    if len(parts) >= 3:
                        return {
                            'source': parts[0],
                            'mount_point': parts[2],
                            'type': parts[4] if len(parts) > 4 else 'unknown',
                            'options': ' '.join(parts[5:]) if len(parts) > 5 else ''
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"マウント情報の取得中にエラーが発生しました: {e}")
            return None
    
    def remount(self) -> Tuple[bool, str]:
        """
        マウントを再実行（マウントされていない場合のみ）
        
        Returns:
            Tuple[bool, str]: (成功したか, メッセージ)
        """
        # 既にマウントされている場合は成功として返す
        if self.is_mounted():
            logger.debug(f"マウントは既に有効です: {self.mount_point}")
            return True, "マウントは既に有効です"
        
        # マウントポイントのディレクトリが存在しない場合は作成
        if not self.mount_point.exists():
            try:
                self.mount_point.mkdir(parents=True, exist_ok=True)
                logger.info(f"マウントポイントを作成しました: {self.mount_point}")
            except Exception as e:
                error_msg = f"マウントポイントの作成に失敗しました: {e}"
                logger.error(error_msg)
                return False, error_msg
        
        # マウントコマンドを構築
        mount_source = f"//{self.mac_ip}/{self.mac_share}"
        
        # マウントオプションを構築
        mount_options = [
            f"username={self.mac_username}",
            "uid=1000",
            "gid=1000",
            "iocharset=utf8",
            "file_mode=0755",
            "dir_mode=0755"
        ]
        
        if self.mac_password:
            mount_options.append(f"password={self.mac_password}")
        
        # mountコマンドを実行
        try:
            mount_cmd = [
                'mount',
                '-t', 'cifs',
                mount_source,
                str(self.mount_point),
                '-o', ','.join(mount_options)
            ]
            
            logger.info(f"マウントを実行します: {' '.join(mount_cmd)}")
            result = subprocess.run(
                mount_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"マウントが成功しました: {self.mount_point}")
                return True, "マウントが成功しました"
            else:
                error_msg = f"マウントに失敗しました: {result.stderr}"
                logger.error(error_msg)
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "マウントコマンドの実行がタイムアウトしました"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"マウント実行中にエラーが発生しました: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def ensure_mounted(self) -> Tuple[bool, str]:
        """
        マウントされていることを保証（マウントされていない場合は再マウント）
        
        Returns:
            Tuple[bool, str]: (成功したか, メッセージ)
        """
        # マウント状態を確認
        if self.is_mounted():
            # アクセス可能性も確認
            accessible, access_message = self.check_mount_accessible()
            if accessible:
                return True, "マウントは正常に動作しています"
            else:
                logger.warning(f"マウントはされていますが、アクセスできません: {access_message}")
                # 一旦アンマウントして再マウントを試みる
                self._unmount()
        
        # マウントされていない場合は再マウント
        return self.remount()
    
    def _unmount(self) -> bool:
        """
        マウントを解除（内部メソッド）
        
        Returns:
            bool: 成功したか
        """
        try:
            result = subprocess.run(
                ['umount', str(self.mount_point)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"マウントを解除しました: {self.mount_point}")
                return True
            else:
                logger.warning(f"マウント解除に失敗しました: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"マウント解除中にエラーが発生しました: {e}")
            return False


def check_mount_status(mount_point: str, mac_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    マウント状態をチェックして結果を返す
    
    Args:
        mount_point: マウントポイントのパス
        mac_config: Mac接続設定
    
    Returns:
        Dict[str, Any]: マウント状態の詳細情報
    """
    manager = MountManager(mount_point, mac_config)
    
    is_mounted = manager.is_mounted()
    exists = manager.check_mount_point_exists()
    accessible, access_message = manager.check_mount_accessible()
    mount_info = manager.get_mount_info()
    
    return {
        'is_mounted': is_mounted,
        'mount_point_exists': exists,
        'is_accessible': accessible,
        'access_message': access_message,
        'mount_info': mount_info,
        'status': 'ok' if (is_mounted and accessible) else 'error'
    }

