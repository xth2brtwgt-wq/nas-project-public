# Insta360自動同期 - マウント問題の診断と修正

## 問題の症状

ログには以下のように表示されるが、実際にはファイルが同期されない：

```
2025-11-04 00:00:24,326 - __main__ - INFO - スケジュール実行を開始します...
```

その後、ファイル検索結果や同期結果のログが表示されない。

## 原因

**docker-compose.ymlがMac側の共有フォルダではなく、NAS上のローカルディレクトリをマウントしていた**

### 修正前（問題あり）
```yaml
volumes:
  - ~/nas-project-data/insta360-auto-sync/source:/source
```

### 修正後（正しい設定）
```yaml
volumes:
  - /mnt/mac-share:/source  # Mac側の共有フォルダマウントポイント
```

## 診断手順

### 1. NAS側でのマウント状態を確認

```bash
# NASにSSH接続後、マウント状態を確認
mount | grep mac-share

# マウントポイントの存在確認
ls -la /mnt/mac-share

# ファイルが存在するか確認
ls -la /mnt/mac-share/
```

**期待される結果**:
- `mount | grep mac-share` でマウント情報が表示される
- `/mnt/mac-share` ディレクトリが存在し、Mac側のファイルが見える

**問題がある場合**:
- マウント情報が表示されない
- ディレクトリが空または存在しない
- "Permission denied" などのエラーが表示される

### 2. コンテナ内でのソースパス確認

```bash
# コンテナ内でソースパスを確認
docker exec -it insta360-auto-sync ls -la /source

# ファイル数確認
docker exec -it insta360-auto-sync find /source -type f | wc -l
```

**期待される結果**:
- Mac側のInsta360ファイルが表示される
- ファイル数が0より大きい

**問題がある場合**:
- ディレクトリが空
- "No such file or directory" エラーが表示される

### 3. Mac側の共有フォルダ確認

Mac側で以下を確認：

```bash
# 共有設定を確認
system_profiler SPNetworkLocationDataType | grep -A 10 "Insta360"

# 共有フォルダの存在確認
ls -la ~/Insta360  # または共有フォルダのパス
```

## 修正手順

### ステップ1: docker-compose.ymlの修正（完了済み）

`docker-compose.yml`を修正して、Mac共有フォルダのマウントポイント（`/mnt/mac-share`）を使用するように変更しました。

### ステップ2: NAS側でMac共有フォルダをマウント

#### 2-1. マウントポイントの作成

```bash
# マウントポイントディレクトリを作成
sudo mkdir -p /mnt/mac-share

# パーミッション設定
sudo chmod 755 /mnt/mac-share
```

#### 2-2. 手動マウント（テスト）

```bash
# 既存のマウントを解除（存在する場合）
sudo umount /mnt/mac-share 2>/dev/null || true

# 手動マウント実行
sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755

# マウント確認
mount | grep mac-share
ls -la /mnt/mac-share
```

#### 2-3. 自動マウント設定（永続化）

```bash
# fstabのバックアップ作成
sudo cp /etc/fstab /etc/fstab.backup

# fstabにマウント設定を追加（既に存在する場合はスキップ）
if ! grep -q "mac-share" /etc/fstab; then
    echo "//YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share cifs username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755 0 0" | sudo tee -a /etc/fstab
fi

# 設定テスト
sudo mount -a

# 確認
mount | grep mac-share
```

### ステップ3: Dockerコンテナの再起動

```bash
# プロジェクトディレクトリに移動（重要: nas-project-dataではなくnas-project）
cd ~/nas-project/insta360-auto-sync

# 最新コードを取得
git pull

# コンテナを再起動
docker-compose down
docker-compose up -d --build

# コンテナ内で確認
docker exec -it insta360-auto-sync ls -la /source
```

### ステップ4: 動作確認

```bash
# テストモードで実行
docker exec insta360-auto-sync python /app/scripts/sync.py --test

# 1回だけ同期を実行
docker exec insta360-auto-sync python /app/scripts/sync.py --once

# ログ確認
docker logs insta360-auto-sync --tail 50
```

## 確認ポイント

### ✅ 正しく設定されている場合

1. **NAS側マウント**:
   ```bash
   mount | grep mac-share
   # 出力例: //YOUR_MAC_IP_ADDRESS/Insta360 on /mnt/mac-share type cifs (...)
   ```

2. **ファイル確認**:
   ```bash
   ls -la /mnt/mac-share
   # Mac側のInsta360ファイルが表示される
   ```

3. **コンテナ内確認**:
   ```bash
   docker exec insta360-auto-sync ls -la /source
   # 同じファイルが表示される
   ```

4. **同期実行**:
   ```bash
   docker exec insta360-auto-sync python /app/scripts/sync.py --once
   # "Insta360ファイルを X 件発見しました" と表示される
   ```

### ❌ 問題がある場合

1. **マウントされていない**:
   - `mount | grep mac-share` で何も表示されない
   - → ステップ2を実行してマウント設定を行う

2. **マウントエラー**:
   - "mount error(13): Permission denied"
   - → Mac側の共有フォルダ設定を確認
   - → パスワードが正しいか確認

3. **コンテナ内でファイルが見えない**:
   - `/mnt/mac-share`にはファイルがあるが、コンテナ内の`/source`が空
   - → コンテナを再起動: `docker-compose restart`

4. **ファイルが見つからない**:
   - マウントは成功しているが、ファイルが見つからない
   - → Mac側の共有フォルダにInsta360ファイルが存在するか確認
   - → ファイルパターン（`VID_*.mp4`, `*.insv`など）が正しいか確認

## トラブルシューティング

### マウントが頻繁に解除される場合

```bash
# マウント状態を確認
mount | grep mac-share

# 再マウント
sudo mount -a

# 自動マウント設定を確認
cat /etc/fstab | grep mac-share
```

### Mac側のIPアドレスが変更された場合

1. `app.json`の`mac.ip_address`を更新
2. `/etc/fstab`のIPアドレスを更新
3. マウントを再実行: `sudo mount -a`

### パスワードが変更された場合

1. `/etc/fstab`のパスワードを更新
2. マウントを再実行: `sudo mount -a`

## 関連ドキュメント

- [MOUNT_SETUP.md](MOUNT_SETUP.md) - マウント設定の詳細手順
- [README.md](README.md) - システム全体の説明
- [EMERGENCY_FIX.md](EMERGENCY_FIX.md) - 緊急時の修正手順

## 更新履歴

- 2025-11-04: マウント問題の診断と修正手順を追加

