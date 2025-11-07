# Insta360自動同期 - マウント接続エラー修正ガイド

## 問題の症状

```
mount error(111): could not connect to YOUR_MAC_IP_ADDRESS
Unable to find suitable address.
```

## 原因

Mac側のファイル共有（SMB）が正しく設定されていないか、接続できない状態です。

## 解決手順

### ステップ1: Mac側のIPアドレスを確認

```bash
# Mac側で実行
ifconfig | grep "inet " | grep -v 127.0.0.1
# または
ipconfig getifaddr en0
```

**確認**: IPアドレスが `YOUR_MAC_IP_ADDRESS` であることを確認してください。

### ステップ2: Mac側でファイル共有を有効化

1. **システム設定を開く**
   - アップルメニュー > システム設定

2. **共有を開く**
   - システム設定 > 一般 > 共有

3. **ファイル共有を有効化**
   - 「ファイル共有」をオンにする

4. **共有フォルダを追加**
   - 「共有フォルダ」セクションの「+」ボタンをクリック
   - `/Users/Yoshi/Movies/Insta360` を選択して追加
   - ユーザー（Admin）に読み書き権限を設定

5. **オプション設定（重要）**
   - 「オプション」ボタンをクリック
   - **「SMBを使ってファイルやフォルダを共有」をチェック**
   - **「SMBファイル共有をオンにする」をチェック**
   - 共有するユーザー（Admin）を選択
   - 「完了」をクリック

### ステップ3: Mac側でSMBサービスの状態を確認

```bash
# Mac側で実行
# 1. SMBサービスの状態を確認
sudo launchctl list | grep smb

# 2. SMBポート（445）が開いているか確認
netstat -an | grep 445

# 3. 共有フォルダの一覧を確認
smbutil statshares //localhost
```

### ステップ4: Mac側のファイアウォール設定を確認

1. **システム設定 > ネットワーク > ファイアウォール**
   - ファイアウォールがオンの場合、「オプション」をクリック
   - 「ファイル共有」が許可されているか確認
   - 許可されていない場合は追加

### ステップ5: NAS側からMac側への接続テスト

```bash
# NAS側で実行
# 1. Mac側への接続確認
ping -c 2 YOUR_MAC_IP_ADDRESS

# 2. SMBポート（445）への接続確認
telnet YOUR_MAC_IP_ADDRESS 445
# または
nc -zv YOUR_MAC_IP_ADDRESS 445

# 3. SMB共有の一覧を確認
smbclient -L //YOUR_MAC_IP_ADDRESS -U YOUR_USERNAME%YOUR_PASSWORD
```

### ステップ6: NAS側でマウントを再実行

```bash
# NAS側で実行
# 1. 既存のマウントを解除
sudo umount /mnt/mac-share 2>/dev/null || true

# 2. マウントを再実行（詳細なログを出力）
sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755,vers=3.0

# 3. マウント確認
mount | grep mac-share

# 4. ファイル確認
ls -la /mnt/mac-share
```

**注意**: SMBバージョンが3.0の場合、`vers=3.0` オプションが必要な場合があります。

### ステップ7: 別のSMBバージョンを試す

```bash
# NAS側で実行
# SMB 2.0を試す
sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755,vers=2.0

# または SMB 1.0を試す（推奨しない）
sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755,vers=1.0
```

## トラブルシューティング

### 接続できない場合

1. **Mac側のIPアドレスを再確認**
   ```bash
   # Mac側で実行
   ifconfig | grep "inet "
   ```

2. **Mac側のファイル共有が有効になっているか確認**
   - システム設定 > 一般 > 共有 > ファイル共有
   - 「ファイル共有」がオンになっているか確認

3. **Mac側のSMBサービスが起動しているか確認**
   ```bash
   # Mac側で実行
   sudo launchctl list | grep smb
   ```

### 認証エラーが発生する場合

1. **Mac側のユーザー名とパスワードを確認**
   - ユーザー名: `Admin`
   - パスワード: `0828`

2. **Mac側で共有フォルダの権限を確認**
   - システム設定 > 一般 > 共有 > ファイル共有 > 共有フォルダ
   - `/Users/Yoshi/Movies/Insta360` が共有されているか確認
   - ユーザー（Admin）に読み書き権限があるか確認

### マウントは成功するがファイルが見えない場合

1. **Mac側の共有フォルダの内容を確認**
   ```bash
   # Mac側で実行
   ls -la /Users/Yoshi/Movies/Insta360/
   ```

2. **NAS側のマウントポイントを確認**
   ```bash
   # NAS側で実行
   ls -la /mnt/mac-share
   ```

3. **コンテナ内のソースパスを確認**
   ```bash
   # NAS側で実行
   docker exec insta360-auto-sync ls -la /source
   ```

## 確認ポイント

✅ Mac側のIPアドレスが `YOUR_MAC_IP_ADDRESS` である  
✅ Mac側のファイル共有が有効になっている  
✅ Mac側のSMB共有が有効になっている  
✅ Mac側の共有フォルダ `/Users/Yoshi/Movies/Insta360` が共有されている  
✅ NAS側からMac側への接続が可能である  
✅ NAS側でマウントが成功している  
✅ `/mnt/mac-share` にファイルが表示される  

## 関連ドキュメント

- [MOUNT_SETUP.md](MOUNT_SETUP.md) - マウント設定の詳細手順
- [MOUNT_TROUBLESHOOTING.md](MOUNT_TROUBLESHOOTING.md) - マウント問題の診断と修正
- [MAC_SHARE_SETUP.md](MAC_SHARE_SETUP.md) - Mac側共有フォルダ設定ガイド

