# YouTube to Notion Summarizer

**YouTube動画要約・Notion自動投稿システム**

YouTube動画のURLを入力するだけで、自動的に音声を文字起こしし、AI要約を生成してNotionデータベースに保存するWebアプリケーション。

## 🎯 概要

- **バージョン**: v1.0.0
- **目的**: YouTube動画の内容を5分以内で要約・保存
- **対象**: 技術系YouTube動画、学習コンテンツ、ビジネス動画
- **特徴**: 既存システム（meeting-minutes-byc）の資産を最大限活用

## ✨ 主要機能

### 必須機能（Phase 1 - MVP）
- ✅ **YouTube URL入力**: 動画URLの入力・検証
- ✅ **動画情報取得**: タイトル、チャンネル、再生時間、サムネイル
- ✅ **音声抽出**: yt-dlpによる高品質音声抽出
- ✅ **AI文字起こし**: Gemini 2.5 Flashによる高精度文字起こし
- ✅ **AI要約生成**: 構造化された要約の自動作成
- ✅ **Notion自動投稿**: 要約の自動Notion保存
- ✅ **リアルタイム進捗**: WebSocketによる処理進捗表示
- ✅ **結果表示**: 要約・文字起こしの表示・ダウンロード

### オプション機能（Phase 2 - 拡張）
- 🔜 **バッチ処理**: 複数動画の一括処理
- 🔜 **検索機能**: 過去処理動画の検索・フィルタ
- 🔜 **ベクトル検索**: Qdrant連携による意味的検索
- 🔜 **スケジュール実行**: チャンネル新着動画の自動処理

## 🛠️ 技術スタック

### バックエンド
- **言語**: Python 3.11+
- **フレームワーク**: Flask 3.0+
- **WebSocket**: Flask-SocketIO
- **非同期処理**: Threading

### 外部API
- **YouTube音声抽出**: yt-dlp
- **文字起こし**: Google Gemini 2.5 Flash API
- **AI要約**: Google Gemini / Anthropic Claude
- **Notion連携**: Notion API

### フロントエンド
- **HTML5/CSS3/JavaScript**
- **UIフレームワーク**: Bootstrap 5
- **WebSocket**: Socket.IO Client

### インフラ
- **実行環境**: Docker
- **OS**: Debian/Ubuntu
- **Webサーバー**: Flask内蔵サーバー（開発）/ Gunicorn（本番）

## 🚀 クイックスタート

### 1. 前提条件

- Docker & Docker Compose
- Gemini API Key ([Google AI Studio](https://makersuite.google.com/app/apikey)で取得)
- Notion API Key (Notion連携を使用する場合)

### 2. 環境設定

```bash
# プロジェクトのクローン
git clone <repository-url>
cd youtube-to-notion

# 環境変数ファイルの作成
cp env.example .env.restore
nano .env.restore  # APIキーを設定
```

### 3. デプロイ

```bash
# デプロイスクリプトの実行
./deploy.sh
```

### 4. アクセス

- **Web UI**: http://localhost:8110
- **ヘルスチェック**: http://localhost:8110/health

## 📋 環境変数設定

### 必須設定

```bash
# Gemini API設定（必須）
GEMINI_API_KEY=your_gemini_api_key_here

# アプリケーション設定
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

### オプション設定

```bash
# Notion連携（オプション）
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here

# 処理設定
MAX_VIDEO_DURATION=7200  # 最大動画時間（秒）
AUDIO_QUALITY=128        # 音声品質
SUMMARY_LENGTH=medium    # 要約の長さ
```

## 🏗️ システムアーキテクチャ

```
┌─────────────────────────────────────────────────────┐
│                  ユーザー（ブラウザ）                  │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/WebSocket
                     ↓
┌─────────────────────────────────────────────────────┐
│              Flask Webアプリケーション                 │
│  ┌─────────────────────────────────────────────┐   │
│  │  Web UI Layer (templates/static)            │   │
│  └──────────────────┬──────────────────────────┘   │
│                     ↓                               │
│  ┌─────────────────────────────────────────────┐   │
│  │  API Layer (app.py)                         │   │
│  │  - /youtube (POST): YouTube URL処理          │   │
│  │  - /health (GET): ヘルスチェック             │   │
│  │  - /results/<id> (GET): 結果取得            │   │
│  └──────────────────┬──────────────────────────┘   │
│                     ↓                               │
│  ┌─────────────────────────────────────────────┐   │
│  │  Business Logic Layer (services/)           │   │
│  │  - youtube_downloader.py: 音声抽出          │   │
│  │  - video_info_service.py: 動画情報取得      │   │
│  │  - summarization_service.py: 要約生成        │   │
│  │  - notion_client.py: Notion連携            │   │
│  └──────────────────┬──────────────────────────┘   │
│                     ↓                               │
│  ┌─────────────────────────────────────────────┐   │
│  │  Utility Layer (utils/)                     │   │
│  │  - markdown_generator.py: ファイル生成      │   │
│  │  - logger.py: ロギング                      │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
┌──────────────────┐   ┌──────────────────┐
│  外部API         │   │  ローカルストレージ │
│  - Gemini API    │   │  - /uploads      │
│  - Notion API    │   │  - /outputs      │
│  - YouTube       │   │  - /logs         │
└──────────────────┘   └──────────────────┘
```

## 📊 データフロー

```
1. URL入力
   ↓
2. 動画情報取得 (yt-dlp)
   ↓
3. 音声ダウンロード (yt-dlp)
   ↓ /uploads/youtube_<id>.mp3
4. 文字起こし (Gemini API)
   ↓ テキストデータ
5. AI要約生成 (Gemini API)
   ↓ 構造化要約
6. Notion投稿 (Notion API)
   ↓ NotionページURL
7. ファイル保存 (/outputs)
   ↓
8. 一時ファイル削除 (/uploads)
   ↓
9. 結果表示
```

## 🔧 管理コマンド

### Docker管理

```bash
# ログ確認
docker logs -f youtube-to-notion

# コンテナ停止
docker compose down

# コンテナ再起動
docker compose restart

# データ確認
ls -la data/
```

### データ管理

```bash
# 一時ファイルのクリーンアップ
docker exec youtube-to-notion find /app/data/uploads -type f -mtime +1 -delete

# ログローテーション
docker exec youtube-to-notion find /app/logs -name "*.log" -mtime +7 -delete
```

## 📈 パフォーマンス要件

- **処理時間**: 10分動画で2分以内（目標）
- **同時処理数**: 最大3リクエスト
- **レスポンスタイム**: 画面遷移3秒以内
- **稼働率**: 95%以上

## 🔒 セキュリティ要件

- **APIキー管理**: 環境変数による安全な管理
- **一時ファイル**: 処理完了後の自動削除
- **アクセス制御**: ローカルネットワークのみ（Phase 1）
- **ログ管理**: 詳細な処理ログの記録

## 📚 既存システムとの連携

### 流用コンポーネント
- **meeting-minutes-byc**: Gemini文字起こし、Notion連携、WebSocket進捗表示
- **document-automation**: AI要約・分類機能
- **環境変数管理戦略**: 統一された設定管理

### 独立運用
- 既存システムとは完全に独立
- 独自のポート（8110）で運用
- 専用のデータディレクトリ

## 🐛 トラブルシューティング

### よくある問題

1. **Gemini APIエラー**
   ```bash
   # APIキーの確認
   echo $GEMINI_API_KEY
   ```

2. **Notion連携エラー**
   ```bash
   # Notion設定の確認
   curl -H "Authorization: Bearer $NOTION_API_KEY" \
        "https://api.notion.com/v1/databases/$NOTION_DATABASE_ID"
   ```

3. **音声抽出エラー**
   ```bash
   # yt-dlpの動作確認
   docker exec youtube-to-notion yt-dlp --version
   ```

### ログ確認

```bash
# アプリケーションログ
docker logs youtube-to-notion

# 詳細ログ
docker exec youtube-to-notion tail -f /app/logs/app.log
```

## 📝 ライセンス

このプロジェクトは既存システム（meeting-minutes-byc）の資産を活用して構築されています。

## 🤝 貢献

バグ報告や機能要望は、既存のプロジェクト管理システムを通じてお知らせください。

---

**YouTube to Notion Summarizer v1.0.0**  
*YouTube動画を効率的に学習ログとして管理*
