# Meeting Minutes BYC - NAS環境デプロイメントガイド

## 🎯 概要

Meeting Minutes BYC（議事録作成システム）をNAS環境にデプロイする手順です。テンプレート切り替え機能を含む最新版を本番環境で運用できます。

## 📋 前提条件

- Ugreen NAS (DXP2800)
- Docker & Docker Compose がインストール済み
- 管理者権限 (AdminUser)
- インターネット接続（Gemini API用）

## 🚀 デプロイ手順

### 1. NASに接続
```bash
ssh -p 23456 AdminUser@192.168.68.110
```

### 2. プロジェクトディレクトリに移動
```bash
cd /home/AdminUser/nas-project/meeting-minutes-byc
```

### 3. 最新のコードを取得
```bash
git pull origin main
```

### 4. 環境変数の設定
```bash
# 環境変数ファイルをコピー
cp env.example env.production

# 環境変数を編集
nano env.production
```

**必須設定項目:**
```bash
# Gemini API設定（必須）
GEMINI_API_KEY=your_actual_gemini_api_key_here

# アプリケーション設定
FLASK_ENV=production
FLASK_DEBUG=False
UPLOAD_DIR=/app/uploads
TRANSCRIPT_DIR=/app/transcripts

# サーバー設定
HOST=0.0.0.0
PORT=5002

# Notion設定（オプション）
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here

# メール設定（オプション）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_FROM=your_email@gmail.com
```

### 5. NAS環境用デプロイスクリプトを実行
```bash
chmod +x deploy-nas.sh
./deploy-nas.sh
```

## 📊 アクセス情報

デプロイ完了後、以下のURLでアクセスできます：

- **議事録作成システム**: http://192.168.68.110:5002
- **ヘルスチェック**: http://192.168.68.110:5002/health
- **統合管理ダッシュボード**: http://192.168.68.110:9001

## 🔧 管理コマンド

### コンテナ管理
```bash
# ログ確認
docker logs -f meeting-minutes-byc

# コンテナ停止
docker compose down

# コンテナ再起動
docker compose restart

# コンテナ状態確認
docker ps | grep meeting-minutes-byc

# ヘルスチェック
curl http://localhost:5000/health
```

### データ管理
```bash
# アップロードファイル確認
ls -la /home/AdminUser/meeting-minutes-data/uploads/

# 議事録ファイル確認
ls -la /home/AdminUser/meeting-minutes-data/transcripts/

# テンプレートファイル確認
ls -la /home/AdminUser/meeting-minutes-data/templates/

# ログファイル確認
ls -la /home/AdminUser/meeting-minutes-data/logs/
```

## 🆕 新機能: テンプレート管理

### 利用可能なテンプレート
1. **標準議事録**: 一般的な会議用の包括的なテンプレート
2. **簡潔版議事録**: 要点を簡潔にまとめたテンプレート
3. **詳細版議事録**: 詳細な分析と背景情報を含む包括的なテンプレート

### テンプレート管理機能
- テンプレート選択（会議情報入力時）
- カスタムテンプレート作成
- テンプレート編集・削除
- デフォルトテンプレート設定

## 🛡️ セキュリティ設定

### 環境変数の保護
```bash
# 環境変数ファイルの権限設定
chmod 600 env.production

# バックアップの作成
cp env.production env.production.backup
```

### ファイアウォール設定
```bash
# ポート5002の開放確認
sudo ufw allow 5002
sudo ufw status
```

## 📈 監視とメンテナンス

### ログ監視
```bash
# リアルタイムログ監視
docker logs -f meeting-minutes-byc

# ログファイルの確認
tail -f /home/AdminUser/meeting-minutes-data/logs/app.log
```

### ディスク使用量監視
```bash
# データディレクトリの使用量確認
du -sh /home/AdminUser/meeting-minutes-data/*

# 古いファイルのクリーンアップ
find /home/AdminUser/meeting-minutes-data/uploads -type f -mtime +7 -delete
```

### バックアップ
```bash
# データバックアップ
tar -czf meeting-minutes-backup-$(date +%Y%m%d).tar.gz /home/AdminUser/meeting-minutes-data/

# 設定ファイルバックアップ
cp env.production meeting-minutes-config-$(date +%Y%m%d).backup
```

## 🔄 アップデート手順

### 1. 現在のコンテナを停止
```bash
docker compose down
```

### 2. 最新コードを取得
```bash
git pull origin main
```

### 3. 再デプロイ
```bash
./deploy-nas.sh
```

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. コンテナが起動しない
```bash
# ログを確認
docker logs meeting-minutes-byc

# 環境変数を確認
cat env.production

# ポートの競合を確認
netstat -tlnp | grep 5002
```

#### 2. Gemini API エラー
```bash
# API キーを確認
echo $GEMINI_API_KEY

# 環境変数ファイルを再読み込み
export $(grep -v '^#' env.production | xargs)
```

#### 3. ファイルアップロードエラー
```bash
# ディレクトリ権限を確認
ls -la /home/AdminUser/meeting-minutes-data/

# 権限を修正
chmod 755 /home/AdminUser/meeting-minutes-data/uploads
```

#### 4. メール送信エラー
```bash
# SMTP設定を確認
grep SMTP env.production

# テスト送信
curl -X POST http://localhost:5000/test-email
```

## 📞 サポート

問題が解決しない場合は、以下の情報を収集してサポートに連絡してください：

1. エラーログ: `docker logs meeting-minutes-byc`
2. システム情報: `docker version` と `docker compose version`
3. 環境変数設定: `cat env.production`（機密情報は除く）
4. ディスク使用量: `df -h`

## 🎉 デプロイ完了後の確認事項

- [ ] ブラウザで http://192.168.68.110:5002 にアクセス可能
- [ ] テンプレート選択ドロップダウンが表示される
- [ ] テンプレート管理画面が開ける
- [ ] 音声ファイルのアップロードが可能
- [ ] 議事録生成が正常に動作する
- [ ] メール送信機能が動作する（設定済みの場合）
- [ ] Notion連携が動作する（設定済みの場合）

これで、Meeting Minutes BYCがNAS環境で正常に動作するはずです！
