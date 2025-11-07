# Insta360自動同期システム

## 概要
Insta360カメラで撮影したファイルをNAS環境に自動同期するシステムです。PC側の共有フォルダからNAS側のストレージに、スケジュール実行により自動的にファイルを転送します。

## 主な機能

- **自動スケジュール実行**: 毎日00:00に自動実行（cronジョブ）
- **マウントチェック**: 同期処理実行前に自動的にマウント状態を確認・再マウント
- **ファイル形式対応**: MP4、INSV、INSP、JPG、DNG、RAW形式に対応
- **重複ファイル検出**: 既存ファイルのスキップ機能
- **メール通知**: 同期結果のメール通知（オプション）
- **ログ管理**: 詳細な実行ログの記録
- **Docker対応**: コンテナ化による環境分離

## システム構成

### アーキテクチャ
```
PC (Mac) → NAS (UGreen DXP2800) → Docker Container
    ↓              ↓                    ↓
共有フォルダ    CIFSマウント      Python同期スクリプト
```

### ファイルフロー
1. PC側のInsta360共有フォルダにファイルが保存される
2. **cronジョブが毎日00:00に実行される**
3. **マウントチェックスクリプトがマウント状態を確認・再マウント**
4. NAS側でCIFSマウントにより共有フォルダにアクセス
5. Dockerコンテナ内のPythonスクリプトがファイルを検出
6. 指定されたパターンに一致するファイルをNAS側ストレージに転送

## 必要な環境

### PC側（Mac）
- **IPアドレス**: YOUR_MAC_IP_ADDRESS
- **ユーザー名**: Admin
- **共有フォルダ**: Insta360
- **ファイル共有**: SMB/CIFSプロトコル

### NAS側（UGreen DXP2800）
- **OS**: Linux
- **Docker**: 対応済み
- **マウントポイント**: /mnt/mac-share
- **保存先**: /volume2/data/insta360

## セットアップ手順

### 1. 環境変数設定
```bash
# env.exampleをコピーして.envを作成
cp env.example .env

# .envファイルを編集
vim .env
```

### 2. マウント設定
詳細は [MOUNT_SETUP.md](MOUNT_SETUP.md) を参照してください。

### 3. Docker起動
```bash
# デプロイスクリプト実行
./deploy.sh
```

### 4. cronジョブ設定
```bash
# cronジョブ設定スクリプトを実行
chmod +x scripts/setup-cron-sync.sh
./scripts/setup-cron-sync.sh

# または、手動でcrontabを編集
crontab -e
# 以下の行を追加:
# 0 0 * * * ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh >> ~/nas-project-data/insta360-auto-sync/logs/cron.log 2>&1
```

詳細は [SYNC_WITH_MOUNT_CHECK.md](SYNC_WITH_MOUNT_CHECK.md) を参照してください。

## 使用方法

### 手動実行（推奨）
```bash
# マウントチェック付きラッパースクリプトを使用（推奨）
~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh

# または、コンテナ内で直接実行
# テストモード
docker exec insta360-auto-sync python /app/scripts/sync.py --test

# 1回だけ実行
docker exec insta360-auto-sync python /app/scripts/sync.py --once

# ドライランモード
docker exec insta360-auto-sync python /app/scripts/sync.py --dry-run
```

詳細は [MANUAL_SYNC_GUIDE.md](MANUAL_SYNC_GUIDE.md) を参照してください。

### ログ確認
```bash
# リアルタイムログ確認
docker logs -f insta360-auto-sync

# ログファイル確認
tail -f logs/insta360_sync.log
```

## 設定ファイル

### app.json
```json
{
  "sync": {
    "file_patterns": [
      "VID_*.mp4",
      "*.insv",
      "*.insp",
      "*.jpg",
      "*.dng",
      "*.raw"
    ],
    "schedule": "0 0 * * *",
    "delete_source": false,
    "delete_empty_dirs": true
  }
}
```

### docker-compose.yml
```yaml
services:
  insta360-auto-sync:
    build: .
    volumes:
      - /mnt/mac-share:/source
      - /volume2/data/insta360:/volume2/data/insta360
    environment:
      - SOURCE_PATH=/source
      - DESTINATION_PATH=/volume2/data/insta360
      - SYNC_SCHEDULE_TIME=00:00
```

## トラブルシューティング

### よくある問題

#### 1. マウントが解除される
```bash
# マウント状況確認
mount | grep mac-share

# 再マウント
sudo mount -a

# または、マウントチェック付きスクリプトを使用（自動的に再マウント）
~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh
```

**注意**: 同期処理実行前に自動的にマウントチェックが実行されるため、通常は手動で再マウントする必要はありません。

#### 2. ファイルが同期されない
```bash
# ソースディレクトリ確認
docker exec insta360-auto-sync ls -la /source

# 手動同期テスト
docker exec insta360-auto-sync python scripts/sync.py --test
```

#### 3. スケジュールが動作しない
```bash
# cronジョブの確認
crontab -l | grep insta360

# cronサービスの状態確認
sudo systemctl status cron

# cronログの確認
sudo journalctl -u cron -n 50

# または、ログファイルの確認
tail -f ~/nas-project-data/insta360-auto-sync/logs/cron.log

# コンテナ再起動
docker restart insta360-auto-sync

# ログ確認
docker logs insta360-auto-sync --tail 50
```

詳細は [CRON_TROUBLESHOOTING.md](CRON_TROUBLESHOOTING.md) を参照してください。

### 緊急修正
問題が発生した場合は [EMERGENCY_FIX.md](EMERGENCY_FIX.md) を参照してください。

## ファイル構成

```
insta360-auto-sync/
├── scripts/
│   ├── sync.py                        # メイン同期スクリプト
│   ├── sync-with-mount-check.sh       # マウントチェック付きラッパースクリプト
│   ├── setup-cron-sync.sh             # cronジョブ設定スクリプト
│   ├── remove-duplicate-cron.sh       # cronジョブ重複削除スクリプト
│   └── fix-insta360-schedule.sh       # 緊急修正スクリプト
├── utils/
│   ├── config_utils.py                # 設定管理
│   ├── file_utils.py                  # ファイル操作
│   ├── email_sender.py                # メール送信
│   └── mount_utils.py                 # マウント管理
├── config/
│   ├── app.json                       # アプリケーション設定
│   └── email.json                     # メール設定
├── docker-compose.yml                 # Docker Compose設定
├── Dockerfile                        # Dockerイメージ定義
├── deploy.sh                         # デプロイスクリプト
├── env.example                       # 環境変数設定例
├── README.md                         # このファイル
├── MOUNT_SETUP.md                    # マウント設定手順
├── SYNC_WITH_MOUNT_CHECK.md          # 同期処理実行前のマウントチェック設定
├── CRON_SETUP_MANUAL.md              # cronジョブ手動設定ガイド
├── CRON_TROUBLESHOOTING.md           # cronジョブトラブルシューティング
├── CRON_PERMISSION_FIX.md            # cronジョブ権限エラー対処法
├── MANUAL_SYNC_GUIDE.md              # 手動実行ガイド
└── EMERGENCY_FIX.md                  # 緊急修正手順
```

## バージョン履歴

### v1.1.0 (2025-11-04)
- 同期処理実行前のマウントチェック機能を追加
- systemdタイマーによる常時監視から、必要なときだけマウントチェックする方式に変更
- cronジョブによる実行方式に変更
- `.env`ファイル読み込みエラーの修正
- マウント管理ユーティリティの追加
- ドキュメントの大幅な更新

### v1.0.1 (2025-10-27)
- 重複ログ出力の修正
- ドキュメント更新

### v1.0.0 (2025-10-24)
- 初回リリース
- 基本的な同期機能
- スケジュール実行機能
- メール通知機能

## ライセンス
このプロジェクトはMITライセンスの下で公開されています。

## 連絡先
問題や質問がある場合は、システム管理者に連絡してください。

---
**最終更新**: 2025年11月4日  
**バージョン**: 1.1.0
