# -*- coding: utf-8 -*-
"""
Amazon Analytics - データベースクリーンアップワーカー
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import text
from app.models.database import SessionLocal
from config.settings import settings

logger = logging.getLogger(__name__)

class AmazonAnalyticsCleanupWorker:
    """Amazon Analytics データベースクリーンアップワーカー"""
    
    def __init__(self):
        self.is_running = False
        
    async def start(self):
        """クリーンアップワーカーを開始"""
        self.is_running = True
        logger.info("Amazon Analytics データベースクリーンアップワーカーを開始しました")
        
        while self.is_running:
            try:
                await self._run_cleanup()
                # 7日ごとに実行（購入データは長期保持が重要）
                await asyncio.sleep(7 * 24 * 60 * 60)
            except Exception as e:
                logger.error(f"クリーンアップエラー: {e}")
                # エラー時は1時間後に再試行
                await asyncio.sleep(60 * 60)
    
    async def stop(self):
        """クリーンアップワーカーを停止"""
        self.is_running = False
        logger.info("Amazon Analytics データベースクリーンアップワーカーを停止しました")
    
    async def _run_cleanup(self):
        """クリーンアップを実行"""
        logger.info("Amazon Analytics データベースクリーンアップを開始します")
        
        # 分析結果のクリーンアップ（90日経過）
        analysis_deleted = await self._cleanup_analysis_results()
        
        # インポート履歴のクリーンアップ（180日経過）
        import_deleted = await self._cleanup_import_history()
        
        logger.info(f"クリーンアップ完了: 分析結果={analysis_deleted}件, インポート履歴={import_deleted}件")
    
    async def _cleanup_analysis_results(self) -> int:
        """90日経過の分析結果を削除"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            db = SessionLocal()
            try:
                result = db.execute(
                    text("DELETE FROM analysis_results WHERE created_at < :cutoff_date"),
                    {"cutoff_date": cutoff_date}
                )
                deleted_count = result.rowcount
                db.commit()
                
                if deleted_count > 0:
                    logger.info(f"90日経過の分析結果を削除しました: {deleted_count}件")
                
                return deleted_count
            finally:
                db.close()
        except Exception as e:
            logger.error(f"分析結果クリーンアップエラー: {e}")
            return 0
    
    async def _cleanup_import_history(self) -> int:
        """180日経過のインポート履歴を削除"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=180)
            
            db = SessionLocal()
            try:
                result = db.execute(
                    text("DELETE FROM import_history WHERE created_at < :cutoff_date"),
                    {"cutoff_date": cutoff_date}
                )
                deleted_count = result.rowcount
                db.commit()
                
                if deleted_count > 0:
                    logger.info(f"180日経過のインポート履歴を削除しました: {deleted_count}件")
                
                return deleted_count
            finally:
                db.close()
        except Exception as e:
            logger.error(f"インポート履歴クリーンアップエラー: {e}")
            return 0
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """データベース統計情報を取得"""
        try:
            db = SessionLocal()
            try:
                # テーブルサイズ情報
                size_query = text("""
                    SELECT 
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                        pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                    FROM pg_tables 
                    WHERE schemaname='public' 
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                """)
                
                size_result = db.execute(size_query).fetchall()
                
                # レコード数情報
                count_query = text("""
                    SELECT 
                        'purchases' as table_name, COUNT(*) as count FROM purchases
                    UNION ALL
                    SELECT 
                        'categories' as table_name, COUNT(*) as count FROM categories
                    UNION ALL
                    SELECT 
                        'analysis_results' as table_name, COUNT(*) as count FROM analysis_results
                    UNION ALL
                    SELECT 
                        'import_history' as table_name, COUNT(*) as count FROM import_history
                """)
                
                count_result = db.execute(count_query).fetchall()
                
                # データベース全体サイズ
                db_size_query = text("SELECT pg_size_pretty(pg_database_size(current_database())) as db_size")
                db_size_result = db.execute(db_size_query).fetchone()
                
                return {
                    "table_sizes": [dict(row._mapping) for row in size_result],
                    "record_counts": [dict(row._mapping) for row in count_result],
                    "database_size": db_size_result[0] if db_size_result else "Unknown"
                }
            finally:
                db.close()
        except Exception as e:
            logger.error(f"データベース統計取得エラー: {e}")
            return {}

# グローバルインスタンス
amazon_analytics_cleanup_worker = AmazonAnalyticsCleanupWorker()
