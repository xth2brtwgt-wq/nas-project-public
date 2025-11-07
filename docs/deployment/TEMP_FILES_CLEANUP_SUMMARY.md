# 一時的なバックアップファイルやテスト用ファイルの整理結果

## 📋 確認結果

### ローカル環境

#### 一時的なバックアップファイル（削除候補）

- **nas-dashboard-monitoring/.env.bak** (1.2K) - 一時的なバックアップファイル
- **nas-dashboard-monitoring/.env.backup2** (1.3K) - 一時的なバックアップファイル

#### テスト用ファイル（確認が必要）

- **notion-knowledge-summaries/test_connections.py** (1.4K) - 接続テスト用（継続使用の可能性）
- **notion-knowledge-summaries/test_config.py** (1.2K) - 設定テスト用（継続使用の可能性）
- **nas-dashboard/scripts/test_monthly_report.py** (3.7K) - 月次レポートテスト用（継続使用の可能性）
- **nas-dashboard-monitoring/test_monitoring.py** (11K) - 監視テスト用（継続使用の可能性）
- **nas-dashboard-monitoring/test_websocket.py** (1.7K) - WebSocketテスト用（継続使用の可能性）
- **nas-dashboard-monitoring/test-local.sh** (3.1K) - ローカルテスト用（継続使用の可能性）
- **insta360-auto-sync/test-sync-after-mount.sh** (1.5K) - マウント後同期テスト用（継続使用の可能性）

#### デバッグ用ファイル（確認が必要）

- **insta360-auto-sync/debug-sync.sh** (1.7K) - 同期デバッグ用（トラブルシューティング時に使用）

### NAS環境

NAS環境でも同様の確認が必要です。

## 🎯 整理方針

### 1. 一時的なバックアップファイル

#### 削除対象
- `.env.bak` - 一時的なバックアップファイル（`.env.restore`があれば不要）
- `.env.backup2` - 一時的なバックアップファイル（`.env.restore`があれば不要）

### 2. テスト用ファイル

#### 保持するもの
- 継続的に使用するテストファイル
- デプロイメント時に必要なテストファイル

#### 移動するもの
- `docs/testing/`に移動（テスト用ファイルの集約）

### 3. デバッグ用ファイル

#### 保持するもの
- トラブルシューティング時に使用するデバッグスクリプト

#### 移動するもの
- `docs/testing/`または`guides/troubleshooting/`に移動

## 📋 整理手順

### Phase 1: 一時的なバックアップファイルの削除

```bash
# ローカル環境で実行
rm -f nas-dashboard-monitoring/.env.bak
rm -f nas-dashboard-monitoring/.env.backup2

# NAS環境でも同様に削除
```

### Phase 2: テスト用ファイルの整理

テスト用ファイルを`docs/testing/`に移動するか、各プロジェクトの`tests/`ディレクトリに整理します。

### Phase 3: デバッグ用ファイルの整理

デバッグ用ファイルを`docs/testing/`または`guides/troubleshooting/`に移動します。

## ✅ 確認スクリプト

`scripts/check-temp-files.sh`を作成しました。このスクリプトで一時的なファイルを確認できます。

---

**更新日**: 2025年11月7日

