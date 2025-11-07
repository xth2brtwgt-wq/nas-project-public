# Insta360自動同期システム - セットアップガイド

## 概要

このガイドでは、Insta360自動同期システムのセットアップ手順を説明します。

## 前提条件

### PC側（Mac）
- **IPアドレス**: YOUR_MAC_IP_ADDRESS（固定IP推奨）
- **ユーザー名**: Admin
- **共有フォルダ**: Insta360
- **ローカルパス**: `/Users/Yoshi/Movies/Insta360/`
- **ファイル共有**: SMB/CIFSプロトコルが有効

### NAS側（UGreen DXP2800）
- **OS**: Linux
- **Docker**: インストール済み
- **ユーザー**: YOUR_USERNAME
- **プロジェクトディレクトリ**: `~/nas-project/insta360-auto-sync`
- **データディレクトリ**: `~/nas-project-data/insta360-auto-sync/`

## セットアップ手順

### 1. プロジェクトの取得

```bash
# NAS側で実行

# プロジェクトディレクトリに移動
cd ~/nas-project/insta360-auto-sync

# 最新のコードを取得
git pull
```

### 2. 環境変数の設定

```bash
# NAS側で実行

# 1. env.exampleから.envを作成
cp env.example .env

# 2. .envファイルを編集（実際のAPIキー・パスワードを設定）
vim .env
```

**設定項目**:
- `MAC_IP`: Mac側のIPアドレス（例: YOUR_MAC_IP_ADDRESS）
- `MAC_USERNAME`: Mac側のユーザー名（例: Admin）
- `MAC_PASSWORD`: Mac側のパスワード
- `MAC_SHARE`: Mac側の共有フォルダ名（例: Insta360）
- `TO_EMAIL`: メール通知先（例: nas.system.0828@gmail.com）

**注意**: `.env`はGitで管理されます（実際のAPIキー・パスワードを含む）。

```bash
# 3. .envから.env.restoreを作成（バックアップ）
cp .env .env.restore
```

**重要**: `.env.restore`はバックアップ用ファイルです。`git pull`で`.env`が初期化された場合、`.env.restore`から復元できます。

### 3. マウント設定

詳細は [MOUNT_SETUP.md](MOUNT_SETUP.md) を参照してください。

#### 3-1. fstab設定（システム起動時に自動マウント）

```bash
# NAS側で実行

# バックアップ作成
sudo cp /etc/fstab /etc/fstab.backup

# fstabに自動マウント設定を追加
echo "//YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share cifs username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755 0 0" | sudo tee -a /etc/fstab

# 設定テスト
sudo mount -a

# マウント状態を確認
mount | grep mac-share
```

### 4. Docker起動

```bash
# NAS側で実行

# デプロイスクリプト実行
./deploy.sh

# コンテナの状態を確認
docker ps | grep insta360-auto-sync

# ログを確認
docker logs insta360-auto-sync
```

### 5. cronジョブ設定（推奨）

同期処理実行前に自動的にマウントチェックが実行されるように設定します。

詳細は [SYNC_WITH_MOUNT_CHECK.md](SYNC_WITH_MOUNT_CHECK.md) を参照してください。

#### 5-1. スクリプトを使用（推奨）

```bash
# NAS側で実行

# cronジョブ設定スクリプトを実行
chmod +x scripts/setup-cron-sync.sh
./scripts/setup-cron-sync.sh
```

#### 5-2. 手動で設定

```bash
# NAS側で実行

# crontabを編集
crontab -e

# 以下の行を追加（既存の行の下に追加）
0 0 * * * ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh >> ~/nas-project-data/insta360-auto-sync/logs/cron.log 2>&1

# 保存して終了
# viの場合: Esc → :wq → Enter
# nanoの場合: Ctrl+X → Y → Enter

# 設定を確認
crontab -l | grep insta360
```

### 6. 動作確認

```bash
# NAS側で実行

# 1. マウント状態を確認
mount | grep mac-share

# 2. コンテナ内でファイルを確認
docker exec insta360-auto-sync ls -la /source

# 3. 手動実行でテスト
~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh

# 4. cronジョブを確認
crontab -l | grep insta360

# 5. ログを確認
tail -f ~/nas-project-data/insta360-auto-sync/logs/cron.log
```

## 設定ファイルの構成

### 環境変数ファイル

```
.env                # 実際の稼働設定（Gitで管理、実際のAPIキー・パスワードを含む）
.env.restore        # バックアップ用（Git管理外、実行時には使用しない）
env.example         # テンプレート（Gitで管理）
```

**運用フロー**:
- `env.example` → `.env` → `.env.restore`（バックアップ作成）
- トラブル時は `.env.restore` → `.env`（復元）

**重要**: 実行時には`.env`のみを使用します（`.env.restore`は使用しません）。

詳細は [ENV_FILE_STRATEGY.md](../ENV_FILE_STRATEGY.md) を参照してください。

### 設定ファイル

```
config/
├── app.json        # アプリケーション設定
└── email.json      # メール設定
```

### データディレクトリ

```
~/nas-project-data/insta360-auto-sync/
├── logs/           # ログファイル
└── insta360/      # 転送先（実際のパス: /volume2/data/insta360）
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

詳細は [MOUNT_TROUBLESHOOTING.md](MOUNT_TROUBLESHOOTING.md) を参照してください。

#### 2. cronジョブが動作しない

```bash
# cronジョブの確認
crontab -l | grep insta360

# cronサービスの状態確認
sudo systemctl status cron

# ログファイルの確認
tail -f ~/nas-project-data/insta360-auto-sync/logs/cron.log
```

詳細は [CRON_TROUBLESHOOTING.md](CRON_TROUBLESHOOTING.md) を参照してください。

#### 3. ファイルが同期されない

```bash
# ソースディレクトリ確認
docker exec insta360-auto-sync ls -la /source

# 手動同期テスト
docker exec insta360-auto-sync python /app/scripts/sync.py --test
```

詳細は [MANUAL_SYNC_GUIDE.md](MANUAL_SYNC_GUIDE.md) を参照してください。

## 関連ドキュメント

- [README.md](README.md) - プロジェクト概要
- [MOUNT_SETUP.md](MOUNT_SETUP.md) - マウント設定手順
- [SYNC_WITH_MOUNT_CHECK.md](SYNC_WITH_MOUNT_CHECK.md) - 同期処理実行前のマウントチェック設定
- [CRON_SETUP_MANUAL.md](CRON_SETUP_MANUAL.md) - cronジョブ手動設定ガイド
- [CRON_TROUBLESHOOTING.md](CRON_TROUBLESHOOTING.md) - cronジョブトラブルシューティング
- [MANUAL_SYNC_GUIDE.md](MANUAL_SYNC_GUIDE.md) - 手動実行ガイド
- [EMERGENCY_FIX.md](EMERGENCY_FIX.md) - 緊急修正手順

## 更新履歴

- 2025-11-04: 初版作成
  - 同期処理実行前のマウントチェック方式を追加
  - cronジョブ設定手順を追加
  - 環境変数ファイル戦略を追加

