# Insta360自動同期 - マウント設定ドキュメント

## 概要
NAS側からPC側の共有フォルダをマウントして、Insta360ファイルを自動同期するための設定手順。

## 設定日時
2025年10月27日（最終更新）

## マウント設定

### 1. 手動マウント（一時的）
```bash
# 既存のマウントを解除
sudo umount /mnt/mac-share

# 手動マウント実行
sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD
```

### 2. 自動マウント設定（永続化）
```bash
# バックアップ作成
sudo cp /etc/fstab /etc/fstab.backup

# fstabに自動マウント設定を追加
echo "//YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share cifs username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755 0 0" | sudo tee -a /etc/fstab

# 設定テスト
sudo mount -a
```

## 設定内容

### PC側設定
- **IPアドレス**: YOUR_MAC_IP_ADDRESS
- **ユーザー名**: Admin
- **パスワード**: 0828
- **共有フォルダ**: Insta360（Mac側のローカルパス: `/Users/Yoshi/Movies/Insta360/`）

### NAS側設定
- **マウントポイント**: /mnt/mac-share
- **コンテナ内パス**: /source
- **保存先**: /volume2/data/insta360

## Docker Compose設定

### docker-compose.yml
```yaml
services:
  insta360-auto-sync:
    volumes:
      - /mnt/mac-share:/source  # PC側のマウントポイント
      - /volume2/data/insta360:/volume2/data/insta360  # NAS側の保存先
    environment:
      - SOURCE_PATH=/source
      - DESTINATION_PATH=/volume2/data/insta360
```

## 動作確認

### 1. マウント状況確認
```bash
# マウント状況確認
mount | grep mac-share

# ファイル確認
ls -la /mnt/mac-share
```

### 2. コンテナ内確認
```bash
# コンテナ内でファイル確認
docker exec -it insta360-auto-sync ls -la /source

# 手動同期テスト
docker exec -it insta360-auto-sync python /app/scripts/manual_sync.py
```

## トラブルシューティング

### マウントが解除された場合

#### 手動再マウント
```bash
# マウント状況確認
mount | grep mac-share

# 再マウント
sudo mount -a
```

#### 自動再マウント設定（推奨）
実行中にマウントが解除された場合に自動的に再マウントするには、以下の方式を設定してください：

**推奨**: 同期処理実行前のマウントチェック方式（[SYNC_WITH_MOUNT_CHECK.md](SYNC_WITH_MOUNT_CHECK.md)）
- 同期処理実行前に自動的にマウント状態を確認・再マウント
- 普段はマウントされていなくてもOK
- 必要なときだけマウントを確認・実行

**代替方法**:
1. **systemd自動マウント**: [AUTO_REMOUNT_GUIDE.md](AUTO_REMOUNT_GUIDE.md) の方法1を参照
2. **cronジョブ**: [AUTO_REMOUNT_GUIDE.md](AUTO_REMOUNT_GUIDE.md) の方法2を参照

### コンテナ内でファイルが見えない場合
```bash
# コンテナ再起動
docker-compose down
docker-compose up -d

# 確認
docker exec -it insta360-auto-sync ls -la /source
```

## 注意事項

1. **PC再起動時**: 自動的にマウントされる（fstab設定により）
2. **NAS再起動時**: 自動的にマウントされる（fstab設定により）
3. **実行中にマウントが解除された場合**: 
   - fstabだけでは自動再マウントされない
   - **推奨**: 同期処理実行前のマウントチェック方式（[SYNC_WITH_MOUNT_CHECK.md](SYNC_WITH_MOUNT_CHECK.md)）
   - **代替**: systemd自動マウントまたはcronジョブ（[AUTO_REMOUNT_GUIDE.md](AUTO_REMOUNT_GUIDE.md)）
4. **パスワード変更時**: fstab設定と`.env`ファイルの更新が必要
5. **IPアドレス変更時**: fstab設定と`config/app.json`、`.env`ファイルの更新が必要

## 関連ファイル

- `/etc/fstab`: 自動マウント設定
- `/etc/fstab.backup`: 設定バックアップ
- `docker-compose.yml`: コンテナ設定
- `/mnt/mac-share`: マウントポイント

