#!/bin/bash
# Insta360自動同期 - デバッグスクリプト

echo "=== 1. マウント状態の確認 ==="
mount | grep mac-share || echo "❌ マウントされていません"

echo ""
echo "=== 2. NAS側のマウントポイント確認 ==="
ls -la /mnt/mac-share | head -20

echo ""
echo "=== 3. コンテナ内のソースパス確認 ==="
docker exec insta360-auto-sync ls -la /source | head -20

echo ""
echo "=== 4. ファイル検索テスト ==="
docker exec insta360-auto-sync find /source -type f | head -20

echo ""
echo "=== 5. ファイルパターンテスト ==="
echo "検索対象ファイルパターン:"
docker exec insta360-auto-sync python -c "
import sys
sys.path.append('/app')
from utils.config_utils import ConfigManager
config_manager = ConfigManager('/app/config')
app_config = config_manager.load_config('app')
patterns = app_config.get('sync', {}).get('file_patterns', [])
print('\\n'.join(patterns))
"

echo ""
echo "=== 6. パターンマッチングテスト ==="
docker exec insta360-auto-sync python -c "
import os
import fnmatch
from pathlib import Path

source_path = Path('/source')
patterns = ['VID_*.mp4', '*.insv', '*.insp', '*.jpg', '*.dng', '*.raw']

if source_path.exists():
    print(f'ソースパス存在: {source_path}')
    print(f'ファイル一覧:')
    for root, dirs, files in os.walk(source_path):
        for filename in files:
            print(f'  {Path(root) / filename}')
            for pattern in patterns:
                if fnmatch.fnmatch(filename, pattern):
                    print(f'    ✅ マッチ: {pattern}')
                    break
        break  # 最初のディレクトリのみ
else:
    print(f'❌ ソースパスが存在しません: {source_path}')
"











