# Insta360自動同期 - 自動再マウント設定（シンプル版）

## 概要

実行中にマウントが解除された場合に自動的に再マウントする設定方法です。

## 現在の状態

- ✅ マウントは成功している
- ✅ マウントチェックスクリプト `/usr/local/bin/check-mac-share-mount.sh` は存在
- ❌ cronジョブが設定されていない（権限エラーのため）

## 解決方法

### 方法1: crontab -e で直接編集（推奨）

```bash
# NAS側で実行
crontab -e

# エディタが開いたら、以下の行を追加
*/5 * * * * /usr/local/bin/check-mac-share-mount.sh

# 保存して終了
# viの場合は: Esc → :wq → Enter
# nanoの場合は: Ctrl+X → Y → Enter
```

### 方法2: echoとパイプを使用

```bash
# NAS側で実行

# 既存のcronジョブを取得して、新しいエントリを追加
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/check-mac-share-mount.sh") | crontab -

# 確認
crontab -l | grep check-mac-share-mount
```

### 方法3: systemdタイマーを使用（より確実）

```bash
# NAS側で実行

# 1. systemdタイマーユニットファイルを作成
sudo tee /etc/systemd/system/check-mac-share-mount.timer > /dev/null << 'EOF'
[Unit]
Description=Mac Share Mount Check Timer
After=network-online.target

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
Unit=check-mac-share-mount.service

[Install]
WantedBy=timers.target
EOF

# 2. systemdサービスユニットファイルを作成
sudo tee /etc/systemd/system/check-mac-share-mount.service > /dev/null << 'EOF'
[Unit]
Description=Mac Share Mount Check
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/check-mac-share-mount.sh
User=root
EOF

# 3. systemd設定を再読み込み
sudo systemctl daemon-reload

# 4. タイマーを有効化
sudo systemctl enable --now check-mac-share-mount.timer

# 5. 動作確認
sudo systemctl status check-mac-share-mount.timer
```

## 動作確認

### cronジョブの場合

```bash
# NAS側で実行
# 1. cronジョブの確認
crontab -l | grep check-mac-share-mount

# 2. 手動でスクリプトを実行してテスト
sudo /usr/local/bin/check-mac-share-mount.sh

# 3. マウント状態を確認
mount | grep mac-share
```

### systemdタイマーの場合

```bash
# NAS側で実行
# 1. タイマーの状態確認
sudo systemctl status check-mac-share-mount.timer

# 2. タイマーの一覧確認
sudo systemctl list-timers | grep check-mac-share-mount

# 3. 手動でサービスを実行してテスト
sudo systemctl start check-mac-share-mount.service

# 4. マウント状態を確認
mount | grep mac-share
```

## 推奨設定

**systemdタイマー**を使用することを推奨します：
- cronジョブよりも確実
- ログ管理が容易
- 状態確認が簡単

## まとめ

| 方法 | 設定の簡単さ | 確実性 | 推奨度 |
|------|------------|--------|--------|
| crontab -e | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| echo + crontab | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| systemdタイマー | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 関連ドキュメント

- [AUTO_REMOUNT_GUIDE.md](AUTO_REMOUNT_GUIDE.md) - 詳細な自動再マウント設定ガイド
- [MOUNT_SETUP.md](MOUNT_SETUP.md) - マウント設定の詳細手順











