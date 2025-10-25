#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube to Notion - ファイルクリーンアップユーティリティ
音声ファイルの定期削除・移動機能
"""

import os
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

class FileCleanupManager:
    """ファイルクリーンアップ管理クラス"""
    
    def __init__(self, 
                 upload_dir: str,
                 archive_dir: Optional[str] = None,
                 max_age_hours: int = 24,
                 max_files: int = 10):
        """
        初期化
        
        Args:
            upload_dir: アップロードディレクトリ
            archive_dir: アーカイブディレクトリ（Noneの場合は削除）
            max_age_hours: 最大保持時間（時間）
            max_files: 最大ファイル数
        """
        self.upload_dir = Path(upload_dir)
        self.archive_dir = Path(archive_dir) if archive_dir else None
        self.max_age_hours = max_age_hours
        self.max_files = max_files
        
        # ディレクトリ作成
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        if self.archive_dir:
            self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def cleanup_audio_files(self, dry_run: bool = False) -> dict:
        """
        音声ファイルのクリーンアップ実行
        
        Args:
            dry_run: ドライランモード（実際には削除しない）
            
        Returns:
            クリーンアップ結果の辞書
        """
        result = {
            'total_files': 0,
            'deleted_files': 0,
            'archived_files': 0,
            'skipped_files': 0,
            'freed_space': 0,
            'errors': []
        }
        
        try:
            # 音声ファイルを取得
            audio_files = self._get_audio_files()
            result['total_files'] = len(audio_files)
            
            if not audio_files:
                logger.info("クリーンアップ対象の音声ファイルが見つかりません")
                return result
            
            # ファイルをソート（古い順）
            audio_files.sort(key=lambda x: x.stat().st_mtime)
            
            # 削除・アーカイブ対象を決定
            files_to_process = self._select_files_for_cleanup(audio_files)
            
            for file_path in files_to_process:
                try:
                    file_size = file_path.stat().st_size
                    
                    if dry_run:
                        logger.info(f"[DRY RUN] 処理予定: {file_path.name} ({file_size} bytes)")
                        result['freed_space'] += file_size
                        continue
                    
                    if self.archive_dir:
                        # アーカイブディレクトリに移動
                        archive_path = self.archive_dir / file_path.name
                        shutil.move(str(file_path), str(archive_path))
                        result['archived_files'] += 1
                        logger.info(f"アーカイブ: {file_path.name} -> {archive_path}")
                    else:
                        # 削除
                        file_path.unlink()
                        result['deleted_files'] += 1
                        logger.info(f"削除: {file_path.name}")
                    
                    result['freed_space'] += file_size
                    
                except Exception as e:
                    error_msg = f"ファイル処理エラー {file_path.name}: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    result['skipped_files'] += 1
            
            # 結果ログ
            if not dry_run:
                logger.info(f"クリーンアップ完了: 削除={result['deleted_files']}, "
                           f"アーカイブ={result['archived_files']}, "
                           f"スキップ={result['skipped_files']}, "
                           f"解放容量={self._format_size(result['freed_space'])}")
            
        except Exception as e:
            error_msg = f"クリーンアップ処理エラー: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _get_audio_files(self) -> List[Path]:
        """音声ファイル一覧を取得"""
        audio_extensions = {'.mp3', '.wav', '.webm', '.m4a', '.ogg'}
        audio_files = []
        
        for file_path in self.upload_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
                audio_files.append(file_path)
        
        return audio_files
    
    def _select_files_for_cleanup(self, audio_files: List[Path]) -> List[Path]:
        """クリーンアップ対象ファイルを選択"""
        files_to_process = []
        current_time = datetime.now()
        
        for file_path in audio_files:
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            age_hours = (current_time - file_mtime).total_seconds() / 3600
            
            # 年齢ベースの削除
            if age_hours > self.max_age_hours:
                files_to_process.append(file_path)
                continue
            
            # ファイル数ベースの削除（古い順）
            if len(files_to_process) + len([f for f in audio_files if f not in files_to_process]) > self.max_files:
                files_to_process.append(file_path)
        
        return files_to_process
    
    def _format_size(self, size_bytes: int) -> str:
        """バイト数を人間が読みやすい形式に変換"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def get_cleanup_stats(self) -> dict:
        """クリーンアップ統計情報を取得"""
        audio_files = self._get_audio_files()
        total_size = sum(f.stat().st_size for f in audio_files)
        
        return {
            'total_files': len(audio_files),
            'total_size': total_size,
            'total_size_formatted': self._format_size(total_size),
            'oldest_file': min((f.stat().st_mtime for f in audio_files), default=None),
            'newest_file': max((f.stat().st_mtime for f in audio_files), default=None)
        }


def cleanup_youtube_audio_files(upload_dir: str, 
                               archive_dir: Optional[str] = None,
                               max_age_hours: int = 24,
                               max_files: int = 10,
                               dry_run: bool = False) -> dict:
    """
    YouTube音声ファイルのクリーンアップ実行（便利関数）
    
    Args:
        upload_dir: アップロードディレクトリ
        archive_dir: アーカイブディレクトリ（Noneの場合は削除）
        max_age_hours: 最大保持時間（時間）
        max_files: 最大ファイル数
        dry_run: ドライランモード
        
    Returns:
        クリーンアップ結果
    """
    cleanup_manager = FileCleanupManager(
        upload_dir=upload_dir,
        archive_dir=archive_dir,
        max_age_hours=max_age_hours,
        max_files=max_files
    )
    
    return cleanup_manager.cleanup_audio_files(dry_run=dry_run)


if __name__ == "__main__":
    # コマンドライン実行用
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube音声ファイルクリーンアップ')
    parser.add_argument('--upload-dir', required=True, help='アップロードディレクトリ')
    parser.add_argument('--archive-dir', help='アーカイブディレクトリ（指定しない場合は削除）')
    parser.add_argument('--max-age-hours', type=int, default=24, help='最大保持時間（時間）')
    parser.add_argument('--max-files', type=int, default=10, help='最大ファイル数')
    parser.add_argument('--dry-run', action='store_true', help='ドライランモード')
    
    args = parser.parse_args()
    
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # クリーンアップ実行
    result = cleanup_youtube_audio_files(
        upload_dir=args.upload_dir,
        archive_dir=args.archive_dir,
        max_age_hours=args.max_age_hours,
        max_files=args.max_files,
        dry_run=args.dry_run
    )
    
    print(f"クリーンアップ結果: {result}")
