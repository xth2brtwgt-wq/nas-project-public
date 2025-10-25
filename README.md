# NAS Project Suite

NAS環境で動作する多機能ツールスイートです。AI技術を活用した文書処理、議事録作成、データ分析、自動同期などの機能を提供します。

## 🚀 プロジェクト概要

このプロジェクトは、NAS（Network Attached Storage）環境で動作する複数のツールを統合したスイートです。各ツールは独立したDockerコンテナとして動作し、相互に連携して包括的なソリューションを提供します。

## 📦 含まれるプロジェクト

### 1. Document Automation
- **機能**: AIを活用した文書処理・分析システム
- **技術**: FastAPI, Gemini AI, OCR, RAG
- **用途**: 文書の自動分類、要約、検索

### 2. Meeting Minutes BYC
- **機能**: AI議事録作成システム
- **技術**: Flask, Gemini AI, Whisper
- **用途**: 音声ファイルから自動で議事録を生成

### 3. Amazon Analytics
- **機能**: Amazon購入データ分析システム
- **技術**: FastAPI, Gemini AI, PostgreSQL
- **用途**: 購入パターン分析、支出最適化

### 4. NAS Dashboard
- **機能**: 統合管理ダッシュボード
- **技術**: Flask, Chart.js
- **用途**: システム監視、レポート生成

### 5. Insta360 Auto Sync
- **機能**: Insta360カメラ自動同期システム
- **技術**: Python, SMB, Email
- **用途**: カメラファイルの自動バックアップ

### 6. YouTube to Notion
- **機能**: YouTube動画要約・Notion連携
- **技術**: Flask, YouTube API, Notion API
- **用途**: 動画コンテンツの自動要約・保存

## 🛠️ 技術スタック

- **Backend**: Python (FastAPI, Flask)
- **Database**: PostgreSQL, Redis
- **AI/ML**: Google Gemini, OpenAI GPT, Whisper
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Infrastructure**: Docker, Docker Compose
- **Storage**: NAS (SMB/CIFS)

## 🚀 クイックスタート

### 前提条件
- Docker & Docker Compose
- NAS環境（推奨: UGreen DXP2800）
- インターネット接続（AI API用）

### セットアップ

1. **リポジトリのクローン**
```bash
git clone https://github.com/your-username/nas-project-public.git
cd nas-project-public
```

2. **環境変数の設定**
各プロジェクトの`env.example`をコピーして`.env`を作成：
```bash
# 例: Document Automation
cd document-automation
cp env.example .env
# .envファイルを編集してAPIキー等を設定
```

3. **Dockerコンテナの起動**
```bash
# 個別プロジェクトの起動
cd document-automation
docker-compose up -d

# または全プロジェクトの起動
./deploy-all.sh
```

## 📋 各プロジェクトの詳細

### Document Automation
- **ポート**: 8001
- **機能**: 文書のOCR、AI分析、RAG検索
- **設定**: Gemini APIキーが必要

### Meeting Minutes BYC
- **ポート**: 5002
- **機能**: 音声から議事録自動生成
- **設定**: Gemini APIキー、Notion API（オプション）

### Amazon Analytics
- **ポート**: 8000
- **機能**: 購入データ分析、レポート生成
- **設定**: Gemini APIキー、Amazon CSVデータ

### NAS Dashboard
- **ポート**: 9001
- **機能**: システム監視、統合ダッシュボード
- **設定**: 各プロジェクトの接続情報

### Insta360 Auto Sync
- **機能**: バックグラウンド同期
- **設定**: NASマウントポイント、メール設定

### YouTube to Notion
- **ポート**: 5003
- **機能**: YouTube動画要約・Notion保存
- **設定**: YouTube API、Notion API

## 🔧 設定ガイド

### 環境変数の設定
各プロジェクトには`env.example`ファイルが含まれています。これをコピーして`.env`を作成し、実際の値を設定してください。

### APIキーの取得
- **Gemini API**: [Google AI Studio](https://aistudio.google.com/apikey)
- **OpenAI API**: [OpenAI Platform](https://platform.openai.com/api-keys)
- **Notion API**: [Notion Developers](https://www.notion.so/my-integrations)

### NAS環境の設定
- NASのIPアドレスを`YOUR_NAS_IP`に置き換え
- ユーザー名を`YOUR_USERNAME`に置き換え
- 適切なマウントポイントを設定

## 📚 ドキュメント

各プロジェクトの詳細なドキュメントは以下のディレクトリにあります：
- `document-automation/README.md`
- `meeting-minutes-byc/README.md`
- `amazon-analytics/README.md`
- `nas-dashboard/README.md`
- `insta360-auto-sync/README.md`
- `youtube-to-notion/README.md`

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## ⚠️ セキュリティ

- 機密情報（APIキー、パスワード等）は環境変数で管理
- `.env`ファイルはGitにコミットしない
- 本番環境では適切なセキュリティ設定を実施

## 🆘 サポート

問題や質問がある場合は、GitHubのIssuesページで報告してください。

## 📈 ロードマップ

- [ ] モバイルアプリ対応
- [ ] クラウド同期機能
- [ ] 多言語対応
- [ ] プラグインシステム
- [ ] リアルタイム監視

---

**注意**: このプロジェクトは教育・研究目的で公開されています。商用利用の場合は適切なライセンス確認を行ってください。