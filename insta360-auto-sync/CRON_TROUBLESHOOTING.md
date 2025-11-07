# Insta360自動同期 - cronジョブ設定のトラブルシューティング

## 問題: crontab -eで編集しても反映されない

### 原因と対処法

#### 1. nanoエディタでの保存操作

nanoエディタで編集した場合、以下の手順で**必ず保存**してください：

```
1. ファイルを編集
2. Ctrl+X を押す（保存して終了）
3. Y を押す（保存するか確認）
4. Enter を押す（ファイル名を確認して保存）
```

**注意**: Ctrl+Xだけで保存されない場合があります。必ずYを押してEnterを押してください。

#### 2. 保存後の確認

```bash
# NAS側で実行

# 1. 保存直後にcrontabの内容を確認
crontab -l

# 2. insta360関連のエントリが含まれているか確認
crontab -l | grep insta360

# 3. エントリが表示されない場合、再度編集
crontab -e
```

#### 3. 別のユーザーのcrontabを編集している可能性

```bash
# NAS側で実行

# 現在のユーザーを確認
whoami

# 現在のユーザーのcrontabを確認
crontab -l

# 別のユーザーのcrontabを編集している場合、sudoが必要（通常は不要）
# sudo crontab -e -u YOUR_USERNAME
```

#### 4. 一時ファイルの権限問題

```bash
# NAS側で実行

# 一時ディレクトリの権限を確認
ls -la /tmp/ | grep crontab

# 権限エラーが発生する場合、環境変数を確認
echo $TMPDIR
echo $TMP
```

#### 5. 代替方法: 一時ファイルを使用

```bash
# NAS側で実行

# 1. 現在のcrontabをバックアップ
crontab -l > /tmp/crontab.backup

# 2. 新しいエントリを追加したファイルを作成
cat > /tmp/crontab.new << 'EOF'
0 0 * * * "~/.acme.sh"/acme.sh --cron --home "~/.acme.sh" > /dev/null 2>&1

0 3 * * * sudo ~/bin/renew-cert-and-reload.sh >> ~/cert-renewal.log 2>&1

0 0 * * * ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh >> ~/nas-project-data/insta360-auto-sync/logs/cron.log 2>&1
EOF

# 3. crontabファイルを設定
crontab /tmp/crontab.new

# 4. 確認
crontab -l | grep insta360

# 5. 一時ファイルを削除
rm -f /tmp/crontab.new
```

#### 6. 直接crontabファイルを編集（非推奨）

```bash
# NAS側で実行（注意: 通常はcrontab -eを使用）

# crontabファイルの場所を確認
ls -la /var/spool/cron/crontabs/$(whoami)

# 直接編集（権限が必要な場合がある）
sudo vi /var/spool/cron/crontabs/$(whoami)
```

### 確認方法

#### 1. crontabの内容を確認

```bash
# NAS側で実行

# すべてのcronジョブを表示
crontab -l

# insta360関連のエントリを確認
crontab -l | grep insta360

# エントリが存在するか確認
crontab -l | grep -q "sync-with-mount-check.sh" && echo "✅ 設定されています" || echo "❌ 設定されていません"
```

#### 2. cronサービスの状態を確認

```bash
# NAS側で実行

# cronサービスの状態を確認
sudo systemctl status cron
# または
sudo systemctl status crond

# cronログを確認
sudo journalctl -u cron -n 50
```

#### 3. 手動実行でテスト

```bash
# NAS側で実行

# スクリプトを手動実行してテスト
~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh
```

### 推奨される設定方法

#### 方法1: crontab -e（推奨）

```bash
# NAS側で実行

# 1. crontabを編集
crontab -e

# 2. 以下の行を追加（既存の行の下に追加）
0 0 * * * ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh >> ~/nas-project-data/insta360-auto-sync/logs/cron.log 2>&1

# 3. 保存（nanoの場合: Ctrl+X → Y → Enter）
# 4. 確認
crontab -l | grep insta360
```

#### 方法2: 一時ファイルを使用

```bash
# NAS側で実行

# 既存のcrontabを取得
crontab -l > /tmp/my_crontab

# 新しいエントリを追加
echo "0 0 * * * ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh >> ~/nas-project-data/insta360-auto-sync/logs/cron.log 2>&1" >> /tmp/my_crontab

# crontabファイルを設定
crontab /tmp/my_crontab

# 確認
crontab -l | grep insta360

# 一時ファイルを削除
rm /tmp/my_crontab
```

### よくある問題と解決方法

#### 問題1: nanoで保存しても反映されない

**解決方法**: 
- Ctrl+X → **Y** → Enter の順序を守る
- 保存後、`crontab -l`で確認する

#### 問題2: 権限エラーが発生する

**解決方法**:
- `sudo`を使わずに実行する（ユーザー自身のcrontabを編集）
- 一時ファイルを`/tmp`ディレクトリに作成する

#### 問題3: エントリが重複する

**解決方法**:
```bash
# 既存のinsta360関連のエントリを削除してから追加
(crontab -l 2>/dev/null | grep -v "insta360-auto-sync" | grep -v "sync-with-mount-check.sh"; \
 echo "0 0 * * * ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh >> ~/nas-project-data/insta360-auto-sync/logs/cron.log 2>&1") | crontab -
```

### 最終確認

```bash
# NAS側で実行

# 1. crontabの内容を確認
crontab -l

# 2. insta360関連のエントリを確認
crontab -l | grep insta360

# 3. スクリプトが存在し、実行権限があるか確認
ls -la ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh

# 4. 手動実行でテスト
~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh
```











