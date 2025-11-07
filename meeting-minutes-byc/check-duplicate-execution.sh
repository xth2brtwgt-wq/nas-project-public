#!/bin/bash

# 重複実行確認スクリプト
# 使用方法: ./check-duplicate-execution.sh

echo "🔍 重複実行のログを確認中..."
echo ""

# 1. 直近のログを確認（/uploadエンドポイントへのアクセス）
echo "📋 1. /uploadエンドポイントへのアクセスログ:"
docker logs meeting-minutes-byc --tail 200 | grep -E "(ファイルをアップロード|Notion登録完了|処理完了)" | tail -20
echo ""

# 2. Notion登録のログを確認
echo "📋 2. Notion登録のログ:"
docker logs meeting-minutes-byc --tail 200 | grep -i "notion" | tail -20
echo ""

# 3. エラーログの確認
echo "📋 3. エラーログ:"
docker logs meeting-minutes-byc --tail 200 | grep -i "error\|exception" | tail -10
echo ""

# 4. リクエストのタイムスタンプを確認
echo "📋 4. リクエストのタイムスタンプ:"
docker logs meeting-minutes-byc --tail 200 | grep -E "POST /upload|GET /upload" | tail -10
echo ""

# 5. ファイル名で重複を確認
echo "📋 5. 最新のファイル処理ログ（重複確認）:"
docker logs meeting-minutes-byc --tail 200 | grep -E "ファイルをアップロード|処理完了" | tail -10 | awk '{print $1, $2, $NF}'
echo ""

echo "🎉 確認完了！"
echo ""
echo "💡 確認ポイント:"
echo "   - 同じファイル名で処理が2回実行されていないか"
echo "   - Notion登録が2回実行されていないか"
echo "   - リクエストのタイムスタンプが近いか（重複実行の可能性）"
echo "   - エラーログがないか"









