# Insta360自動同期システム - 緊急修正手順

## 概要
Insta360自動同期システムに問題が発生した際の緊急修正手順です。

## 緊急修正スクリプト
`scripts/fix-insta360-schedule.sh` を使用してシステムを完全に再構築します。

## 使用場面
- スケジュール実行が停止した場合
- ファイル同期にエラーが発生した場合
- コンテナが正常に起動しない場合
- 設定ファイルに問題がある場合
- **ログが重複出力される場合**（v1.0.1で修正済み）

## 実行手順

### 1. 事前確認
```bash
# 現在の状態を確認
docker compose ps
docker compose logs
```

### 2. 緊急修正スクリプト実行
```bash
# プロジェクトディレクトリで実行
cd /path/to/insta360-auto-sync
./scripts/fix-insta360-schedule.sh
```

### 3. 修正内容
スクリプトは以下の処理を自動実行します：

1. **バックアップ作成**
   - `scripts/sync.py` → `scripts/sync.py.backup.YYYYMMDD_HHMMSS`
   - `docker-compose.yml` → `docker-compose.yml.backup.YYYYMMDD_HHMMSS`

2. **sync.py完全書き換え**
   - 新しい同期ロジックで置き換え
   - エラーハンドリング強化
   - **ログ出力改善**（v1.0.1で重複ログ問題を修正）

3. **docker-compose.yml修正**
   - コンテナ設定を最新化
   - 環境変数設定を最適化

4. **コンテナ再起動**
   - 既存コンテナを停止
   - 新しい設定で再構築
   - 自動起動

### 4. 修正後確認
```bash
# コンテナ状態確認
docker compose ps

# ログ確認
docker compose logs -f

# 手動同期テスト
docker compose exec insta360-auto-sync python scripts/sync.py --test
```

## 注意事項

### ⚠️ 重要な注意点
- **実行前に必ずバックアップが作成されます**
- **既存の設定は完全に置き換えられます**
- **データは保持されますが、設定は初期化されます**

### 🔄 復元方法
修正前の状態に戻したい場合：
```bash
# バックアップファイルを復元
cp scripts/sync.py.backup.YYYYMMDD_HHMMSS scripts/sync.py
cp docker-compose.yml.backup.YYYYMMDD_HHMMSS docker-compose.yml

# コンテナ再起動
docker compose down
docker compose up -d
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. スクリプト実行権限エラー
```bash
chmod +x scripts/fix-insta360-schedule.sh
```

#### 2. Docker権限エラー
```bash
sudo docker compose down
sudo docker compose build
sudo docker compose up -d
```

#### 3. ログファイル確認
```bash
# 詳細ログを確認
tail -f logs/insta360_sync.log
```

## 連絡先
問題が解決しない場合は、システム管理者に連絡してください。

---
**最終更新**: 2025年10月27日  
**バージョン**: 1.0.1
