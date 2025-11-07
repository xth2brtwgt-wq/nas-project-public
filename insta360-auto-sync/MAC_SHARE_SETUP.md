# Insta360自動同期 - Mac側共有フォルダ設定ガイド

## 問題の状況

- NAS側のマウントポイント `/mnt/mac-share` は空（ファイルが存在しない）
- Mac側の共有フォルダ `~/Insta360` が存在しない

## 解決手順

### ステップ1: Mac側で共有フォルダを確認

```bash
# Mac側で実行
# 1. 共有フォルダのパスを確認
ls -la /Users/Yoshi/Movies/Insta360/

# 2. ファイルが存在するか確認
ls -la /Users/Yoshi/Movies/Insta360/
```

**注意**: Mac側のローカルパスは `/Users/Yoshi/Movies/Insta360/` です。

### ステップ2: Mac側でファイル共有を有効化

1. **システム設定を開く**
   - アップルメニュー > システム設定

2. **共有を開く**
   - システム設定 > 一般 > 共有

3. **ファイル共有を有効化**
   - 「ファイル共有」をオンにする

4. **共有フォルダを追加**
   - 「共有フォルダ」セクションの「+」ボタンをクリック
   - `/Users/Yoshi/Movies/Insta360/` を選択して追加

5. **オプション設定**
   - 「オプション」ボタンをクリック
   - 「SMBを使ってファイルやフォルダを共有」をチェック
   - 「共有フォルダ」で `Insta360` フォルダを選択
   - 共有するユーザー（Admin）を選択し、読み書き権限を設定

### ステップ3: Mac側のIPアドレスと共有フォルダ名を確認

```bash
# Mac側で実行
# 1. IPアドレスを確認
ifconfig | grep "inet " | grep -v 127.0.0.1

# 2. 共有フォルダの確認
smbutil statshares //localhost

# または
netstat -an | grep 445
```

### ステップ4: NAS側でマウントを再実行

```bash
# NAS側で実行
# 1. 既存のマウントを解除
sudo umount /mnt/mac-share 2>/dev/null || true

# 2. マウントを再実行
sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755

# 3. マウント確認
mount | grep mac-share

# 4. ファイル確認
ls -la /mnt/mac-share
```

### ステップ5: テストファイルを配置（オプション）

```bash
# Mac側で実行
# テストファイルを作成（既にファイルがある場合は不要）
echo "test" > /Users/Yoshi/Movies/Insta360/test.txt

# NAS側で確認
ls -la /mnt/mac-share
```

### ステップ6: 自動マウント設定（永続化）

```bash
# NAS側で実行
# fstabに設定を追加（既に存在する場合はスキップ）
if ! grep -q "mac-share" /etc/fstab; then
    echo "//YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share cifs username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755 0 0" | sudo tee -a /etc/fstab
fi

# 設定テスト
sudo mount -a

# 確認
mount | grep mac-share
```

### ステップ7: Dockerコンテナを再起動

```bash
# NAS側で実行
cd ~/nas-project/insta360-auto-sync
docker-compose restart

# コンテナ内で確認
docker exec insta360-auto-sync ls -la /source
```

## トラブルシューティング

### 共有フォルダが見つからない場合

```bash
# Mac側で実行
# 1. 共有フォルダの一覧を確認
smbutil statshares //localhost

# 2. 共有フォルダ名を確認
# システム設定 > 一般 > 共有 > ファイル共有 > 共有フォルダ
```

### マウントエラーが発生する場合

```bash
# NAS側で実行
# 1. Mac側への接続を確認
ping -c 2 YOUR_MAC_IP_ADDRESS

# 2. SMBポートを確認
telnet YOUR_MAC_IP_ADDRESS 445

# 3. マウントエラーの詳細を確認
sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755 -v
```

### パスワードが正しくない場合

```bash
# NAS側で実行
# パスワードを確認して、正しいパスワードでマウント
sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=正しいパスワード,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755
```

## 確認ポイント

✅ Mac側の共有フォルダ `/Users/Yoshi/Movies/Insta360/` が存在する  
✅ ファイル共有が有効になっている  
✅ SMB共有が有効になっている  
✅ NAS側でマウントが成功している  
✅ `/mnt/mac-share` にファイルが表示される  
✅ コンテナ内の `/source` にファイルが表示される  

## 関連ドキュメント

- [MOUNT_SETUP.md](MOUNT_SETUP.md) - マウント設定の詳細手順
- [MOUNT_TROUBLESHOOTING.md](MOUNT_TROUBLESHOOTING.md) - マウント問題の診断と修正
- [MANUAL_SYNC_GUIDE.md](MANUAL_SYNC_GUIDE.md) - 手動実行ガイド

