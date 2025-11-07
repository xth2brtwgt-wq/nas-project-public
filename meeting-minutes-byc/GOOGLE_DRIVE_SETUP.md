# Google Drive API設定手順

このドキュメントでは、議事録をGoogle Drive（Obsidian Vault）に保存するためのGoogle Drive APIの設定手順を説明します。

## 前提条件

- Googleアカウントを持っていること
- Google Cloud Consoleにアクセスできること

## 手順1: Google Cloud Consoleでプロジェクトを作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 右上のプロジェクト選択ドロップダウンをクリック
3. 「新しいプロジェクト」をクリック
4. プロジェクト名を入力（例: `meeting-minutes-byc`）
5. 「作成」をクリック
6. 作成したプロジェクトを選択

## 手順2: Google Drive APIを有効化

1. 左側のメニューから「APIとサービス」→「ライブラリ」を選択
2. 検索ボックスに「Google Drive API」と入力
3. 「Google Drive API」を選択
4. 「有効にする」をクリック

## 手順3: OAuth 2.0認証情報を作成

1. 左側のメニューから「APIとサービス」→「認証情報」を選択
2. 画面上部の「認証情報を作成」をクリック
3. 「OAuth クライアント ID」を選択

### OAuth同意画面の設定（初回のみ）

OAuth同意画面が設定されていない場合は、先に設定が必要です：

1. 「OAuth同意画面」タブを選択
2. 「外部」を選択（個人利用の場合は「内部」も可）
3. 「作成」をクリック
4. アプリ情報を入力：
   - アプリ名: `Meeting Minutes BYC`（任意）
   - ユーザーサポートメール: 自分のメールアドレス
   - デベロッパーの連絡先情報: 自分のメールアドレス
5. 「保存して次へ」をクリック
6. スコープはデフォルトのまま「保存して次へ」をクリック
7. テストユーザーは後で追加可能なので「保存して次へ」をクリック
8. 概要を確認して「ダッシュボードに戻る」をクリック

### OAuth クライアント IDの作成

1. 「認証情報」タブに戻る
2. 「認証情報を作成」→「OAuth クライアント ID」を選択
3. アプリケーションの種類: 「デスクトップアプリ」を選択
4. 名前: `Meeting Minutes BYC Client`（任意）
5. 「作成」をクリック
6. 認証情報が表示されるので、「JSONをダウンロード」をクリック
7. ダウンロードしたファイルを `credentials.json` にリネーム

## 手順4: Google DriveフォルダIDを取得

1. [Google Drive](https://drive.google.com/)にアクセス
2. Obsidian Vaultとして使用するフォルダを作成（または既存のフォルダを使用）
3. フォルダを開く
4. ブラウザのアドレスバーからURLを確認
   - 例: `https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p`
   - フォルダIDは `/folders/` の後の文字列（`1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p`）

## 手順5: 認証情報ファイルを配置

1. ダウンロードした `credentials.json` をプロジェクトのルートディレクトリに配置
   - 例: `/nas-project/meeting-minutes-byc/credentials.json`
2. ファイルのパーミッションを確認（読み取り可能であること）

## 手順6: 環境変数の設定

`.env.local` ファイル（または `.env` ファイル）に以下を追加：

```bash
# Google Drive Integration (Obsidian Vault用)
GOOGLE_DRIVE_FOLDER_ID=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
GOOGLE_DRIVE_CREDENTIALS_PATH=./credentials.json
GOOGLE_DRIVE_TOKEN_PATH=./token.json
```

**重要**: 
- `GOOGLE_DRIVE_FOLDER_ID` は手順4で取得したフォルダIDに置き換えてください
- `GOOGLE_DRIVE_CREDENTIALS_PATH` は `credentials.json` の実際のパスに合わせてください
- `GOOGLE_DRIVE_TOKEN_PATH` は初回認証後に自動生成されます

## 手順7: 初回認証の実行

1. アプリケーションを起動
2. 議事録をアップロードし、「Google Drive（Obsidian Vault）に保存する」にチェックを入れる
3. 初回実行時、ブラウザが自動的に開き、Googleアカウントでの認証が求められます
4. 認証を完了すると、`token.json` が自動生成されます
5. 以降は自動的に認証されます

### 注意事項

- **初回認証はローカル環境で実行することを推奨**
  - NAS環境で実行する場合、ブラウザが開かない可能性があります
  - その場合は、ローカル環境で一度認証を実行し、生成された `token.json` をNAS環境にコピーしてください

## 手順8: NAS環境へのデプロイ（初回認証後）

1. ローカル環境で生成された `token.json` をNAS環境にコピー
2. `credentials.json` もNAS環境にコピー
3. 環境変数をNAS環境の `.env.local` に設定
4. アプリケーションを再起動

## トラブルシューティング

### 認証エラーが発生する場合

1. `token.json` を削除して再認証を試みる
2. `credentials.json` が正しいパスに配置されているか確認
3. Google Cloud ConsoleでAPIが有効になっているか確認

### フォルダが見つからないエラー

1. `GOOGLE_DRIVE_FOLDER_ID` が正しいか確認
2. フォルダへのアクセス権限があるか確認
3. フォルダが削除されていないか確認

### 書き込み権限エラー

1. OAuth同意画面で適切なスコープが設定されているか確認
2. 認証時に「Google Driveへのアクセス」を許可したか確認

## セキュリティに関する注意事項

- `credentials.json` と `token.json` は機密情報です
- `.gitignore` に追加してGitにコミットしないようにしてください
- これらのファイルは適切に保護してください

## 参考リンク

- [Google Drive API ドキュメント](https://developers.google.com/drive/api)
- [OAuth 2.0 認証フロー](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)



