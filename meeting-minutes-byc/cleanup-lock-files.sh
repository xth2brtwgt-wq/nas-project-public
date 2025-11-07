#!/bin/bash

# ロックファイルのクリーンアップスクリプト
# 使用方法: ./cleanup-lock-files.sh

echo "🧹 ロックファイルをクリーンアップ中..."
echo ""

# アップロードロックファイルのディレクトリ
UPLOAD_LOCK_DIR="~/nas-project-data/meeting-minutes-byc/transcripts/.upload_locks"

if [ -d "$UPLOAD_LOCK_DIR" ]; then
    echo "📁 アップロードロックファイルの確認:"
    ls -la "$UPLOAD_LOCK_DIR" 2>/dev/null | head -20
    
    echo ""
    echo "🗑️  60秒以上経過したロックファイルを削除中..."
    find "$UPLOAD_LOCK_DIR" -name "*.lock" -type f -mmin +1 -delete 2>/dev/null
    
    echo "✅ クリーンアップ完了"
    echo ""
    echo "📁 残存ロックファイル:"
    ls -la "$UPLOAD_LOCK_DIR" 2>/dev/null | head -10
else
    echo "⚠️  ロックファイルディレクトリが見つかりません: $UPLOAD_LOCK_DIR"
fi

echo ""
echo "🎉 クリーンアップ完了！"









