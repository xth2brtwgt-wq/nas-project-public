# データベース肥大化対策実装レポート

## 概要

NAS環境で稼働する各プロジェクトのデータベース肥大化を防ぐため、包括的な対策を実装しました。本レポートでは、実装内容、技術的詳細、および各プロジェクトでの適用状況をまとめます。

## 実装日時

- **実装期間**: 2025年10月29日
- **対象プロジェクト**: 4プロジェクト
- **実装者**: AI Assistant

## 実装内容

### 1. 共通機能

#### 1.1 データベース管理API
以下のRESTful APIエンドポイントを各プロジェクトに実装：

- `GET /api/database/stats` - データベース統計情報取得
- `GET /api/database/size` - データベースサイズチェック
- `GET /api/database/cleanup-recommendations` - クリーンアップ推奨事項
- `POST /api/database/cleanup` - 手動クリーンアップ実行

#### 1.2 自動クリーンアップワーカー
- 定期的な古いデータ削除
- 設定可能な保持期間
- ログ出力による実行状況の可視化

#### 1.3 データベースサイズ監視
- 閾値ベースのサイズ監視
- アラート機能（NAS Monitoring System連携）
- テーブル別サイズ表示

### 2. プロジェクト別実装詳細

#### 2.1 nas-dashboard-monitoring

**データベース**: PostgreSQL + Redis
**実装ファイル**:
- `app/workers/cleanup_worker.py` - クリーンアップワーカー
- `app/services/db_size_monitor.py` - サイズ監視サービス
- `app/api/metrics.py` - データベース管理API

**保持ポリシー**:
- metrics: 30日
- anomalies: 90日
- notification_history: 30日

**閾値**: 100MB

#### 2.2 amazon-analytics

**データベース**: PostgreSQL
**実装ファイル**:
- `app/workers/cleanup_worker.py` - クリーンアップワーカー
- `app/services/db_size_monitor.py` - サイズ監視サービス
- `app/api/database_routes.py` - データベース管理API

**保持ポリシー**:
- analysis_results: 180日
- import_history: 90日

**閾値**: 50MB

#### 2.3 document-automation

**データベース**: Qdrant (Vector DB) + SQLite
**実装ファイル**:
- `app/workers/cleanup_worker.py` - クリーンアップワーカー
- `app/services/db_size_monitor.py` - サイズ監視サービス
- `app/api/database_routes.py` - データベース管理API

**保持ポリシー**:
- documents: 365日
- rag_sources: 365日
- vector_index: 365日
- processing_logs: 90日

**閾値**: 200MB

#### 2.4 notion-knowledge-summaries

**データベース**: SQLite + Chroma
**実装ファイル**:
- `app/api/database_routes.py` - データベース管理API

**保持ポリシー**:
- processing_logs: 90日
- rag_queries: 180日
- export_history: 90日

**閾値**: 50MB

**特別な対応**:
- DockerfileのCMD修正（`app.py` → `main.py`）
- `app`ディレクトリとの競合解決

## 技術的実装詳細

### 3.1 アーキテクチャパターン

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend UI   │◄──►│  Database API    │◄──►│   Database      │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                ▲
                                │
                       ┌──────────────────┐
                       │ Cleanup Worker   │
                       │ Size Monitor     │
                       └──────────────────┘
```

### 3.2 データ保持ポリシー設計

| データタイプ | 保持期間 | 理由 |
|-------------|----------|------|
| システムメトリクス | 30日 | リアルタイム監視に必要 |
| 異常検知結果 | 90日 | パターン分析に必要 |
| 処理ログ | 90日 | デバッグ・監査に必要 |
| 分析結果 | 180日 | トレンド分析に必要 |
| ドキュメント | 365日 | 長期参照に必要 |

### 3.3 エラーハンドリング

- データベース接続エラーの適切な処理
- ファイル不存在時の適切なレスポンス
- ログ出力による問題の可視化
- グレースフルデグラデーション

## 運用面での考慮事項

### 4.1 監視・アラート

- NAS Monitoring Systemとの連携
- データベースサイズの閾値監視
- クリーンアップ実行状況のログ監視

### 4.2 バックアップ戦略

- クリーンアップ前の自動バックアップ
- 重要なデータの長期保存
- 復旧手順の文書化

### 4.3 パフォーマンス影響

- 非同期処理による影響最小化
- インデックス最適化
- バッチ処理による効率化

## 実装結果

### 5.1 成功指標

- ✅ 全4プロジェクトでAPI動作確認完了
- ✅ Dockerコンテナ正常起動
- ✅ エラーハンドリング適切に動作
- ✅ ログ出力正常

### 5.2 解決した問題

1. **Dockerコンテナ起動エラー** (`notion-knowledge-summaries`)
   - 問題: `app`ディレクトリと`app.py`の競合
   - 解決: `app.py` → `main.py`リネーム

2. **データベース肥大化リスク**
   - 問題: 無制限なデータ蓄積
   - 解決: 自動クリーンアップ + サイズ監視

3. **運用負荷**
   - 問題: 手動でのデータ管理
   - 解決: 自動化 + API提供

## 新規システム追加時の考慮事項

### 6.1 データベース使用システムの判定基準

新規システムを追加する際は、以下の基準でデータベース肥大化対策の必要性を判定してください：

#### 6.1.1 データベース使用の確認項目
- [ ] SQLite、PostgreSQL、MySQL、MongoDB等のデータベースを使用している
- [ ] ファイルベースのデータストレージ（JSON、CSV等）を使用している
- [ ] ベクトルデータベース（Qdrant、Chroma、Pinecone等）を使用している
- [ ] キャッシュシステム（Redis、Memcached等）を使用している
- [ ] ログファイルが継続的に蓄積される
- [ ] ユーザー生成データが蓄積される
- [ ] APIレスポンスデータが保存される

#### 6.1.2 対策が必要なケース
以下のいずれかに該当する場合は、データベース肥大化対策の実装を検討してください：

- **データベース使用**: 上記6.1.1の項目に1つ以上該当
- **データ蓄積量**: 月間1GB以上のデータ増加が予想される
- **長期運用**: 1年以上の継続運用が予定されている
- **パフォーマンス重要**: レスポンス時間が重要なシステム
- **ストレージ制約**: 限られたストレージ容量での運用

### 6.2 実装手順

#### 6.2.1 事前調査
1. **データベース種類の特定**
   - 使用しているデータベースの種類
   - データベースファイルの場所
   - 接続設定の確認

2. **データ構造の分析**
   - テーブル/コレクションの一覧
   - 各テーブルのデータ量
   - データの性質（ログ、ユーザーデータ、分析結果等）

3. **保持要件の決定**
   - ビジネス要件に基づく保持期間
   - 法的要件（データ保護法等）
   - 分析・監査要件

#### 6.2.2 実装テンプレート

新規システム用の実装テンプレートを以下に示します：

**1. データベース管理API (`app/api/database_routes.py`)**
```python
# -*- coding: utf-8 -*-
"""
{プロジェクト名} - データベース管理API
"""

from flask import Blueprint, jsonify, request
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
db_bp = Blueprint('database', __name__)

# データ保持ポリシー (日数) - プロジェクトに応じて調整
TABLE_RETENTION_DAYS = {
    'logs': 90,
    'user_data': 365,
    'analysis_results': 180,
    # プロジェクト固有のテーブルを追加
}

# データベースサイズ閾値 (MB) - プロジェクトに応じて調整
DB_SIZE_THRESHOLD_MB = 100

@db_bp.route('/stats', methods=['GET'])
def get_database_stats():
    """データベース統計情報を取得"""
    # プロジェクト固有の実装
    pass

@db_bp.route('/size', methods=['GET'])
def get_database_size():
    """データベースサイズをチェック"""
    # プロジェクト固有の実装
    pass

@db_bp.route('/cleanup-recommendations', methods=['GET'])
def get_cleanup_recommendations():
    """クリーンアップ推奨事項を取得"""
    # プロジェクト固有の実装
    pass

@db_bp.route('/cleanup', methods=['POST'])
def run_manual_cleanup():
    """手動クリーンアップを実行"""
    # プロジェクト固有の実装
    pass
```

**2. クリーンアップワーカー (`app/workers/cleanup_worker.py`)**
```python
# -*- coding: utf-8 -*-
"""
{プロジェクト名} - データベースクリーンアップワーカー
"""

import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CleanupWorker:
    def __init__(self):
        self.running = False
        
    async def start(self):
        """クリーンアップワーカーを開始"""
        self.running = True
        logger.info("データベースクリーンアップワーカーを開始しました")
        
        while self.running:
            try:
                await self.run_cleanup()
                # 24時間ごとに実行
                await asyncio.sleep(24 * 60 * 60)
            except Exception as e:
                logger.error(f"クリーンアップ実行エラー: {str(e)}")
                await asyncio.sleep(60)  # エラー時は1分待機
    
    async def run_cleanup(self):
        """クリーンアップを実行"""
        # プロジェクト固有の実装
        pass
    
    async def stop(self):
        """クリーンアップワーカーを停止"""
        self.running = False
        logger.info("データベースクリーンアップワーカーを停止しました")
```

**3. サイズ監視サービス (`app/services/db_size_monitor.py`)**
```python
# -*- coding: utf-8 -*-
"""
{プロジェクト名} - データベースサイズ監視サービス
"""

import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseSizeMonitor:
    def __init__(self):
        self.threshold_mb = 100  # プロジェクトに応じて調整
        
    async def start_periodic_check(self):
        """定期的なサイズチェックを開始"""
        while True:
            try:
                await self.check_database_size()
                # 1時間ごとにチェック
                await asyncio.sleep(60 * 60)
            except Exception as e:
                logger.error(f"サイズチェックエラー: {str(e)}")
                await asyncio.sleep(60)
    
    async def check_database_size(self):
        """データベースサイズをチェック"""
        # プロジェクト固有の実装
        pass
```

#### 6.2.3 設定ファイル更新

**Docker Compose (`docker-compose.yml`)**
```yaml
services:
  {サービス名}:
    # 既存の設定...
    environment:
      # データベース肥大化対策用の環境変数を追加
      - DB_CLEANUP_ENABLED=true
      - DB_SIZE_THRESHOLD_MB=100
      - DB_RETENTION_DAYS=90
```

**メインアプリケーション (`app/main.py` または `app.py`)**
```python
# クリーンアップワーカーとサイズ監視の統合
from app.workers.cleanup_worker import CleanupWorker
from app.services.db_size_monitor import DatabaseSizeMonitor

# アプリケーション起動時にワーカーを開始
cleanup_worker = CleanupWorker()
size_monitor = DatabaseSizeMonitor()

# FastAPIの場合
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_worker.start())
    asyncio.create_task(size_monitor.start_periodic_check())

# Flaskの場合
if __name__ == '__main__':
    asyncio.create_task(cleanup_worker.start())
    asyncio.create_task(size_monitor.start_periodic_check())
    app.run()
```

### 6.3 プロジェクト固有の調整項目

#### 6.3.1 データベース種類別の実装例

**PostgreSQL**
```python
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        cursor_factory=RealDictCursor
    )

def get_database_size():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pg_size_pretty(pg_database_size(current_database())) as size,
               pg_database_size(current_database()) as size_bytes
    """)
    result = cursor.fetchone()
    conn.close()
    return result
```

**SQLite**
```python
import sqlite3
from pathlib import Path

def get_db_path():
    return Path("data") / "database.db"

def get_database_size():
    db_path = get_db_path()
    if not db_path.exists():
        return 0
    return db_path.stat().st_size
```

**MongoDB**
```python
from pymongo import MongoClient

def get_db_connection():
    client = MongoClient(os.getenv('MONGO_URI'))
    return client[os.getenv('DB_NAME')]

def get_database_size():
    db = get_db_connection()
    stats = db.command("dbStats")
    return stats['dataSize']
```

#### 6.3.2 保持ポリシーの決定指針

| データタイプ | 推奨保持期間 | 考慮事項 |
|-------------|-------------|----------|
| アクセスログ | 30-90日 | セキュリティ監査、パフォーマンス分析 |
| エラーログ | 90-180日 | デバッグ、パターン分析 |
| ユーザーデータ | 365日以上 | 法的要件、ビジネス要件 |
| 分析結果 | 180-365日 | トレンド分析、レポート生成 |
| 一時データ | 7-30日 | 処理完了後の不要データ |
| バックアップ | 30-90日 | 災害復旧、データ復元 |

### 6.4 テスト・検証手順

#### 6.4.1 実装後のテスト項目
- [ ] データベース管理APIの動作確認
- [ ] クリーンアップワーカーの動作確認
- [ ] サイズ監視の動作確認
- [ ] エラーハンドリングの確認
- [ ] ログ出力の確認
- [ ] Dockerコンテナ起動の確認

#### 6.4.2 パフォーマンステスト
- [ ] クリーンアップ実行時のパフォーマンス影響
- [ ] 大量データ削除時のロック時間
- [ ] サイズ監視のオーバーヘッド
- [ ] APIレスポンス時間

### 6.5 運用開始後の監視項目

#### 6.5.1 日常監視
- データベースサイズの推移
- クリーンアップ実行状況
- エラーログの確認
- パフォーマンスメトリクス

#### 6.5.2 定期レビュー
- 保持ポリシーの見直し（四半期ごと）
- 閾値設定の調整（半年ごと）
- パフォーマンス最適化（年1回）

## 今後の拡張可能性

### 7.1 機能拡張

- より詳細な分析機能
- カスタム保持ポリシー設定
- データ圧縮機能
- 分散データベース対応

### 7.2 監視強化

- リアルタイムダッシュボード
- 予測的アラート
- パフォーマンスメトリクス
- コスト最適化提案

## まとめ

データベース肥大化対策の実装により、NAS環境の各プロジェクトで以下の効果が期待されます：

1. **ストレージ使用量の最適化**
2. **パフォーマンスの維持**
3. **運用負荷の軽減**
4. **データ管理の自動化**

**新規システム追加時の重要ポイント**:
- データベース使用の有無を必ず確認
- 本レポートの判定基準に基づいて対策の必要性を判断
- 実装テンプレートを活用して効率的に実装
- プロジェクト固有の要件に応じてカスタマイズ
- 実装後のテスト・検証を必ず実施

実装は段階的に行われ、各プロジェクトの特性に応じてカスタマイズされています。継続的な監視と調整により、長期的な効果を最大化できます。

---

**実装完了日**: 2025年10月29日  
**対象プロジェクト**: nas-dashboard-monitoring, amazon-analytics, document-automation, notion-knowledge-summaries  
**実装者**: AI Assistant  
**更新日**: 2025年10月29日（新規システム追加時の考慮事項を追加）
