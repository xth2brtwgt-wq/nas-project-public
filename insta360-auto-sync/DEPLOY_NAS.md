# Insta360自動同期 - NASデプロイ手順

## デプロイ手順（NAS側で実行）

### 1. 最新の変更を取得
```bash
cd ~/nas-project/insta360-auto-sync
git pull origin main
```

### 2. デプロイスクリプトを実行
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. コンテナの再構築（Dockerfile変更のため）
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### 4. 動作確認
```bash
# コンテナが起動しているか確認
docker ps | grep insta360-auto-sync

# コンテナのログ確認（スケジューラーのログが出ないことを確認）
docker compose logs insta360-auto-sync

# cronジョブが設定されているか確認
crontab -l | grep insta360
```

## 変更内容

- **Dockerfile**: スケジューラーモードを無効化（`CMD ["tail", "-f", "/dev/null"]`）
- **実行方式**: cronジョブ方式（マウントチェック付き）のみで実行
- **重複実行問題**: 修正完了

## 注意事項

1. **コンテナ再構築が必要**: Dockerfileを変更したため、コンテナを再構築する必要があります
2. **cronジョブの確認**: cronジョブが正しく設定されていることを確認してください
3. **マウントチェック**: 同期処理実行前にマウント状態が確認されます

