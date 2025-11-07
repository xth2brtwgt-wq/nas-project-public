# Insta360自動同期 - UGreen NASスケジューラー統合ガイド

## 概要

UGreen NASの組み込みスケジューラー機能を使用して、Insta360自動同期を実行する方法を説明します。

## UGreen NASスケジューラー機能について

UGreen NASには、Web UIから設定できるタスクスケジューラー機能があります。この機能を使用することで、cronジョブの代わりに、またはcronジョブと併用してスケジュール実行を行うことができます。

### メリット

- **Web UIから設定可能**: コマンドライン操作が不要
- **視覚的な管理**: スケジュールを一覧で確認・管理できる
- **エラーハンドリング**: 実行結果をWeb UIで確認できる
- **バックアップ**: 設定がNASの設定として保存される

### デメリット

- **cronジョブとの併用注意**: 重複実行に注意が必要
- **NAS再起動時の動作**: NASの設定に依存する

## 設定手順

### 1. UGreen NASのWeb UIにアクセス

1. ブラウザでUGreen NASの管理画面にアクセス
2. 「タスクスケジューラー」または「スケジューラー」メニューを開く
3. 新しいタスクを作成

### 2. タスクの設定

以下の設定を行います：

#### 基本設定

- **タスク名**: `Insta360自動同期`
- **説明**: `Insta360ファイルの自動同期処理`

#### スケジュール設定

- **実行タイプ**: `定期実行` または `cron形式`
- **実行時間**: `毎日 00:00` または `0 0 * * *` (cron形式)

#### 実行コマンド

- **コマンド**: `/bin/bash`
- **引数**: `~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh`

または、フルパスで指定：

```bash
/bin/bash ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh
```

#### ログ設定

- **ログ出力先**: `~/nas-project-data/insta360-auto-sync/logs/ugreen_scheduler.log`
- **エラー出力**: 標準エラー出力もログに記録

### 3. 既存のcronジョブとの関係

#### オプション1: UGreenスケジューラーのみ使用（推奨）

cronジョブを無効化して、UGreenスケジューラーのみを使用します。

```bash
# NAS側で実行

# 既存のcronジョブを確認
crontab -l | grep insta360

# cronジョブを削除
(crontab -l 2>/dev/null | grep -v "insta360-auto-sync" | grep -v "sync-with-mount-check.sh") | crontab -

# 確認
crontab -l | grep insta360
```

#### オプション2: cronジョブと併用（非推奨）

両方を有効にすると、重複実行のリスクがあります。併用する場合は、実行時間をずらすか、重複防止機能を実装してください。

### 4. 動作確認

#### 手動実行でテスト

```bash
# NAS側で実行

# スクリプトを手動実行
~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh

# ログを確認
tail -f ~/nas-project-data/insta360-auto-sync/logs/ugreen_scheduler.log
```

#### UGreenスケジューラーから実行

1. Web UIでタスクを選択
2. 「今すぐ実行」または「テスト実行」をクリック
3. 実行結果を確認

## トラブルシューティング

### 問題1: タスクが実行されない

**確認事項:**

1. **スクリプトの実行権限**
   ```bash
   chmod +x ~/nas-project/insta360-auto-sync/scripts/sync-with-mount-check.sh
   ```

2. **パスの確認**
   - フルパスを使用しているか確認
   - 相対パスの場合は、作業ディレクトリを確認

3. **ログの確認**
   ```bash
   # UGreenスケジューラーのログを確認
   tail -f ~/nas-project-data/insta360-auto-sync/logs/ugreen_scheduler.log
   
   # システムログを確認
   sudo journalctl -n 50 | grep insta360
   ```

### 問題2: マウントに失敗する

**確認事項:**

1. **Mac側の共有設定**
   - Mac側で「システム環境設定 > 共有 > ファイル共有」が有効か確認
   - 共有名が「Insta360」になっているか確認
   - Mac側のIPアドレスが正しいか確認（`YOUR_MAC_IP_ADDRESS`）

2. **マウントポイントの確認**
   ```bash
   # マウント状態を確認
   mount | grep mac-share
   
   # 手動でマウントを試みる
   sudo mount -t cifs //YOUR_MAC_IP_ADDRESS/Insta360 /mnt/mac-share -o username=YOUR_USERNAME,password=YOUR_PASSWORD,uid=1000,gid=1000,iocharset=utf8,file_mode=0755,dir_mode=0755
   ```

### 問題3: コンテナが実行されていない

**確認事項:**

1. **コンテナの状態**
   ```bash
   # コンテナの状態を確認
   docker ps | grep insta360-auto-sync
   
   # コンテナが停止している場合は起動
   cd ~/nas-project/insta360-auto-sync
   docker compose up -d
   ```

2. **コンテナのログ**
   ```bash
   # コンテナのログを確認
   docker logs insta360-auto-sync
   ```

## cronジョブからUGreenスケジューラーへの移行手順

### ステップ1: 既存のcronジョブを確認

```bash
# NAS側で実行

# 現在のcronジョブを確認
crontab -l | grep insta360
```

### ステップ2: UGreenスケジューラーでタスクを作成

上記の「設定手順」を参照して、UGreenスケジューラーでタスクを作成します。

### ステップ3: 動作確認

UGreenスケジューラーから手動実行して、正常に動作することを確認します。

### ステップ4: cronジョブを無効化

```bash
# NAS側で実行

# cronジョブを削除
(crontab -l 2>/dev/null | grep -v "insta360-auto-sync" | grep -v "sync-with-mount-check.sh") | crontab -

# 確認
crontab -l | grep insta360
```

### ステップ5: 定期実行の確認

次の実行時刻まで待って、正常に実行されることを確認します。

## 比較: cronジョブ vs UGreenスケジューラー

| 項目 | cronジョブ | UGreenスケジューラー |
|------|-----------|---------------------|
| 設定方法 | コマンドライン | Web UI |
| 管理のしやすさ | 中 | 高 |
| ログ確認 | コマンドライン | Web UI + コマンドライン |
| バックアップ | 手動 | 自動（NAS設定） |
| 柔軟性 | 高（cron形式） | 中（UI制限） |
| デバッグ | コマンドライン | Web UI + コマンドライン |

## 推奨事項

### 推奨: UGreenスケジューラーの使用

以下の場合、UGreenスケジューラーの使用を推奨します：

- Web UIから管理したい場合
- 複数のタスクを視覚的に管理したい場合
- NASの設定としてバックアップしたい場合

### 推奨: cronジョブの継続使用

以下の場合、cronジョブの継続使用を推奨します：

- 複雑なcron式を使用したい場合
- コマンドラインでの管理を好む場合
- 既存の設定を変更したくない場合

## 注意事項

1. **重複実行の防止**: cronジョブとUGreenスケジューラーを併用する場合は、重複実行に注意してください。

2. **パスの指定**: UGreenスケジューラーでスクリプトを実行する場合、フルパスを使用してください。

3. **実行権限**: スクリプトに実行権限があることを確認してください。

4. **ログの管理**: UGreenスケジューラーのログは、定期的にローテーションすることを推奨します。

## 関連ファイル

- `scripts/sync-with-mount-check.sh`: マウントチェック付きラッパースクリプト
- `scripts/sync.py`: 同期処理メインスクリプト
- `SYNC_WITH_MOUNT_CHECK.md`: マウントチェック設定ガイド
- `CRON_SETUP_MANUAL.md`: cronジョブ手動設定ガイド

## 参考リンク

- [UGreen NAS サポートセンター](https://support.ugnas.com/knowledgecenter/)
- [UGreen NAS タスクスケジューラー設定](https://support.ugnas.com/knowledgecenter/#/detail/eyJpZCI6MzgyNCwiYXJ0aWNsZUluZm9JZCI6NDc2LCJsYW5ndWFnZSI6ImphLUpQIiwiY2xpZW50VHlwZSI6IlBDIn0=)

