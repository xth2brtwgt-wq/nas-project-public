# Insta360自動同期 - 手動実行ガイド

## 概要
NAS側でInsta360自動同期処理を手動で実行する方法を説明します。

## 手動実行方法

### 1. テストモード（設定確認のみ）

設定とマウント状態を確認します（実際の同期は行いません）：

```bash
docker exec insta360-auto-sync python /app/scripts/sync.py --test
```

**出力例**:
```
テストモード: 設定確認
ソースパス: /source
転送先パス: /volume2/data/insta360
ファイルパターン: ['VID_*.mp4', '*.insv', '*.insp', '*.jpg', '*.dng', '*.raw']
ソースファイル削除: False
空ディレクトリ削除: True
通知先メール: nas.system.0828@gmail.com

=== マウント状態の確認 ===
✅ ソースパスは存在します: /source
   ディレクトリ内のエントリ数: 5

メール接続テスト中...
メール接続テスト: 成功
```

### 2. 1回だけ同期実行（推奨）

実際の同期処理を1回だけ実行します：

```bash
docker exec insta360-auto-sync python /app/scripts/sync.py --once
```

**出力例**:
```
2025-11-04 12:00:00,000 - __main__ - INFO - Insta360ファイル同期を開始します
2025-11-04 12:00:00,100 - utils.file_utils - INFO - Insta360ファイルを 3 件発見しました
2025-11-04 12:00:00,200 - __main__ - INFO - 転送対象ファイル: 3件
2025-11-04 12:00:05,000 - __main__ - INFO - ファイルコピー完了: VID_20231104_120000.mp4 （元ファイル保持）
2025-11-04 12:00:10,000 - __main__ - INFO - Insta360ファイル同期が完了しました
同期完了: 成功 3件, スキップ 0件, 失敗 0件
総容量: 1.23 GB
実行時間: 10.45秒
```

### 3. 手動同期スクリプトを使用

専用の手動同期スクリプトを使用する場合：

```bash
docker exec insta360-auto-sync python /app/scripts/manual_sync.py
```

## 実行前の確認事項

### マウント状態の確認

NAS側で以下を実行してマウント状態を確認：

```bash
# マウント状態確認
mount | grep mac-share

# ファイル確認
ls -la /mnt/mac-share

# コンテナ内で確認
docker exec insta360-auto-sync ls -la /source
```

### コンテナの状態確認

```bash
# コンテナの状態確認
docker ps | grep insta360-auto-sync

# ログ確認
docker logs insta360-auto-sync --tail 50
```

## ログの確認

### リアルタイムログ

```bash
# リアルタイムでログを確認
docker logs -f insta360-auto-sync
```

### ログファイルの確認

```bash
# コンテナ内のログファイルを確認
docker exec insta360-auto-sync tail -f /app/logs/insta360_sync.log

# または、ホスト側のログディレクトリを確認
tail -f ~/nas-project-data/insta360-auto-sync/logs/insta360_sync.log
```

## デプロイ先の確認

**重要**: 
- プロジェクトコードのデプロイ先: `~/nas-project/insta360-auto-sync`（Gitリポジトリ）
- データディレクトリ: `~/nas-project-data/insta360-auto-sync/`（ログ、転送先ファイルなど）

デプロイ時は `~/nas-project/insta360-auto-sync` で実行してください。

## トラブルシューティング

### エラー: "ソースパスが存在しません"

**原因**: Mac共有フォルダがマウントされていない

**対処法**:
```bash
# NAS側でマウントを確認
mount | grep mac-share

# マウントされていない場合は、マウントを実行
sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755
```

### エラー: "ファイル検索エラー"

**原因**: マウントはされているが、アクセス権限の問題

**対処法**:
```bash
# マウントポイントの権限を確認
ls -la /mnt/mac-share

# コンテナ内で確認
docker exec insta360-auto-sync ls -la /source
```

### エラー: "転送対象のInsta360ファイルは見つかりませんでした"

**原因**: 
- Mac側の共有フォルダにファイルが存在しない
- ファイルパターンに一致するファイルがない

**対処法**:
```bash
# Mac側の共有フォルダを確認
# Mac側で確認: ls -la ~/Insta360

# コンテナ内で確認
docker exec insta360-auto-sync find /source -type f
```

## 実行例

### 完全な実行フロー

```bash
# 1. コンテナの状態確認
docker ps | grep insta360-auto-sync

# 2. テストモードで設定確認
docker exec insta360-auto-sync python /app/scripts/sync.py --test

# 3. マウント状態確認
mount | grep mac-share
docker exec insta360-auto-sync ls -la /source

# 4. 実際に同期を実行
docker exec insta360-auto-sync python /app/scripts/sync.py --once

# 5. ログ確認
docker logs insta360-auto-sync --tail 50
```

## 注意事項

1. **手動実行はスケジュール実行に影響しません**
   - `--once`オプションで実行しても、スケジュール実行は継続します

2. **重複実行を避ける**
   - スケジュール実行中に手動実行しても問題ありませんが、同じファイルが重複処理される可能性があります（スキップ機能により通常は問題ありません）

3. **ログの確認**
   - 手動実行後は必ずログを確認して、正常に処理されたことを確認してください

## 関連ドキュメント

- [MOUNT_SETUP.md](MOUNT_SETUP.md) - マウント設定手順
- [MOUNT_TROUBLESHOOTING.md](MOUNT_TROUBLESHOOTING.md) - マウント問題の診断と修正
- [README.md](README.md) - システム全体の説明

