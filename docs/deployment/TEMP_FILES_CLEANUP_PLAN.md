# 一時的なバックアップファイルやテスト用ファイルの整理計画

## 📋 概要

ローカル環境とNAS環境の両方で、一時的なバックアップファイルやテスト用ファイルを確認・整理します。

## 🔍 確認結果

### ローカル環境

#### テスト用ファイル（確認が必要）

- **notion-knowledge-summaries/test_connections.py** - 接続テスト用
- **notion-knowledge-summaries/test_config.py** - 設定テスト用
- **nas-dashboard/scripts/test_monthly_report.py** - 月次レポートテスト用
- **nas-dashboard-monitoring/test_monitoring.py** - 監視テスト用
- **nas-dashboard-monitoring/test_websocket.py** - WebSocketテスト用

#### デバッグ用ファイル（確認が必要）

- **insta360-auto-sync/debug-sync.sh** - 同期デバッグ用
- **insta360-auto-sync/test-sync-after-mount.sh** - マウント後同期テスト用
- **nas-dashboard-monitoring/test-local.sh** - ローカルテスト用

#### アーカイブ（問題なし）

- **docs/archive/backup/** - アーカイブディレクトリ（保持）

### NAS環境

NAS環境でも同様の確認が必要です。

## 🎯 整理方針

### 1. テスト用ファイル

#### 保持するもの
- 継続的に使用するテストファイル
- デプロイメント時に必要なテストファイル

#### 削除または移動するもの
- 一時的なテストファイル
- 使用されていないテストファイル

### 2. デバッグ用ファイル

#### 保持するもの
- トラブルシューティング時に使用するデバッグスクリプト

#### 削除または移動するもの
- 一時的なデバッグファイル
- 使用されていないデバッグファイル

### 3. バックアップファイル

#### 保持するもの
- `.env.restore` - 環境変数のバックアップ（必要）

#### 削除するもの
- 一時的なバックアップファイル（`.backup`, `.bak`, `.old`など）

## 📋 整理手順

### Phase 1: ファイルの確認

各テスト用・デバッグ用ファイルの内容を確認し、必要かどうかを判断します。

### Phase 2: 分類

- **保持**: 継続的に使用するファイル
- **移動**: `docs/archive/`に移動（参照用に保持）
- **削除**: 不要なファイル

### Phase 3: 整理

- 保持するファイルは適切な場所に配置
- 不要なファイルは削除
- `.gitignore`を更新して、一時ファイルを除外

## ✅ 確認スクリプト

`scripts/check-temp-files.sh`を作成しました。このスクリプトで一時的なファイルを確認できます。

### 使用方法

```bash
# ローカル環境で実行
./scripts/check-temp-files.sh

# NAS環境で実行
cd ~/nas-project
./scripts/check-temp-files.sh
```

---

**更新日**: 2025年11月7日

