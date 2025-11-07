# Insta360自動同期 - cronジョブ手動設定ガイド

## 概要

`crontab`コマンドで権限エラーが発生する場合、手動でcronジョブを設定する方法です。

## 手動設定手順

### 方法1: crontab -e で直接編集（推奨）

```bash
# NAS側で実行

# 1. crontabを編集
crontab -e

# 2. エディタが開いたら、以下の行を追加（既存のinsta360関連の行を削除してから追加）
0 0 * * * ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh >> ~/nas-project-data/insta360-auto-sync/logs/cron.log 2>&1

# 3. 保存して終了
# viの場合:
#   Esc → :wq → Enter
# nanoの場合:
#   Ctrl+X → Y → Enter
```

### 方法2: 一時ファイルを使用（権限エラーが発生する場合）

```bash
# NAS側で実行

# 1. 既存のcrontabをバックアップ
crontab -l > /tmp/crontab.backup

# 2. 既存のinsta360関連のエントリを削除して新しいエントリを追加
(crontab -l 2>/dev/null | grep -v "insta360-auto-sync" | grep -v "sync-with-mount-check.sh" | grep -v "sync.py"; \
 echo "0 0 * * * ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh >> ~/nas-project-data/insta360-auto-sync/logs/cron.log 2>&1") > /tmp/crontab.new

# 3. 新しいcrontabを設定
crontab /tmp/crontab.new

# 4. 一時ファイルを削除
rm -f /tmp/crontab.new

# 5. 設定を確認
crontab -l | grep insta360
```

### 方法3: スクリプトを使用（推奨）

```bash
# NAS側で実行

cd ~/nas-project/insta360-auto-sync
chmod +x scripts/setup-cron-sync.sh
./scripts/setup-cron-sync.sh
```

## 設定確認

```bash
# NAS側で実行

# cronジョブを確認
crontab -l | grep insta360

# すべてのcronジョブを確認
crontab -l
```

## 手動実行でテスト

```bash
# NAS側で実行

# ラッパースクリプトを手動実行
~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh
```

## トラブルシューティング

### 権限エラーが発生する場合

```bash
# NAS側で実行

# 1. 現在のユーザーを確認
whoami

# 2. crontabの権限を確認
ls -la /var/spool/cron/

# 3. 自分のcrontabファイルの権限を確認
ls -la /var/spool/cron/crontabs/$(whoami) 2>/dev/null || echo "ファイルが見つかりません"

# 4. crontab -e で直接編集（最も確実）
crontab -e
```

### cronジョブが実行されない場合

```bash
# NAS側で実行

# 1. cronサービスの状態を確認
sudo systemctl status cron
# または
sudo systemctl status crond

# 2. cronログを確認
sudo journalctl -u cron -n 50
# または
sudo tail -f /var/log/cron

# 3. 手動でスクリプトを実行してテスト
~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh
```

## 注意事項

- cronジョブは**ユーザー自身のcrontab**に設定する必要があります（`sudo`を使わない）
- パスは**絶対パス**で指定してください
- ログファイルのディレクトリが存在することを確認してください
- スクリプトに実行権限があることを確認してください











