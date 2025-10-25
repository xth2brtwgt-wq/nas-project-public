# Meeting Minutes BYC - 音声文字起こし・議事録生成アプリケーション

**バージョン**: v1.1.0 (config/version.pyで一元管理)

## 📋 概要

音声ファイルをアップロードして、Gemini AIを使用した自動文字起こしと議事録生成を行うWebアプリケーションです。リアルタイム進捗表示、Notion連携、メール送信機能を搭載しています。

## ✨ 機能

- 🎤 **音声ファイルアップロード**: WAV, MP3, M4A, FLAC, OGG, WEBM対応
- 🤖 **AI文字起こし**: Gemini 2.5 Flashによる高精度な文字起こし
- 📝 **議事録自動生成**: 構造化された議事録の自動作成
- 📊 **リアルタイム進捗表示**: WebSocketによる処理進捗のリアルタイム更新
- 📄 **Notion連携**: 生成された議事録の自動Notion登録
- 📧 **メール送信**: 処理完了通知の自動メール送信
- 💾 **ファイル生成**: Markdown、テキスト形式での結果保存
- 📚 **カスタム辞書機能**: 音声文字起こし精度向上のための辞書管理システム
- 🎨 **美しいUI**: レスポンシブデザインのWebインターフェース

## 🚀 クイックスタート

### 1. 必要な準備

- Python 3.11以上
- Gemini AI API Key ([Google AI Studio](https://makersuite.google.com/app/apikey)で取得)
- Notion API Key (Notion連携を使用する場合)
- SMTP設定 (メール送信を使用する場合)

### 2. 環境設定

```bash
# リポジトリのクローン
git clone <repository-url>
cd meeting-minutes-byc

# 環境変数ファイルの作成
cp env_example.txt .env
# .envファイルを編集してAPI Keyを設定
```

#### 環境変数の設定例

```bash
# 必須設定
GEMINI_API_KEY=your_gemini_api_key_here

# Notion連携（オプション）
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_database_id_here

# メール送信（オプション）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
FROM_EMAIL=your_email@gmail.com

# アプリケーション設定
PORT=5003
FLASK_ENV=development
```

### 3. 開発環境での実行

```bash
# 開発用スクリプトの実行
./run_dev.sh
```

または手動で実行:

```bash
# 仮想環境の作成とアクティベート
python3 -m venv venv
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt

# アプリケーションの起動
python app.py
```

### 4. アクセス

ブラウザで http://localhost:5003 にアクセス

## 🐳 Dockerでの実行

### 開発環境

```bash
# 環境変数の設定
export GEMINI_API_KEY=your_api_key_here

# Docker Composeで起動
docker-compose -f docker-compose.dev.yml up --build
```

### 本番環境

```bash
# 本番用Docker Composeで起動
docker-compose up --build
```

## 📁 プロジェクト構造

```
meeting-minutes-byc/
├── app.py                 # メインアプリケーション（WebSocket対応）
├── requirements.txt       # Python依存関係
├── Dockerfile            # Dockerイメージ定義
├── docker-compose.dev.yml # 開発用Docker Compose
├── run_dev.sh            # 開発用実行スクリプト
├── templates/
│   └── index.html        # メインHTMLテンプレート
├── static/
│   ├── css/
│   │   └── style.css     # スタイルシート
│   └── js/
│       └── app.js        # JavaScript（WebSocket対応）
├── utils/
│   ├── email_sender.py   # メール送信機能
│   ├── notion_client.py  # Notion連携機能
│   ├── markdown_generator.py # ファイル生成機能
│   └── dictionary_manager.py # カスタム辞書管理機能
├── config/
│   ├── version.py        # バージョン情報管理
│   └── custom_dictionary.json # カスタム辞書データ
├── uploads/              # アップロードファイル（一時）
├── transcripts/          # 生成された議事録
└── README.md
```

## 🔧 設定

### 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `GEMINI_API_KEY` | Gemini AI API Key | 必須 |
| `NOTION_API_KEY` | Notion API Key | オプション |
| `NOTION_DATABASE_ID` | NotionデータベースID | オプション |
| `SMTP_SERVER` | SMTPサーバー | オプション |
| `SMTP_PORT` | SMTPポート | `587` |
| `SMTP_USERNAME` | SMTPユーザー名 | オプション |
| `SMTP_PASSWORD` | SMTPパスワード | オプション |
| `FROM_EMAIL` | 送信者メールアドレス | オプション |
| `FLASK_ENV` | Flask環境 | `development` |
| `FLASK_DEBUG` | デバッグモード | `True` |
| `UPLOAD_DIR` | アップロードディレクトリ | `./uploads` |
| `TRANSCRIPT_DIR` | 議事録保存ディレクトリ | `./transcripts` |
| `HOST` | サーバーホスト | `0.0.0.0` |
| `PORT` | サーバーポート | `5003` |

## 📱 使用方法

1. **会議情報入力**: 会議日時、メールアドレス、Notion登録の有無を設定
2. **辞書管理** (オプション): 「📚 辞書管理」ボタンで専門用語や固有名詞を登録
3. **ファイルアップロード**: 音声ファイルをドラッグ&ドロップまたは選択
4. **処理実行**: 「文字起こし・議事録生成」ボタンをクリック
5. **進捗確認**: リアルタイムで処理進捗を確認
6. **結果確認**: 処理完了後、結果画面で詳細を確認
7. **自動処理**: Notion登録とメール送信が自動実行

## 🎯 対応ファイル形式

- **WAV**: 無圧縮音声
- **MP3**: MPEG-1 Audio Layer 3
- **M4A**: MPEG-4 Audio
- **FLAC**: Free Lossless Audio Codec
- **OGG**: Ogg Vorbis
- **WEBM**: WebM Audio

## 🔍 API エンドポイント

- `GET /`: メインページ
- `GET /health`: ヘルスチェック
- `POST /upload`: 音声ファイルアップロードと処理
- `GET /api/email-status`: メール送信状況の取得
- `GET /api/dictionary`: 辞書データの取得
- `GET /api/dictionary/search`: 辞書検索
- `POST /api/dictionary/entry`: 辞書エントリの追加
- `DELETE /api/dictionary/entry`: 辞書エントリの削除
- `GET /transcripts/<filename>`: 議事録ファイルの取得

## 🔌 WebSocket イベント

- `connect`: クライアント接続
- `disconnect`: クライアント切断
- `join_room`: ルーム参加
- `progress_update`: 処理進捗更新
- `email_status_update`: メール送信状況更新

## 🛠️ 開発

### ローカル開発

```bash
# 開発サーバーの起動
python app.py

# テスト実行
python -m pytest tests/
```

### Docker開発

```bash
# 開発用コンテナの起動
docker-compose -f docker-compose.dev.yml up --build

# ログの確認
docker-compose -f docker-compose.dev.yml logs -f
```

## 📊 ログ

アプリケーションのログは以下の形式で出力されます:

```
2024-01-01 12:00:00 - app - INFO - ファイルをアップロードしました: meeting_20240101_120000.wav
2024-01-01 12:00:05 - app - INFO - 処理完了: meeting_20240101_120000.wav
```

## 🚨 トラブルシューティング

### よくある問題

1. **API Keyエラー**
   - Gemini AI API Keyが正しく設定されているか確認
   - API Keyの権限とクォータを確認

2. **ファイルアップロードエラー**
   - ファイル形式が対応しているか確認
   - ファイルサイズが100MB以下か確認

3. **文字起こしエラー**
   - 音声ファイルの品質を確認
   - ネットワーク接続を確認

## 📄 ライセンス

MIT License

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します。

## 📞 サポート

問題が発生した場合は、GitHubのIssuesページで報告してください。
