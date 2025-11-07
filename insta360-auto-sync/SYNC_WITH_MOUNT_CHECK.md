# Insta360自動同期 - 同期処理実行前のマウントチェック設定

## 概要

普段はマウントされていなくてもOKで、**同期処理が実行される前にのみ**マウント状態を確認して再マウントする方式に変更しました。

## 変更内容

### 従来の方式
- systemdタイマーで5分ごとにマウント状態をチェック
- 常にマウントを維持する必要がある

### 新しい方式
- 同期処理実行前にのみマウント状態をチェック
- マウントされていない場合は自動的に再マウント
- 普段はマウントされていなくてもOK

## 設定手順

### 1. 既存のsystemdタイマーを無効化（推奨）

```bash
# NAS側で実行

# systemdタイマーを停止・無効化
sudo systemctl stop check-mac-share-mount.timer
sudo systemctl disable check-mac-share-mount.timer

# タイマーの状態を確認
sudo systemctl status check-mac-share-mount.timer
```

### 2. ラッパースクリプトを配置

```bash
# NAS側で実行

# ラッパースクリプトを配置
cd ~/nas-project/insta360-auto-sync
chmod +x scripts/sync-with-mount-check.sh
```

### 3. cronジョブを更新（毎日00:00に実行）

```bash
# NAS側で実行

# 既存のcronジョブを確認
crontab -l | grep insta360

# cronジョブを更新（既存のエントリを削除して追加）
(crontab -l 2>/dev/null | grep -v "insta360-auto-sync" | grep -v "sync.py"; \
 echo "0 0 * * * ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh >> ~/nas-project-data/insta360-auto-sync/logs/cron.log 2>&1") | crontab -

# cronジョブを確認
crontab -l | grep insta360
```

### 4. 手動実行でテスト

```bash
# NAS側で実行

# ラッパースクリプトを手動実行
~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh
```

## 動作フロー

1. **cronジョブが実行**（毎日00:00）
2. **ラッパースクリプトが実行**
   - マウント状態をチェック
   - マウントされていない場合は再マウント
   - マウントが成功したら次のステップへ
   - マウントが失敗したらエラーで終了
3. **同期処理を実行**
   - コンテナ内で`sync.py --once`を実行
   - ファイルを検索・転送

## メリット

- **効率的**: 必要なときだけマウントを確認・実行
- **シンプル**: systemdタイマーが不要（無効化可能）
- **柔軟**: 普段はマウントされていなくてもOK
- **確実**: 同期処理実行前に必ずマウント状態を確認

## トラブルシューティング

### マウントに失敗する場合

```bash
# NAS側で実行

# マウント状態を確認
mount | grep mac-share

# 手動でマウントを試みる
sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755

# Mac側の共有設定を確認
# - Mac側で「システム環境設定 > 共有 > ファイル共有」が有効か確認
# - 「共有名」が「Insta360」になっているか確認
# - Mac側のIPアドレスが正しいか確認（YOUR_MAC_IP_ADDRESS）
```

### 同期処理が実行されない場合

```bash
# NAS側で実行

# コンテナの状態を確認
docker ps | grep insta360-auto-sync

# コンテナのログを確認
docker logs insta360-auto-sync

# 手動で同期処理を実行
docker exec insta360-auto-sync python /app/scripts/sync.py --once
```

### cronジョブが実行されない場合

```bash
# NAS側で実行

# cronジョブを確認
crontab -l

# cronサービスのログを確認
sudo journalctl -u cron -n 50

# cronログを確認
tail -f ~/nas-project-data/insta360-auto-sync/logs/cron.log
```

## 注意事項

- マウントに失敗した場合、同期処理は実行されません
- マウントが成功するまで、Mac側の共有フォルダが有効になっている必要があります
- パスワードは`scripts/sync-with-mount-check.sh`に直接記述されています（環境変数化を推奨）

## 関連ファイル

- `scripts/sync-with-mount-check.sh`: マウントチェック付きラッパースクリプト
- `scripts/sync.py`: 同期処理メインスクリプト
- `utils/mount_utils.py`: マウント管理ユーティリティ（コンテナ内からは使用不可）











