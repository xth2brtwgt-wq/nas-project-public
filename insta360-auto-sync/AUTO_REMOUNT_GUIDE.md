# Insta360自動同期 - 自動再マウント設定ガイド

## 概要

fstabの設定だけでは、**システム起動時のみ**自動マウントされます。実行中にマウントが解除された場合、自動的に再マウントされません。

このガイドでは、マウントが解除された場合に自動的に再マウントする方法を説明します。

## 現在の動作

### fstab設定の場合

- ✅ **システム起動時**: 自動的にマウントされる
- ❌ **実行中に解除された場合**: 自動的に再マウントされない（手動で `sudo mount -a` が必要）

## 自動再マウントの方法

### 方法1: systemd自動マウント（推奨）

systemd自動マウントを使用すると、マウントポイントにアクセスしたときに自動的にマウントされます。

#### 設定手順

```bash
# NAS側で実行

# 1. 既存のユニットファイルを削除（存在する場合）
sudo systemctl stop mnt-mac-share.automount 2>/dev/null || true
sudo systemctl disable mnt-mac-share.automount 2>/dev/null || true
sudo rm -f /etc/systemd/system/mnt-mac-share.automount
sudo rm -f /etc/systemd/system/mnt-mac-share.mount
sudo systemctl daemon-reload

# 2. systemdマウントユニットファイルを作成（先に作成する必要がある）
sudo tee /etc/systemd/system/mnt-mac-share.mount > /dev/null << 'EOF'
[Unit]
Description=Mac Share Mount
After=network-online.target
Wants=network-online.target

[Mount]
What=//YOUR_MAC_IP_ADDRESS/Insta360
Where=/mnt/mac-share
Type=cifs
Options=username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755

[Install]
WantedBy=multi-user.target
EOF

# 3. systemd自動マウントユニットファイルを作成
sudo tee /etc/systemd/system/mnt-mac-share.automount > /dev/null << 'EOF'
[Unit]
Description=Mac Share Auto Mount
After=network-online.target
Wants=network-online.target

[Automount]
Where=/mnt/mac-share
TimeoutIdleSec=0

[Install]
WantedBy=multi-user.target
EOF

# 4. systemd設定を再読み込み
sudo systemctl daemon-reload

# 5. 自動マウントを有効化
sudo systemctl enable --now mnt-mac-share.automount

# 6. 動作確認
sudo systemctl status mnt-mac-share.automount

# 7. マウントポイントにアクセスして自動マウントをテスト
ls /mnt/mac-share
```

#### 動作確認

```bash
# マウントポイントにアクセス（自動的にマウントされる）
ls /mnt/mac-share

# マウント状態を確認
mount | grep mac-share
```

### 方法2: cronジョブ（シンプル）

定期的にマウント状態をチェックして、解除されていれば再マウントします。

#### 設定手順

```bash
# NAS側で実行

# 1. マウントチェックスクリプトを作成
sudo tee /usr/local/bin/check-mac-share-mount.sh > /dev/null << 'EOF'
#!/bin/bash
# Mac Share マウント状態チェックスクリプト

MOUNT_POINT="/mnt/mac-share"
MOUNT_SOURCE="//YOUR_MAC_IP_ADDRESS/Insta360"
MOUNT_OPTIONS="username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755"

# マウント状態をチェック
if ! mount | grep -q "${MOUNT_POINT}"; then
    logger "Mac Share マウントが解除されています。再マウントを実行します。"
    mount -t cifs "${MOUNT_SOURCE}" "${MOUNT_POINT}" -o "${MOUNT_OPTIONS}"
    if [ $? -eq 0 ]; then
        logger "Mac Share マウントが成功しました。"
    else
        logger "Mac Share マウントに失敗しました。"
    fi
fi
EOF

# 2. 実行権限を付与
sudo chmod +x /usr/local/bin/check-mac-share-mount.sh

# 3. cronジョブを追加（5分ごとにチェック）
(crontab -l 2>/dev/null | grep -v "check-mac-share-mount"; echo "*/5 * * * * /usr/local/bin/check-mac-share-mount.sh") | crontab -

# 4. cronジョブを確認
crontab -l | grep check-mac-share-mount
```

#### 動作確認

```bash
# 手動でスクリプトを実行してテスト
sudo /usr/local/bin/check-mac-share-mount.sh

# ログを確認
journalctl -u cron | grep "Mac Share" | tail -10
# または
grep "Mac Share" /var/log/syslog | tail -10
```

### 方法3: fstab + autoオプション（基本）

fstabに `auto` オプションを追加すると、システム起動時に自動マウントされますが、実行中に解除された場合は再マウントされません。

```bash
# NAS側で実行
# fstabの設定例（既に設定済みの場合）
# //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share cifs username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755 0 0
```

## 推奨設定

### 組み合わせ設定（推奨）

1. **fstab設定**: システム起動時に自動マウント
2. **systemd自動マウント**: 実行中に解除された場合の自動再マウント

```bash
# NAS側で実行

# 1. fstab設定を確認（既に設定済み）
grep "mac-share" /etc/fstab

# 2. systemd自動マウントを設定（上記の方法1を実行）
```

### または

1. **fstab設定**: システム起動時に自動マウント
2. **cronジョブ**: 定期的にマウント状態をチェックして再マウント

```bash
# NAS側で実行

# 1. fstab設定を確認（既に設定済み）
grep "mac-share" /etc/fstab

# 2. cronジョブを設定（上記の方法2を実行）
```

## 動作確認

### systemd自動マウントの場合

```bash
# 1. 自動マウントサービスの状態確認
sudo systemctl status mnt-mac-share.automount

# 2. マウントポイントへのアクセス（自動的にマウントされる）
ls /mnt/mac-share

# 3. マウント状態を確認
mount | grep mac-share
```

### cronジョブの場合

```bash
# 1. cronジョブの確認
crontab -l | grep check-mac-share-mount

# 2. マウント状態を確認
mount | grep mac-share

# 3. 手動でスクリプトを実行してテスト
sudo /usr/local/bin/check-mac-share-mount.sh
```

## トラブルシューティング

### systemd自動マウントが動作しない場合

```bash
# 1. サービス状態を確認
sudo systemctl status mnt-mac-share.automount
sudo systemctl status mnt-mac-share.mount

# 2. ログを確認
sudo journalctl -u mnt-mac-share.automount -n 50
sudo journalctl -u mnt-mac-share.mount -n 50

# 3. サービスを再起動
sudo systemctl restart mnt-mac-share.automount
```

### cronジョブが動作しない場合

```bash
# 1. cronジョブの確認
crontab -l

# 2. cronサービスが動作しているか確認
sudo systemctl status cron
# または
sudo systemctl status crond

# 3. ログを確認
journalctl -u cron | grep check-mac-share-mount | tail -20
```

## 注意事項

1. **systemd自動マウント**: マウントポイントへのアクセス時に自動的にマウントされます。アイドル状態が続くと自動的にアンマウントされる場合があります（`TimeoutIdleSec=0` で無効化可能）

2. **cronジョブ**: 定期的にチェックするため、マウント解除から最大5分（設定による）の遅延が発生する可能性があります

3. **fstab設定**: システム起動時のみ自動マウントされます。実行中に解除された場合は再マウントされません

## まとめ

| 方法 | 起動時マウント | 実行中再マウント | 推奨度 |
|------|--------------|----------------|--------|
| fstabのみ | ✅ | ❌ | ⭐⭐ |
| fstab + systemd自動マウント | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| fstab + cronジョブ | ✅ | ✅（遅延あり） | ⭐⭐⭐⭐ |

**推奨**: fstab設定に加えて、systemd自動マウントを設定することをお勧めします。

## 関連ドキュメント

- [MOUNT_SETUP.md](MOUNT_SETUP.md) - マウント設定の詳細手順
- [MOUNT_TROUBLESHOOTING.md](MOUNT_TROUBLESHOOTING.md) - マウント問題の診断と修正
- [MOUNT_CONNECTION_FIX.md](MOUNT_CONNECTION_FIX.md) - マウント接続エラーの修正

