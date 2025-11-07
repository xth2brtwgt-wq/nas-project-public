# -*- coding: utf-8 -*-
"""
Amazon Analytics - データベース管理API
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.workers.cleanup_worker import amazon_analytics_cleanup_worker
from app.services.db_size_monitor import amazon_analytics_db_size_monitor

router = APIRouter()

@router.get("/database/stats")
async def get_database_stats():
    """データベース統計情報を取得"""
    try:
        stats = await amazon_analytics_cleanup_worker.get_database_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データベース統計取得に失敗しました: {str(e)}")

@router.get("/database/size")
async def check_database_size():
    """データベースサイズをチェック"""
    try:
        size_info = await amazon_analytics_db_size_monitor.check_database_size()
        return size_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データベースサイズチェックに失敗しました: {str(e)}")

@router.get("/database/cleanup-recommendations")
async def get_cleanup_recommendations():
    """クリーンアップ推奨事項を取得"""
    try:
        recommendations = await amazon_analytics_db_size_monitor.get_cleanup_recommendations()
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"クリーンアップ推奨事項取得に失敗しました: {str(e)}")

@router.post("/database/cleanup")
async def run_manual_cleanup():
    """手動クリーンアップを実行"""
    try:
        # クリーンアップを実行
        await amazon_analytics_cleanup_worker._run_cleanup()
        
        # 最新の統計を取得
        stats = await amazon_analytics_cleanup_worker.get_database_stats()
        
        return {
            "message": "クリーンアップが完了しました",
            "stats": stats,
            "executed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"クリーンアップ実行に失敗しました: {str(e)}")
