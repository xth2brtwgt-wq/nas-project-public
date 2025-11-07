# -*- coding: utf-8 -*-
"""
Document Automation - データベースクリーンアップワーカー
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import text
from app.models.database import SessionLocal
from config.settings import settings

logger = logging.getLogger(__name__)

class DocumentAutomationCleanupWorker:
    """Document Automation データベースクリーンアップワーカー"""
    
    def __init__(self):
        self.is_running = False
        
    async def start(self):
        """クリーンアップワーカーを開始"""
        self.is_running = True
        logger.info("Document Automation データベースクリーンアップワーカーを開始しました")
        
        while self.is_running:
            try:
                await self._run_cleanup()
                # 7日ごとに実行
                await asyncio.sleep(7 * 24 * 60 * 60)
            except Exception as e:
                logger.error(f"クリーンアップエラー: {e}")
                # エラー時は1時間後に再試行
                await asyncio.sleep(60 * 60)
    
    async def stop(self):
        """クリーンアップワーカーを停止"""
        self.is_running = False
        logger.info("Document Automation データベースクリーンアップワーカーを停止しました")
    
    async def _run_cleanup(self):
        """クリーンアップを実行"""
        logger.info("Document Automation データベースクリーンアップを開始します")
        
        # ドキュメントのクリーンアップ（180日経過、アーカイブ済み）
        documents_deleted = await self._cleanup_documents()
        
        # 処理ログのクリーンアップ（90日経過）
        logs_deleted = await self._cleanup_processing_logs()
        
        # エクスポート履歴のクリーンアップ（90日経過）
        exports_deleted = await self._cleanup_export_history()
        
        logger.info(f"クリーンアップ完了: ドキュメント={documents_deleted}件, ログ={logs_deleted}件, エクスポート={exports_deleted}件")
    
    async def _cleanup_documents(self) -> int:
        """180日経過のアーカイブ済みドキュメントを削除"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=180)
            
            db = SessionLocal()
            try:
                result = db.execute(
                    text("DELETE FROM documents WHERE is_archived = true AND created_at < :cutoff_date"),
                    {"cutoff_date": cutoff_date}
                )
                deleted_count = result.rowcount
                db.commit()
                
                if deleted_count > 0:
                    logger.info(f"180日経過のアーカイブ済みドキュメントを削除しました: {deleted_count}件")
                
                return deleted_count
            finally:
                db.close()
        except Exception as e:
            logger.error(f"ドキュメントクリーンアップエラー: {e}")
            return 0
    
    async def _cleanup_processing_logs(self) -> int:
        """90日経過の処理ログを削除"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            db = SessionLocal()
            try:
                result = db.execute(
                    text("DELETE FROM processing_logs WHERE created_at < :cutoff_date"),
                    {"cutoff_date": cutoff_date}
                )
                deleted_count = result.rowcount
                db.commit()
                
                if deleted_count > 0:
                    logger.info(f"90日経過の処理ログを削除しました: {deleted_count}件")
                
                return deleted_count
            finally:
                db.close()
        except Exception as e:
            logger.error(f"処理ログクリーンアップエラー: {e}")
            return 0
    
    async def _cleanup_export_history(self) -> int:
        """90日経過のエクスポート履歴を削除"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            db = SessionLocal()
            try:
                result = db.execute(
                    text("DELETE FROM export_history WHERE created_at < :cutoff_date"),
                    {"cutoff_date": cutoff_date}
                )
                deleted_count = result.rowcount
                db.commit()
                
                if deleted_count > 0:
                    logger.info(f"90日経過のエクスポート履歴を削除しました: {deleted_count}件")
                
                return deleted_count
            finally:
                db.close()
        except Exception as e:
            logger.error(f"エクスポート履歴クリーンアップエラー: {e}")
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
                        'documents' as table_name, COUNT(*) as count FROM documents
                    UNION ALL
                    SELECT 
                        'rag_sources' as table_name, COUNT(*) as count FROM rag_sources
                    UNION ALL
                    SELECT 
                        'vector_index' as table_name, COUNT(*) as count FROM vector_index
                    UNION ALL
                    SELECT 
                        'processing_logs' as table_name, COUNT(*) as count FROM processing_logs
                    UNION ALL
                    SELECT 
                        'export_history' as table_name, COUNT(*) as count FROM export_history
                    UNION ALL
                    SELECT 
                        'rag_queries' as table_name, COUNT(*) as count FROM rag_queries
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
document_automation_cleanup_worker = DocumentAutomationCleanupWorker()
