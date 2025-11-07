# -*- coding: utf-8 -*-
"""
Document Automation - データベース管理API
"""

from fastapi import APIRouter, HTTPException
import logging
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)
router = APIRouter()

def get_db_path():
    """データベースパスを取得"""
    return Path("data") / "documents.db"

def get_db_size():
    """データベースサイズを取得"""
    db_path = get_db_path()
    if not db_path.exists():
        return 0
    return db_path.stat().st_size

def format_size(size_bytes):
    """サイズをフォーマット"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def get_db_connection():
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    return conn

@router.get('/database/stats')
async def get_database_stats():
    """データベース統計情報を取得"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # テーブルサイズとレコード数
        table_stats = []
        tables = ["documents", "rag_sources", "vector_index", "processing_logs", "export_history", "rag_queries"]
        for table_name in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                table_stats.append({
                    "table_name": table_name,
                    "record_count": count,
                })
            except sqlite3.OperationalError:
                # テーブルが存在しない場合はスキップ
                logger.warning(f"テーブル {table_name} が見つかりません")
                continue
        
        # データベース全体のサイズ
        db_size_bytes = get_db_size()
        db_size_mb = db_size_bytes / (1024 * 1024)
        db_size_pretty = format_size(db_size_bytes)

        conn.close()

        return {
            "status": "success",
            "database_size": db_size_pretty,
            "database_size_mb": db_size_mb,
            "table_stats": table_stats
        }

    except Exception as e:
        logger.error(f"データベース統計取得エラー: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@router.get('/database/size')
async def get_database_size():
    """データベースサイズをチェック"""
    try:
        db_size_bytes = get_db_size()
        db_size_mb = db_size_bytes / (1024 * 1024)
        db_size_pretty = format_size(db_size_bytes)

        DB_SIZE_THRESHOLD_MB = 200  # document-automation用の閾値
        is_over_threshold = db_size_mb > DB_SIZE_THRESHOLD_MB

        if is_over_threshold:
            logger.warning(f"データベースサイズが閾値を超過しました: {db_size_pretty} (閾値: {DB_SIZE_THRESHOLD_MB}MB)。")

        return {
            "status": "success",
            "database_size_mb": db_size_mb,
            "database_size_pretty": db_size_pretty,
            "is_over_threshold": is_over_threshold,
            "threshold_mb": DB_SIZE_THRESHOLD_MB
        }

    except Exception as e:
        logger.error(f"データベースサイズチェックエラー: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@router.get('/database/cleanup-recommendations')
async def get_cleanup_recommendations():
    """クリーンアップ推奨事項を取得"""
    recommendations = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        PROCESSING_LOG_RETENTION_DAYS = 90
        RAG_QUERY_RETENTION_DAYS = 180
        EXPORT_HISTORY_RETENTION_DAYS = 90

        # processing_logs
        try:
            cutoff_date_log = datetime.utcnow() - timedelta(days=PROCESSING_LOG_RETENTION_DAYS)
            cursor.execute("SELECT COUNT(*) FROM processing_logs WHERE created_at < ?", (cutoff_date_log.isoformat(),))
            old_logs_count = cursor.fetchone()[0]
            if old_logs_count > 0:
                recommendations.append(f"処理ログに{PROCESSING_LOG_RETENTION_DAYS}日以上前のデータが{old_logs_count}件あります。クリーンアップを推奨します。")
        except sqlite3.OperationalError:
            logger.warning("processing_logs テーブルが見つかりません。")

        # rag_queries
        try:
            cutoff_date_rag = datetime.utcnow() - timedelta(days=RAG_QUERY_RETENTION_DAYS)
            cursor.execute("SELECT COUNT(*) FROM rag_queries WHERE created_at < ?", (cutoff_date_rag.isoformat(),))
            old_rag_queries_count = cursor.fetchone()[0]
            if old_rag_queries_count > 0:
                recommendations.append(f"RAGクエリに{RAG_QUERY_RETENTION_DAYS}日以上前のデータが{old_rag_queries_count}件あります。クリーンアップを推奨します。")
        except sqlite3.OperationalError:
            logger.warning("rag_queries テーブルが見つかりません。")

        # export_history
        try:
            cutoff_date_export = datetime.utcnow() - timedelta(days=EXPORT_HISTORY_RETENTION_DAYS)
            cursor.execute("SELECT COUNT(*) FROM export_history WHERE created_at < ?", (cutoff_date_export.isoformat(),))
            old_export_history_count = cursor.fetchone()[0]
            if old_export_history_count > 0:
                recommendations.append(f"エクスポート履歴に{EXPORT_HISTORY_RETENTION_DAYS}日以上前のデータが{old_export_history_count}件あります。クリーンアップを推奨します。")
        except sqlite3.OperationalError:
            logger.warning("export_history テーブルが見つかりません。")

        if not recommendations:
            recommendations.append("現在、推奨されるクリーンアップはありません。")

        return {
            "status": "success",
            "recommendations": recommendations
        }

    except Exception as e:
        logger.error(f"クリーンアップ推奨事項取得エラー: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        if conn:
            conn.close()

@router.post('/database/cleanup')
async def run_manual_cleanup():
    """手動クリーンアップを実行"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        deleted_counts = {}

        PROCESSING_LOG_RETENTION_DAYS = 90
        RAG_QUERY_RETENTION_DAYS = 180
        EXPORT_HISTORY_RETENTION_DAYS = 90

        # processing_logsの削除
        try:
            cutoff_date_log = datetime.utcnow() - timedelta(days=PROCESSING_LOG_RETENTION_DAYS)
            cursor.execute("DELETE FROM processing_logs WHERE created_at < ?", (cutoff_date_log.isoformat(),))
            deleted_counts["processing_logs"] = cursor.rowcount
            logger.info(f"{deleted_counts['processing_logs']}件の古い処理ログを削除しました。")
        except sqlite3.OperationalError:
            logger.warning("processing_logs テーブルが見つからないため、スキップしました。")
            deleted_counts["processing_logs"] = 0

        # rag_queriesの削除
        try:
            cutoff_date_rag = datetime.utcnow() - timedelta(days=RAG_QUERY_RETENTION_DAYS)
            cursor.execute("DELETE FROM rag_queries WHERE created_at < ?", (cutoff_date_rag.isoformat(),))
            deleted_counts["rag_queries"] = cursor.rowcount
            logger.info(f"{deleted_counts['rag_queries']}件の古いRAGクエリを削除しました。")
        except sqlite3.OperationalError:
            logger.warning("rag_queries テーブルが見つからないため、スキップしました。")
            deleted_counts["rag_queries"] = 0

        # export_historyの削除
        try:
            cutoff_date_export = datetime.utcnow() - timedelta(days=EXPORT_HISTORY_RETENTION_DAYS)
            cursor.execute("DELETE FROM export_history WHERE created_at < ?", (cutoff_date_export.isoformat(),))
            deleted_counts["export_history"] = cursor.rowcount
            logger.info(f"{deleted_counts['export_history']}件の古いエクスポート履歴を削除しました。")
        except sqlite3.OperationalError:
            logger.warning("export_history テーブルが見つからないため、スキップしました。")
            deleted_counts["export_history"] = 0

        conn.commit()

        # VACUUMを実行してデータベースファイルを最適化
        conn.execute("VACUUM")
        conn.commit()
        logger.info("データベースのVACUUMを実行しました。")

        return {
            "status": "success",
            "message": "クリーンアップが完了しました",
            "deleted_counts": deleted_counts,
            "executed_at": datetime.now().isoformat()
        }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"手動クリーンアップエラー: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        if conn:
            conn.close()
