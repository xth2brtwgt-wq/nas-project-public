# 環境設定とデプロイメント

## 環境について
- NAS環境は実働環境です。

## 環境設定詳細
- NAS環境: 192.168.68.110 (AdminUser)
- プロジェクト配置: /home/AdminUser/nas-project/
- Docker使用、各プロジェクト独立コンテナ

### SSH設定
- ポート: 23456
- 推奨環境変数:
  ```env
  SSH_HOST=192.168.68.110
  SSH_USER=AdminUser
  SSH_PORT=23456
  ```

## 必須ルール
- チャットでは必ず日本語で回答してください。
- 環境変数は.envに記述してください。
- **実行時には.envのみを使用してください（.env.restoreは使用しません）**
- .env.restoreはGit管理から除外してください。
- .env.restoreはGitからPullした時に更新されないようにしてください。

## デプロイメントルール
- **絶対ルール**: すべての修正はローカル → NASデプロイの順序
- **禁止事項**: NAS上での直接修正は絶対禁止
- **重要な注意事項**: 
  - **コード変更時**: `docker compose up -d --build`でイメージ再ビルドが必要
  - **環境変数のみ変更時**: `docker compose restart`でOK
  - **理由**: Dockerfileで`COPY . .`によりコードがイメージに組み込まれているため、`restart`だけでは最新コードが反映されない
- **環境ファイル戦略**: 
  - **`.env`**: 実際に稼働時に使うファイル（**Git管理外**、実際のAPIキー・パスワードを含むためセキュリティ上重要）
  - **`.env.restore`**: GitPull時などで.envファイルが初期化された時用のバックアップファイル（Git管理外、実行時には使用しない）
  - **`env.example`**: ドキュメント用テンプレート（Gitで管理、サンプル値のみ）

## 環境ファイル運用フロー

### 初回セットアップ
1. **`env.example`から`.env`を作成**
   ```bash
   cp env.example .env
   ```

2. **`.env`を編集（実際のAPIキー・パスワードを設定）**
   ```bash
   nano .env
   # APIキー、パスワードなどを設定
   ```

3. **`.env`から`.env.restore`を作成（バックアップ）**
   ```bash
   cp .env .env.restore
   ```

### トラブル時の復元
`.env`が初期化された場合、`.env.restore`から復元：
```bash
cp .env.restore .env
docker compose restart  # 環境変数の変更のみなのでrestartでOK
```

## 重要な注意事項
⚠️ **`.env.restore`は実行時に使用されません**
- `docker-compose.yml`の`env_file`には`.env`のみを指定してください
- `.env.restore`は`.env`が初期化された際の復元用バックアップとして保存しておくファイルです
- 実行環境は`.env`のみを読み込みます
- **運用フロー**: `env.example` → `.env` → `.env.restore`（バックアップ作成）→ トラブル時は `.env.restore` → `.env`（復元）

詳細は [DEPLOYMENT_RULES.md](../../DEPLOYMENT_RULES.md) を参照してください。

## データディレクトリ管理ルール
- **統合データディレクトリ**: `/home/AdminUser/nas-project-data/` 配下で一元管理
- **新規プロジェクトデータ**: 必ず `/home/AdminUser/nas-project-data/{プロジェクト名}/` 配下に作成
- **禁止事項**: `/home/AdminUser/{プロジェクト名}-data/` 形式での個別ディレクトリ作成は禁止
- **命名規則**: プロジェクト名は小文字、ハイフン区切り（例: `new-project-name`）
- **権限設定**: 作成時は適切な権限（755）と所有者（AdminUser:admin）を設定
- **バックアップ**: データ移動時は必ずタイムスタンプ付きバックアップを作成
- **データ分離**: ソースコードとデータを完全に分離し、データは統合ディレクトリで管理

詳細は [DATA_MANAGEMENT_RULES.md](../../DATA_MANAGEMENT_RULES.md) を参照してください。

