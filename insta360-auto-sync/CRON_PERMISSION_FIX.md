# Insta360自動同期 - cronジョブ権限エラー対処法

## 問題: `/var/spool/cron/: mkstemp: Permission denied`

### 原因

crontabコマンドが一時ファイルを作成する際に、`/var/spool/cron/`ディレクトリへの書き込み権限がない場合に発生します。

## 解決方法

### 方法1: crontabファイルを直接編集（推奨）

```bash
# NAS側で実行

# 1. 現在のユーザーを確認
whoami

# 2. crontabファイルの場所を確認
ls -la /var/spool/cron/crontabs/$(whoami)

# 3. crontabファイルを直接編集（sudoが必要な場合がある）
sudo vi /var/spool/cron/crontabs/$(whoami)

# または nano を使用
sudo nano /var/spool/cron/crontabs/$(whoami)

# 4. 以下の行を追加（既存の行の下に追加）
0 0 * * * ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh >> ~/nas-project-data/insta360-auto-sync/logs/cron.log 2>&1

# 5. 保存して終了
# viの場合: Esc → :wq → Enter
# nanoの場合: Ctrl+X → Y → Enter

# 6. 権限を確認・修正
sudo chmod 600 /var/spool/cron/crontabs/$(whoami)
sudo chown $(whoami):$(whoami) /var/spool/cron/crontabs/$(whoami)

# 7. 確認
crontab -l | grep insta360
```

### 方法2: sudo crontab -e（推奨）

```bash
# NAS側で実行

# 現在のユーザーでcrontabを編集（sudoを使用）
sudo crontab -e -u $(whoami)

# エディタが開いたら、以下の行を追加
0 0 * * * ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh >> ~/nas-project-data/insta360-auto-sync/logs/cron.log 2>&1

# 保存して終了
# viの場合: Esc → :wq → Enter
# nanoの場合: Ctrl+X → Y → Enter

# 確認
crontab -l | grep insta360
```

### 方法3: ホームディレクトリに一時ファイルを作成

```bash
# NAS側で実行

# 1. 既存のcrontabを取得
crontab -l > ~/my_crontab 2>/dev/null || touch ~/my_crontab

# 2. 新しいエントリを追加
cat >> ~/my_crontab << 'EOF'
0 0 * * * ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh >> ~/nas-project-data/insta360-auto-sync/logs/cron.log 2>&1
EOF

# 3. crontabファイルを設定
crontab ~/my_crontab

# 4. 確認
crontab -l | grep insta360

# 5. 一時ファイルを削除
rm ~/my_crontab
```

### 方法4: スクリプトを使用

```bash
# NAS側で実行

cd ~/nas-project/insta360-auto-sync
git pull
chmod +x scripts/add-cron-entry.sh
./scripts/add-cron-entry.sh
```

## 権限の確認と修正

### crontabファイルの権限を確認

```bash
# NAS側で実行

# crontabファイルの権限を確認
ls -la /var/spool/cron/crontabs/$(whoami)

# 権限が正しくない場合、修正
sudo chmod 600 /var/spool/cron/crontabs/$(whoami)
sudo chown $(whoami):$(whoami) /var/spool/cron/crontabs/$(whoami)
```

### crontabディレクトリの権限を確認

```bash
# NAS側で実行

# crontabディレクトリの権限を確認
ls -la /var/spool/cron/crontabs/

# ディレクトリの権限を確認
ls -ld /var/spool/cron/crontabs/
```

## 確認手順

```bash
# NAS側で実行

# 1. crontabの内容を確認
crontab -l

# 2. insta360関連のエントリを確認
crontab -l | grep insta360

# 3. エントリが存在するか確認
crontab -l | grep -q "sync-with-mount-check.sh" && echo "✅ 設定されています" || echo "❌ 設定されていません"

# 4. cronサービスの状態を確認
sudo systemctl status cron
# または
sudo systemctl status crond
```

## トラブルシューティング

### 問題1: まだ権限エラーが発生する

**解決方法**: 
```bash
# crontabファイルを直接編集
sudo vi /var/spool/cron/crontabs/$(whoami)
```

### 問題2: crontabファイルが存在しない

**解決方法**:
```bash
# 空のcrontabファイルを作成
touch ~/my_crontab
crontab ~/my_crontab
```

### 問題3: cronジョブが実行されない

**解決方法**:
```bash
# cronサービスの状態を確認
sudo systemctl status cron

# cronサービスを再起動
sudo systemctl restart cron

# 手動でスクリプトを実行してテスト
~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh
```











