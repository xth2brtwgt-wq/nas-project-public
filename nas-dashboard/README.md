# NAS統合管理ダッシュボード

NAS環境で稼働する統合管理ダッシュボードシステムです。

## 🚀 機能概要

### メイン機能
- **システム監視**: 各プロジェクトの稼働状況をリアルタイム監視
- **ログ監視**: システムログとDockerコンテナログの統合監視
- **バックアップ管理**: 自動バックアップの実行と管理
- **セキュリティ監視**: fail2banによる不正アクセス監視
- **週次レポート**: 自動レポート生成とメール送信

### ログ監視機能
- **テキストログ**: 各システムのログファイルを個別表示
  - Meeting Minutes BYC
  - Amazon Analytics
  - Document Automation
  - YouTube to Notion
  - NAS Dashboard
- **Dockerログ**: 全コンテナのログをリアルタイム表示
- **フィルタリング**: ログレベル別フィルタリング機能
- **自動更新**: 定期的なログ更新機能

## 🛠 技術スタック

- **Backend**: Python Flask
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Database**: SQLite
- **Container**: Docker & Docker Compose
- **Monitoring**: 統合ログ監視システム

## 📁 プロジェクト構成

```
nas-dashboard/
├── app.py                 # メインアプリケーション
├── templates/
│   ├── dashboard.html     # メインダッシュボード
│   └── log_viewer.html   # ログ監視画面
├── config/
│   └── settings.py        # 設定ファイル
├── utils/
│   ├── ai_analyzer.py     # AI分析機能
│   └── email_sender.py    # メール送信機能
├── scripts/
│   ├── auto_version_update.py      # 自動バージョン更新
│   └── weekly_report_scheduler.py  # 週次レポートスケジューラー
├── docker-compose.yml     # Docker Compose設定
├── Dockerfile            # Docker設定
└── requirements.txt      # Python依存関係
```

## 🚀 セットアップ

### 1. 環境変数設定
```bash
# .env.local ファイルを作成
cp env.example .env.local

# 必要な設定を編集
vim .env.local
```

### 2. Docker起動
```bash
# 開発環境
docker compose up -d

# 本番環境（NAS）
docker compose -f docker-compose.yml up -d --build
```

### 3. アクセス
- **ダッシュボード**: http://localhost:9001
- **ログ監視**: http://localhost:9001/logs

## 📊 ログ監視機能詳細

### テキストログ監視
- 各システムのログファイルを個別に監視
- ドロップダウンでシステムを選択
- 最新50行のログを表示
- ログレベル別の色分け表示

### Dockerログ監視
- 全Dockerコンテナのログを監視
- ドロップダウンでコンテナを選択
- 最新100行のログを表示
- 空行フィルタリング機能

### フィルタリング機能
- **INFO**: 情報ログ（白色）
- **WARNING**: 警告ログ（黄色）
- **ERROR**: エラーログ（赤色）
- **DEBUG**: デバッグログ（灰色）

## 🔧 開発・メンテナンス

### バージョン管理
- 自動バージョン更新機能
- Gitコミット時に自動バージョンアップ
- セマンティックバージョニング対応

### ログ設定
- 各システムのログファイルパス設定
- ログレベル設定
- ローテーション設定

### デプロイメント
- NAS環境への自動デプロイ
- Docker Composeによるコンテナ管理
- 環境変数による設定管理

## 📝 更新履歴

### v1.0.0 (2025-01-21)
- 初期リリース
- 基本ダッシュボード機能
- システム監視機能

### v1.1.0 (2025-10-25)
- ログ監視機能追加
- テキストログとDockerログの統合監視
- デザイン改善とUI統一
- 空行フィルタリング機能

## 🤝 貢献

1. 機能追加やバグ修正
2. ドキュメントの改善
3. テストケースの追加

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 📞 サポート

問題や質問がある場合は、GitHubのIssuesページで報告してください。
