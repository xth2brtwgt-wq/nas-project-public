import os
import shutil
import glob
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FileManager:
    """ファイル管理クラス"""
    
    def __init__(self, source_path: str, destination_path: str, file_patterns: List[str]):
        self.source_path = Path(source_path)
        self.destination_path = Path(destination_path)
        self.file_patterns = file_patterns
        
        # 転送先ディレクトリを作成
        self.destination_path.mkdir(parents=True, exist_ok=True)
    
    def find_insta360_files(self) -> List[Dict[str, Any]]:
        """Insta360ファイルを検索"""
        files = []
        
        if not self.source_path.exists():
            logger.warning(f"ソースパスが存在しません: {self.source_path}")
            return files
        
        try:
            # ソースパス配下の全ファイル数を確認（デバッグ用）
            total_files = 0
            matched_files = []
            unmatched_files = []
            
            # ソースパス配下を再帰的に検索
            for root, dirs, filenames in os.walk(self.source_path):
                for filename in filenames:
                    total_files += 1
                    file_path = Path(root) / filename
                    
                    if self._matches_pattern(filename):
                        matched_files.append(str(file_path))
                        file_info = self._get_file_info(file_path)
                        if file_info:
                            files.append(file_info)
                    else:
                        unmatched_files.append(str(file_path))
            
            # デバッグ情報を出力
            logger.info(f"ソースパス: {self.source_path}")
            logger.info(f"検索対象ファイルパターン: {self.file_patterns}")
            logger.info(f"総ファイル数: {total_files}")
            logger.info(f"パターン一致ファイル数: {len(files)}")
            
            if total_files > 0 and len(files) == 0:
                logger.warning(f"ファイルが {total_files} 件見つかりましたが、パターンに一致するファイルがありませんでした")
                logger.info(f"最初の10件のファイル名: {[Path(f).name for f in unmatched_files[:10]]}")
            elif total_files == 0:
                logger.warning(f"ソースパス内にファイルが見つかりませんでした: {self.source_path}")
                logger.info("Mac側の共有フォルダにファイルが存在するか、マウントが正しく機能しているか確認してください")
            
            logger.info(f"Insta360ファイルを {len(files)} 件発見しました")
            return files
            
        except Exception as e:
            logger.error(f"ファイル検索エラー: {e}", exc_info=True)
            return []
    
    def _matches_pattern(self, filename: str) -> bool:
        """ファイル名がパターンにマッチするかチェック"""
        filename_lower = filename.lower()
        for pattern in self.file_patterns:
            # パターンマッチング（大文字小文字を区別しない）
            if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(filename_lower, pattern.lower()):
                return True
        return False
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """ファイル情報を取得"""
        try:
            stat = file_path.stat()
            return {
                'filename': file_path.name,
                'path': str(file_path),
                'size': stat.st_size,
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'relative_path': str(file_path.relative_to(self.source_path))
            }
        except Exception as e:
            logger.error(f"ファイル情報取得エラー {file_path}: {e}")
            return None
    
    def _files_are_identical(self, source_file: Path, dest_file: Path) -> bool:
        """ソースファイルと転送先ファイルが同一かチェック（サイズと最終更新日時）"""
        if not dest_file.exists():
            return False
        
        try:
            source_stat = source_file.stat()
            dest_stat = dest_file.stat()
            
            # サイズと最終更新日時が同じであれば同一とみなす
            return (source_stat.st_size == dest_stat.st_size and
                    source_stat.st_mtime == dest_stat.st_mtime)
        except Exception as e:
            logger.warning(f"ファイル同一性チェックエラー {source_file} vs {dest_file}: {e}")
            return False

    def copy_file(self, file_info: Dict[str, Any], skip_existing: bool = True) -> Tuple[bool, str]:
        """ファイルをコピー"""
        try:
            source_file = Path(file_info['path'])
            dest_file = self.destination_path / file_info['relative_path']
            
            # 転送先ディレクトリを作成
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 転送先に同じファイルが存在し、かつ同一であればスキップ
            if skip_existing and self._files_are_identical(source_file, dest_file):
                logger.info(f"ファイルをスキップ（転送先に同一ファイルが存在）: {file_info['filename']}")
                return True, "スキップ済み"
            
            # ファイルをコピー
            shutil.copy2(source_file, dest_file)
            
            # コピー完了を検証
            if self._verify_copy(source_file, dest_file):
                logger.info(f"ファイルコピー成功: {file_info['filename']}")
                return True, "コピー成功"
            else:
                logger.error(f"ファイルコピー検証失敗: {file_info['filename']}")
                return False, "コピー検証失敗"
                
        except Exception as e:
            logger.error(f"ファイルコピーエラー {file_info['filename']}: {e}")
            return False, str(e)
    
    def _verify_copy(self, source_file: Path, dest_file: Path) -> bool:
        """コピーの検証（ファイルサイズ比較）"""
        try:
            source_size = source_file.stat().st_size
            dest_size = dest_file.stat().st_size
            return source_size == dest_size
        except Exception as e:
            logger.error(f"コピー検証エラー: {e}")
            return False
    
    def delete_source_file(self, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """ソースファイルを削除"""
        try:
            source_file = Path(file_info['path'])
            source_file.unlink()
            logger.info(f"ソースファイル削除成功: {file_info['filename']}")
            return True, "削除成功"
        except Exception as e:
            logger.error(f"ソースファイル削除エラー {file_info['filename']}: {e}")
            return False, str(e)
    
    def delete_empty_directories(self, file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """ファイル削除後に空のディレクトリを削除"""
        try:
            source_file = Path(file_info['path'])
            parent_dir = source_file.parent
            
            # ソースパスより上の階層は削除しない
            if parent_dir == self.source_path:
                return True, "ルートディレクトリのため削除スキップ"
            
            # 親ディレクトリが空かチェック
            if parent_dir.exists() and not any(parent_dir.iterdir()):
                parent_dir.rmdir()
                logger.info(f"空ディレクトリ削除成功: {parent_dir}")
                
                # さらに上位のディレクトリもチェック（再帰的）
                self._delete_empty_parent_directories(parent_dir)
                
                return True, "空ディレクトリ削除成功"
            else:
                return True, "ディレクトリに他のファイルが存在するため削除スキップ"
                
        except Exception as e:
            logger.error(f"空ディレクトリ削除エラー: {e}")
            return False, str(e)
    
    def _delete_empty_parent_directories(self, directory: Path):
        """空の親ディレクトリを再帰的に削除"""
        try:
            parent = directory.parent
            
            # ソースパスより上の階層は削除しない
            if parent == self.source_path or not parent.exists():
                return
            
            # 親ディレクトリが空かチェック
            if not any(parent.iterdir()):
                parent.rmdir()
                logger.info(f"空ディレクトリ削除成功: {parent}")
                
                # さらに上位もチェック
                self._delete_empty_parent_directories(parent)
                
        except Exception as e:
            logger.warning(f"親ディレクトリ削除エラー: {e}")
    
    def get_destination_size(self) -> int:
        """転送先の総容量を取得"""
        try:
            total_size = 0
            for root, dirs, files in os.walk(self.destination_path):
                for file in files:
                    file_path = Path(root) / file
                    total_size += file_path.stat().st_size
            return total_size
        except Exception as e:
            logger.error(f"転送先容量取得エラー: {e}")
            return 0
    
    def cleanup_old_logs(self, log_dir: str, max_days: int = 30) -> int:
        """古いログファイルを削除"""
        try:
            log_path = Path(log_dir)
            if not log_path.exists():
                return 0
            
            deleted_count = 0
            cutoff_time = datetime.now().timestamp() - (max_days * 24 * 60 * 60)
            
            for log_file in log_path.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    deleted_count += 1
                    logger.info(f"古いログファイルを削除: {log_file.name}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"ログクリーンアップエラー: {e}")
            return 0

def format_file_size(size_bytes: int) -> str:
    """ファイルサイズを人間が読みやすい形式に変換"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def get_file_extension(filename: str) -> str:
    """ファイル拡張子を取得"""
    return Path(filename).suffix.lower()

def is_insta360_file(filename: str) -> bool:
    """Insta360ファイルかどうかを判定"""
    insta360_extensions = {'.mp4', '.insv', '.insp', '.jpg', '.dng', '.raw'}
    return get_file_extension(filename) in insta360_extensions