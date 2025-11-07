# -*- coding: utf-8 -*-
"""
Document Automation - データベースサイズ監視サービス
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import text
from app.models.database import SessionLocal
from config.settings import settings

logger = logging.getLogger(__name__)

class DocumentAutomationDatabaseSizeMonitor:
    """Document Automation データベースサイズ監視サービス"""
    
    def __init__(self):
        self.size_threshold_mb = 200  # 200MB（文書データは中程度のサイズ想定）
        self.last_alert_time: Optional[datetime] = None
        self.alert_cooldown_hours = 24  # 24時間のクールダウン
        self.is_running = False
    
    async def check_database_size(self) -> Dict[str, Any]:
        """データベースサイズをチェック"""
        try:
            db = SessionLocal()
            try:
                # データベース全体サイズを取得
                size_query = text("SELECT pg_database_size(current_database()) as size_bytes")
                result = db.execute(size_query).fetchone()
                
                if result:
                    size_bytes = result[0]
                    size_mb = size_bytes / (1024 * 1024)
                    
                    # テーブル別サイズも取得
                    table_sizes = await self._get_table_sizes(db)
                    
                    stats = {
                        "database_size_bytes": size_bytes,
                        "database_size_mb": round(size_mb, 2),
                        "database_size_pretty": self._format_size(size_bytes),
                        "table_sizes": table_sizes,
                        "threshold_mb": self.size_threshold_mb,
                        "is_over_threshold": size_mb > self.size_threshold_mb,
                        "checked_at": datetime.utcnow()
                    }
                    
                    # 閾値超過の場合はアラート（ログのみ）
                    if stats["is_over_threshold"]:
                        await self._send_size_alert(stats)
                    
                    return stats
                else:
                    logger.error("データベースサイズの取得に失敗しました")
                    return {}
            finally:
                db.close()
        except Exception as e:
            logger.error(f"データベースサイズチェックエラー: {e}")
            return {}
    
    async def _get_table_sizes(self, db) -> list:
        """テーブル別サイズを取得"""
        try:
            query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size_pretty,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables 
                WHERE schemaname='public' 
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            
            result = db.execute(query).fetchall()
            return [
                {
                    "table_name": row.tablename,
                    "size_pretty": row.size_pretty,
                    "size_bytes": row.size_bytes,
                    "size_mb": round(row.size_bytes / (1024 * 1024), 2)
                }
                for row in result
            ]
        except Exception as e:
            logger.error(f"テーブルサイズ取得エラー: {e}")
            return []
    
    async def _send_size_alert(self, stats: Dict[str, Any]):
        """データベースサイズアラートを送信（ログのみ）"""
        try:
            # クールダウンチェック
            if self.last_alert_time:
                time_since_last = datetime.utcnow() - self.last_alert_time
                if time_since_last.total_seconds() < self.alert_cooldown_hours * 3600:
                    logger.info(f"データベースサイズアラートのクールダウン中: {self.alert_cooldown_hours}時間")
                    return
            
            logger.warning(f"Document Automation DBサイズアラート: {stats['database_size_pretty']} (閾値: {self.size_threshold_mb}MB)")
            logger.warning(f"テーブル別サイズ: {stats['table_sizes']}")
            
            # アラート時刻を更新
            self.last_alert_time = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"データベースサイズアラート送信エラー: {e}")
    
    def _format_size(self, size_bytes: int) -> str:
        """サイズを人間が読みやすい形式にフォーマット"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    async def get_cleanup_recommendations(self) -> Dict[str, Any]:
        """クリーンアップ推奨事項を取得"""
        try:
            db = SessionLocal()
            try:
                # 古いデータの統計を取得
                old_documents_query = text("""
                    SELECT COUNT(*) as count 
                    FROM documents 
                    WHERE is_archived = true AND created_at < NOW() - INTERVAL '180 days'
                """)
                
                old_logs_query = text("""
                    SELECT COUNT(*) as count 
                    FROM processing_logs 
                    WHERE created_at < NOW() - INTERVAL '90 days'
                """)
                
                old_exports_query = text("""
                    SELECT COUNT(*) as count 
                    FROM export_history 
                    WHERE created_at < NOW() - INTERVAL '90 days'
                """)
                
                old_documents = db.execute(old_documents_query).fetchone()[0]
                old_logs = db.execute(old_logs_query).fetchone()[0]
                old_exports = db.execute(old_exports_query).fetchone()[0]
                
                return {
                    "old_documents_count": old_documents,
                    "old_logs_count": old_logs,
                    "old_exports_count": old_exports,
                    "recommendations": [
                        f"180日経過のアーカイブ済みドキュメント: {old_documents}件削除可能",
                        f"90日経過の処理ログ: {old_logs}件削除可能",
                        f"90日経過のエクスポート履歴: {old_exports}件削除可能"
                    ] if any([old_documents, old_logs, old_exports]) else ["クリーンアップ対象データなし"]
                }
            finally:
                db.close()
        except Exception as e:
            logger.error(f"クリーンアップ推奨事項取得エラー: {e}")
            return {"recommendations": ["エラーにより取得できませんでした"]}

    async def start_periodic_check(self):
        """定期チェックを開始（1日ごと）"""
        self.is_running = True
        logger.info("Document Automation データベースサイズ定期監視を開始しました")
        
        while self.is_running:
            try:
                await self.check_database_size()
                # 1日ごとにチェック
                await asyncio.sleep(24 * 60 * 60)
            except Exception as e:
                logger.error(f"定期サイズチェックエラー: {e}")
                # エラー時は6時間後に再試行
                await asyncio.sleep(6 * 60 * 60)
    
    async def stop_periodic_check(self):
        """定期チェックを停止"""
        self.is_running = False
        logger.info("Document Automation データベースサイズ定期監視を停止しました")

# グローバルインスタンス
document_automation_db_size_monitor = DocumentAutomationDatabaseSizeMonitor()
