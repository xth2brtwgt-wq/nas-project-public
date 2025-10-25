# NAS環境デプロイ仕様

## 📋 概要

NAS環境でのDockerアプリケーションデプロイの共通仕様です。
全プロジェクトで統一されたデプロイ方法を提供します。

## 📁 ファイル構成

```
docs/deployment/
├── README.md                           # このファイル
├── NAS_DEPLOYMENT_SPECIFICATION.md    # 詳細仕様書
├── deploy-nas-template.sh             # deploy-nas.shテンプレート
├── docker-compose-template.yml         # docker-compose.ymlテンプレート
├── setup-nas-project.sh               # 新規プロジェクト作成スクリプト
└── update-existing-projects.sh         # 既存プロジェクト更新スクリプト
```

## 🚀 使用方法

### 1. 新規プロジェクトの作成

```bash
# セットアップスクリプトを実行
./docs/deployment/setup-nas-project.sh <プロジェクト名> <ポート番号>

# 例
./docs/deployment/setup-nas-project.sh my-app 5006
```

### 2. 既存プロジェクトの更新

```bash
# 既存プロジェクトを新しい仕様に更新
./docs/deployment/update-existing-projects.sh
```

### 3. 手動でのテンプレート適用

#### deploy-nas.shの作成

```bash
# プロジェクトディレクトリに移動
cd /home/YOUR_USERNAME/nas-project/your-project/

# テンプレートをコピー
cp ../../docs/deployment/deploy-nas-template.sh deploy-nas.sh

# プロジェクト名とポート番号を置換
sed -i 's/PROJECT_NAME/your-project/g' deploy-nas.sh
sed -i 's/PORT/5007/g' deploy-nas.sh

# 実行権限を付与
chmod +x deploy-nas.sh
```

#### docker-compose.ymlの作成

```bash
# テンプレートをコピー
cp ../../docs/deployment/docker-compose-template.yml docker-compose.yml

# プロジェクト名とポート番号を置換
sed -i 's/PROJECT_NAME/your-project/g' docker-compose.yml
sed -i 's/EXTERNAL_PORT/5007/g' docker-compose.yml
```

## 📋 標準的なディレクトリ構造

```
/home/YOUR_USERNAME/
├── nas-project/                    # Gitリポジトリのルート
│   ├── project-name/              # プロジェクトディレクトリ
│   │   ├── app.py                 # メインアプリケーション
│   │   ├── docker-compose.yml    # Docker設定
│   │   ├── deploy-nas.sh         # デプロイスクリプト
│   │   ├── env.production        # 本番環境変数
│   │   └── utils/                # ユーティリティ
│   └── other-project/
└── project-name-data/            # データディレクトリ（ボリュームマウント用）
    ├── uploads/
    ├── transcripts/
    ├── templates/
    └── logs/
```

## 🔧 デプロイ手順

### 初回デプロイ

1. **プロジェクトディレクトリに移動**
   ```bash
   cd /home/YOUR_USERNAME/nas-project/project-name/
   ```

2. **環境変数ファイルの設定**
   ```bash
   cp env.example env.production
   # env.productionを編集してAPIキーなどを設定
   ```

3. **デプロイスクリプトの実行**
   ```bash
   ./deploy-nas.sh
   ```

### 日常的なデプロイ

1. **最新コードの取得**
   ```bash
   git pull origin main
   ```

2. **デプロイの実行**
   ```bash
   ./deploy-nas.sh
   ```

### 緊急時の再起動

```bash
docker compose restart
```

## 📊 プロジェクト一覧

| プロジェクト名 | ポート | データディレクトリ | 状態 |
|---------------|--------|-------------------|------|
| meeting-minutes-byc | 5002 | /home/YOUR_USERNAME/meeting-minutes-data/ | ✅ 稼働中 |
| amazon-analytics | 5001 | /home/YOUR_USERNAME/amazon-analytics-data/ | 🔄 更新予定 |
| document-automation | 5003 | /home/YOUR_USERNAME/document-automation-data/ | 🔄 更新予定 |
| insta360-auto-sync | 5004 | /home/YOUR_USERNAME/insta360-auto-sync-data/ | 🔄 更新予定 |
| nas-dashboard | 5005 | /home/YOUR_USERNAME/nas-dashboard-data/ | 🔄 更新予定 |

## 🔍 トラブルシューティング

### よくある問題

1. **環境変数ファイルの初期化**
   - 症状: APIキーが無効
   - 解決: `.env.local`から`.env`にコピー

2. **ディレクトリ構造の混乱**
   - 症状: 間違ったディレクトリでデプロイ
   - 解決: 正しいディレクトリ（`/home/YOUR_USERNAME/nas-project/project-name/`）で実行

3. **ボリュームマウントの問題**
   - 症状: 古いファイルが残る
   - 解決: データディレクトリの更新

### 確認コマンド

```bash
# コンテナの状態確認
docker ps | grep project-name

# ログの確認
docker logs project-name

# 環境変数の確認
docker exec project-name env | grep API_KEY

# ファイルの確認
ls -la /home/YOUR_USERNAME/project-name-data/
```

## 📋 チェックリスト

### デプロイ前

- [ ] 正しいディレクトリにいる
- [ ] `env.production`が設定されている
- [ ] 必要なAPIキーが設定されている
- [ ] ポートが使用されていない

### デプロイ後

- [ ] コンテナが正常に起動している
- [ ] ヘルスチェックが通る
- [ ] ログにエラーがない
- [ ] アプリケーションにアクセスできる

## 🎯 推奨事項

1. **定期的なバックアップ**
   - データディレクトリのバックアップ
   - 環境変数ファイルのバックアップ

2. **監視の設定**
   - ログの監視
   - リソース使用量の監視

3. **セキュリティ**
   - APIキーの適切な管理
   - 定期的なパスワード変更

---

**作成日**: 2025年10月23日
**対象**: 全NAS環境プロジェクト
**更新**: 必要に応じて更新
