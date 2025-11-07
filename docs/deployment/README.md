# NAS環境デプロイ仕様

## 📋 概要

NAS環境でのDockerアプリケーションデプロイの共通仕様です。
全プロジェクトで統一されたデプロイ方法を提供します。

## 📁 ディレクトリ構成

```
docs/deployment/
├── README.md                    # このファイル（インデックス）
├── guides/                      # ガイド・手順書
│   ├── setup/                   # セットアップガイド
│   ├── configuration/           # 設定ガイド
│   └── troubleshooting/         # トラブルシューティング
├── reports/                     # 完了報告・サマリー
│   ├── completed/               # 完了済みタスク
│   └── summaries/               # サマリードキュメント
├── archive/                     # アーカイブ（古いトラブルシューティング記録）
│   ├── auth/                    # 認証関連の古い記録
│   ├── nginx/                   # Nginx関連の古い記録
│   ├── deployment/              # デプロイメント関連の古い記録
│   ├── security/                # セキュリティ関連の古い記録
│   └── external-access/         # 外部アクセス関連の古い記録
└── templates/                  # テンプレート
    ├── deploy-nas-template.sh
    └── docker-compose-template.yml
```

## 🚀 主要なガイド

### セットアップガイド (`guides/setup/`)

- **NAS_DEPLOYMENT_SPECIFICATION.md** - NAS環境デプロイ仕様書
- **NAS_DEPLOYMENT_GUIDE.md** - NAS環境デプロイガイド
- **NAS_DEPLOYMENT_STEPS.md** - NASデプロイメント手順
- **HTTPS_SETUP_GUIDE.md** - HTTPS設定ガイド
- **DUCKDNS_SETUP_GUIDE.md** - DuckDNS設定ガイド
- **CERTBOT_DNS_CHALLENGE_GUIDE.md** - Certbot DNSチャレンジガイド
- **CERTIFICATE_AUTO_RENEWAL_SETUP.md** - 証明書自動更新設定
- **FAIL2BAN_INSTALL_SETUP.md** - Fail2Banインストール設定
- **UFW_INSTALL_SETUP.md** - UFWインストール設定

### 設定ガイド (`guides/configuration/`)

- **NGINX_FINAL_CONFIG.md** - Nginx最終設定
- **NGINX_SECURITY_HEADERS_COMPLETE.md** - Nginxセキュリティヘッダー設定
- **NGINX_PROXY_MANAGER_SETUP_COMPLETE.md** - Nginx Proxy Manager設定完了
- **NGINX_PROXY_MANAGER_SETUP_STEP_BY_STEP.md** - Nginx Proxy Manager設定手順
- **SECURITY_SETTINGS_COMPLETE.md** - セキュリティ設定完了
- **SECURITY_CHECKLIST.md** - セキュリティチェックリスト

### トラブルシューティング (`guides/troubleshooting/`)

- **CERTBOT_TROUBLESHOOTING.md** - Certbotトラブルシューティング
- **CERTIFICATE_AUTO_RENEWAL.md** - 証明書自動更新
- **CERTIFICATE_AUTO_RENEWAL_SUMMARY.md** - 証明書自動更新サマリー
- **CRON_FIX.md** - Cron修正
- **CRON_TROUBLESHOOTING.md** - Cronトラブルシューティング
- **DEPLOYMENT_TROUBLESHOOTING.md** - デプロイメントトラブルシューティング
- **FIX_PERMISSION_ERROR.md** - 権限エラー修正
- **FIX_REMAINING_ISSUES.md** - 残りの問題修正

## 📊 完了報告・サマリー

### 完了済みタスク (`reports/completed/`)

- **ALL_PROJECTS_DATA_EXTERNAL_FIX.md** - 全プロジェクトのデータ外部化修正
- **DISK_USAGE_FIX.md** - ディスク使用量修正
- **FINAL_CLEANUP_STEPS.md** - 最終クリーンアップ手順
- **FINAL_STATUS_AND_CLEANUP.md** - 最終ステータスとクリーンアップ
- **PROJECT_CLEANUP_ITEMS.md** - プロジェクトクリーンアップ項目
- **DATA_EXTERNAL_CONFIRMATION.md** - データ外部化確認
- **LOG_OUTPUT_FIX_CONFIRMATION.md** - ログ出力先修正確認
- **LOG_MONITORING_PATH_CONFIRMATION.md** - ログ監視パス確認
- **ENVIRONMENT_SYNC_STATUS.md** - 環境同期ステータス

### サマリードキュメント (`reports/summaries/`)

- **DEPLOYMENT_SUCCESS_REPORT.md** - デプロイ成功報告
- **DEPLOYMENT_COMPLETE_SUMMARY.md** - デプロイ完了サマリー
- **ALL_SERVICES_AUTH_INTEGRATION_SUMMARY.md** - 全サービス認証統合サマリー
- **ALL_SERVICES_SUBFOLDER_COMPLETE.md** - 全サービスサブフォルダ対応完了
- **ALL_SERVICES_EXTERNAL_ACCESS_SETUP.md** - 全サービス外部アクセス設定
- **CURRENT_STATUS_SUMMARY.md** - 現在のステータスサマリー
- **CURRENT_ACCESS_STATUS.md** - 現在のアクセスステータス
- **DASHBOARD_EXTERNAL_ACCESS_SUMMARY.md** - ダッシュボード外部アクセスサマリー

## 🔍 アーカイブ

古いトラブルシューティング記録や完了済みの問題の詳細記録は`archive/`ディレクトリに保存されています。

- **archive/auth/** - 認証関連の古い記録（約60個）
- **archive/nginx/** - Nginx関連の古い記録（約40個）
- **archive/deployment/** - デプロイメント関連の古い記録（約30個）
- **archive/security/** - セキュリティ関連の古い記録（約20個）
- **archive/external-access/** - 外部アクセス関連の古い記録（約10個）

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

### 3. 日常的なデプロイ

```bash
# NAS環境で実行
cd ~/nas-project/project-name
git pull origin main
docker compose up -d --build
```

## 📋 標準的なディレクトリ構造

```
/home/AdminUser/
├── nas-project/                    # Gitリポジトリのルート（ソースコードのみ）
│   ├── project-name/              # プロジェクトディレクトリ
│   │   ├── app.py                 # メインアプリケーション
│   │   ├── docker-compose.yml    # Docker設定
│   │   ├── deploy-nas.sh         # デプロイスクリプト
│   │   ├── .env                   # 実際の稼働設定（Git管理）
│   │   ├── .env.restore           # バックアップ（Git管理外）
│   │   └── env.example            # 環境変数テンプレート
│   └── other-project/
└── nas-project-data/              # 統合データディレクトリ（全データを一元管理）
    └── project-name/
        ├── logs/
        ├── data/
        ├── uploads/
        └── cache/
```

## 📊 プロジェクト一覧

| プロジェクト名 | ポート | データディレクトリ | 状態 |
|---------------|--------|-------------------|------|
| meeting-minutes-byc | 5002 | /home/AdminUser/nas-project-data/meeting-minutes-byc/ | ✅ 稼働中 |
| amazon-analytics | 5001 | /home/AdminUser/nas-project-data/amazon-analytics/ | ✅ 稼働中 |
| document-automation | 5003 | /home/AdminUser/nas-project-data/document-automation/ | ✅ 稼働中 |
| youtube-to-notion | 8111 | /home/AdminUser/nas-project-data/youtube-to-notion/ | ✅ 稼働中 |
| nas-dashboard | 9001 | /home/AdminUser/nas-project-data/nas-dashboard/ | ✅ 稼働中 |
| nas-dashboard-monitoring | 8002 | /home/AdminUser/nas-project-data/nas-dashboard-monitoring/ | ✅ 稼働中 |

## 🔧 クイックリファレンス

### よく使うコマンド

```bash
# コンテナの状態確認
docker ps

# ログの確認
docker logs <container-name>

# コンテナの再起動
docker compose restart

# コンテナの再ビルド
docker compose up -d --build
```

### トラブルシューティング

問題が発生した場合は、`guides/troubleshooting/`ディレクトリを参照してください。

## 📚 関連ドキュメント

- [データ管理ルール](../../DATA_MANAGEMENT_RULES.md)
- [デプロイメントルール](../../DEPLOYMENT_RULES.md)
- [バージョン管理](../../VERSION_MANAGEMENT.md)

---

**作成日**: 2025年10月23日  
**最終更新**: 2025年11月7日  
**対象**: 全NAS環境プロジェクト
