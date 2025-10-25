#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insta360手動同期スクリプト
スケジューラーを起動せず、1回だけ同期を実行
"""

import sys
sys.path.append('/app')
sys.path.append('/app/utils')

from scripts.sync import Insta360Sync
from utils.file_utils import format_file_size

def main():
    """手動同期を実行"""
    try:
        # 同期を実行
        sync = Insta360Sync()
        result = sync.run_sync()
        
        # 結果を出力
        print(f"同期完了: 成功 {result['success_files']}件, スキップ {result['skipped_files']}件, 失敗 {result['failed_files']}件")
        print(f"総容量: {format_file_size(result['total_size'])}")
        print(f"実行時間: {result['duration_seconds']:.2f}秒")
        
        # 終了コード（失敗があれば1、なければ0）
        return 0 if result['failed_files'] == 0 else 1
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

