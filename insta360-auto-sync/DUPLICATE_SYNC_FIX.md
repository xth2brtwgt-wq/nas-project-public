# Insta360自動同期 - 重複実行問題の修正

## 問題の概要

NAS上で自動同期が2回処理されていた問題を修正しました。

## 問題の原因

2つの実行方法が同時に動作していたため、同じ時間（毎日00:00）に2回同期処理が実行されていました：

1. **DockerfileのCMD**: `CMD ["python", "scripts/sync.py"]` 
   - スケジューラーモードで毎日00:00に自動実行
   - コンテナ起動時にスケジューラーが開始される

2. **cronジョブ**: `sync-with-mount-check.sh`
   - 毎日00:00にcronジョブから実行
   - マウントチェック付きで同期処理を実行

## 修正内容

### 1. Dockerfileの修正

**変更前:**
```dockerfile
# スケジューラーモードで起動（毎日00:00に自動実行）
CMD ["python", "scripts/sync.py"]
```

**変更後:**
```dockerfile
# コンテナを常時起動させる（cronジョブから実行されるため、スケジューラーは無効化）
# cronジョブが同期処理を実行するため、コンテナは待機状態で起動
CMD ["tail", "-f", "/dev/null"]
```

### 2. 実行方式の統一

**推奨方式**: cronジョブ方式（マウントチェック付き）
- 同期処理実行前にマウント状態を確認・再マウント
- 普段はマウントされていなくてもOK
- 必要なときだけマウントを確認・実行

**無効化**: Dockerfileのスケジューラーモード
- コンテナは常時起動しているが、スケジューラーは動作しない
- cronジョブから同期処理を実行する

## 修正後の動作

1. **コンテナ起動**: コンテナは常時起動（待機状態）
2. **cronジョブ実行**: 毎日00:00に`sync-with-mount-check.sh`が実行
3. **マウントチェック**: 同期処理実行前にマウント状態を確認・再マウント
4. **同期処理実行**: `docker exec`でコンテナ内の`sync.py --once`を実行
5. **結果**: 1回だけ同期処理が実行される

## 修正日時

2025年10月27日

## 確認方法

### 1. コンテナの状態確認
```bash
# コンテナが起動しているか確認
docker ps | grep insta360-auto-sync

# コンテナのログ確認（スケジューラーのログが出ないことを確認）
docker-compose logs insta360-auto-sync
```

### 2. cronジョブの確認
```bash
# cronジョブが設定されているか確認
crontab -l | grep insta360

# cronログの確認
tail -f ~/nas-project-data/insta360-auto-sync/logs/cron.log
```

### 3. 同期処理の確認
```bash
# 手動で同期処理を実行してテスト
docker exec -it insta360-auto-sync python /app/scripts/sync.py --once
```

## 注意事項

1. **コンテナ再構築が必要**: Dockerfileを変更したため、コンテナを再構築する必要があります
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

2. **cronジョブの設定確認**: cronジョブが正しく設定されていることを確認してください
   ```bash
   crontab -l | grep insta360
   ```

3. **マウントチェック**: 同期処理実行前にマウント状態が確認されるため、マウントが解除されていても自動的に再マウントされます

## 関連ファイル

- `Dockerfile`: コンテナの起動コマンド
- `docker-compose.yml`: コンテナ設定
- `scripts/sync-with-mount-check.sh`: cronジョブから実行されるラッパースクリプト
- `scripts/sync.py`: 実際の同期処理スクリプト

## 参考ドキュメント

- [MOUNT_SETUP.md](MOUNT_SETUP.md): マウント設定の詳細
- [SYNC_WITH_MOUNT_CHECK.md](SYNC_WITH_MOUNT_CHECK.md): マウントチェック付き同期処理の詳細
- [CRON_SETUP_MANUAL.md](CRON_SETUP_MANUAL.md): cronジョブの手動設定方法



