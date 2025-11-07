# .envファイル保護ガイド

## 問題の原因

`.env`ファイルが高頻度で消える主な原因：

1. **デプロイスクリプトで`git pull`を実行**
   - デプロイスクリプトの最初に`git pull origin main`を実行
   - `.env`がGit管理されていなくても、`git pull`の後に`.env`が存在しない場合、`env.example`から作成される

2. **`.env`がGit管理されている可能性**
   - 過去に`.env`がコミットされていた場合、履歴に残っている可能性
   - `.gitignore`で除外されていても、履歴から復元される可能性

3. **`deploy-env-to-nas.sh`がローカルの`.env`をNASにコピー**
   - ローカルの`.env`が空または古い場合、NASの`.env`が上書きされる

## 解決策

### デプロイスクリプトの修正

すべてのデプロイスクリプトで、`git pull`の**前後**に`.env`を保護する処理を追加：

```bash
# 0. .envファイルの保護（git pull前にバックアップ）
echo "🔒 .envファイルを保護中..."
if [ -f .env ]; then
    # .envが存在する場合、.env.restoreにバックアップ
    if [ ! -f .env.restore ] || [ .env -nt .env.restore ]; then
        cp .env .env.restore
        echo "✅ .envを.env.restoreにバックアップしました"
    fi
fi

# 1. 最新コードを取得
echo "📥 最新コードを取得中..."
git pull origin main

# 1.5. .envファイルの復元・確認（git pull後に復元）
echo "🔧 環境変数ファイルを確認中..."
if [ ! -f .env ]; then
    echo "⚠️  .envファイルが見つかりません"
    if [ -f .env.restore ]; then
        echo "📋 .env.restoreから復元します..."
        cp .env.restore .env
        echo "✅ .envを復元しました"
    elif [ -f env.example ]; then
        echo "📋 env.exampleから作成します..."
        cp env.example .env
        echo "⚠️  .envファイルを編集してAPIキーを設定してください"
    fi
fi
```

## 修正済みデプロイスクリプト

以下のデプロイスクリプトは修正済み：

- ✅ `youtube-to-notion/deploy.sh`
- ✅ `meeting-minutes-byc/deploy.sh`
- ✅ `nas-dashboard/deploy.sh`

## 今後の対応

新しいデプロイスクリプトを作成する際は、必ず上記の`.env`保護処理を含めてください。

## 注意事項

- `.env`は`.gitignore`で除外されているため、Git管理されていません
- `.env.restore`も`.gitignore`で除外されているため、Git管理されていません
- `env.example`はGit管理されているため、テンプレートとして使用できます

