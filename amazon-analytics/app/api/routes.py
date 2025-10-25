"""API routes"""
import logging
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import shutil

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.purchase import Purchase, Category, ImportHistory, AnalysisResult
from app.services.data_processor import DataProcessor
from app.services.ai_analyzer import AIAnalyzer
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process CSV file"""
    
    # Validate file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # Save uploaded file
    file_path = settings.UPLOAD_DIR / file.filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Saved uploaded file: {file.filename}")
        
        # Process CSV
        processor = DataProcessor(db)
        import_record = processor.import_csv_file(file_path)
        
        # Initialize categories if needed
        if db.query(Category).count() == 0:
            processor.initialize_categories()
        
        return {
            "success": True,
            "filename": file.filename,
            "import_id": import_record.id,
            "record_count": import_record.record_count,
            "status": import_record.status,
        }
        
    except Exception as e:
        logger.error(f"Failed to process upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """Get overall statistics"""
    processor = DataProcessor(db)
    stats = processor.get_statistics()
    
    # Category breakdown
    from sqlalchemy import func
    category_stats = db.query(
        Category.name,
        func.count(Purchase.id).label('count'),
        func.sum(Purchase.total_owed).label('total')
    ).join(Purchase, Category.id == Purchase.category_id, isouter=True)\
     .group_by(Category.name)\
     .all()
    
    stats['categories'] = [
        {
            'name': cat.name,
            'count': cat.count or 0,
            'total': float(cat.total or 0)
        }
        for cat in category_stats
    ]
    
    return stats


@router.get("/purchases")
async def get_purchases(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get purchases with filtering"""
    query = db.query(Purchase)
    
    # Apply filters
    if category:
        query = query.join(Category).filter(Category.name == category)
    
    if start_date:
        query = query.filter(Purchase.order_date >= datetime.fromisoformat(start_date))
    
    if end_date:
        query = query.filter(Purchase.order_date <= datetime.fromisoformat(end_date))
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    purchases = query.order_by(Purchase.order_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return {
        "total": total,
        "items": [
            {
                "id": p.id,
                "order_id": p.order_id,
                "order_date": p.order_date.isoformat() if p.order_date else None,
                "product_name": p.product_name,
                "category": p.category.name if p.category else None,
                "total_owed": p.total_owed,
                "quantity": p.quantity,
            }
            for p in purchases
        ]
    }


@router.post("/analyze/classify")
async def auto_classify(
    limit: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db)
):
    """Auto-classify purchases using AI"""
    analyzer = AIAnalyzer(db)
    
    try:
        analyzer.auto_classify_purchases(limit=limit)
        return {"success": True, "message": "Classification complete"}
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/impulse")
async def analyze_impulse_buying(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Analyze impulse buying patterns"""
    analyzer = AIAnalyzer(db)
    results = analyzer.analyze_impulse_buying(days=days)
    return results


@router.get("/analyze/recurring")
async def analyze_recurring(
    min_occurrences: int = Query(3, ge=2),
    db: Session = Depends(get_db)
):
    """Analyze recurring purchase patterns"""
    analyzer = AIAnalyzer(db)
    results = analyzer.analyze_recurring_purchases(min_occurrences=min_occurrences)
    return {"recurring_purchases": results}


@router.get("/analyze/monthly-insights")
async def monthly_insights(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Generate monthly insights using AI"""
    analyzer = AIAnalyzer(db)
    insights = analyzer.generate_monthly_insights(year, month)
    
    # Save to database
    analyzer.save_analysis_result(
        analysis_type='monthly_insights',
        target_period=f'{year}-{month:02d}',
        result_data={'insights': insights},
        summary=insights[:200]
    )
    
    return {"insights": insights}


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).all()
    return {
        "categories": [
            {
                "id": cat.id,
                "name": cat.name,
                "name_en": cat.name_en,
                "budget": cat.budget,
            }
            for cat in categories
        ]
    }


@router.get("/import-history")
async def get_import_history(db: Session = Depends(get_db)):
    """Get import history"""
    history = db.query(ImportHistory)\
        .order_by(ImportHistory.import_date.desc())\
        .limit(20)\
        .all()
    
    return {
        "history": [
            {
                "id": h.id,
                "filename": h.filename,
                "import_date": h.import_date.isoformat(),
                "record_count": h.record_count,
                "status": h.status,
                "processing_time": h.processing_time,
                "error_message": h.error_message,
            }
            for h in history
        ]
    }


@router.post("/categories/initialize")
async def initialize_categories(db: Session = Depends(get_db)):
    """Initialize default categories"""
    processor = DataProcessor(db)
    processor.initialize_categories()
    return {"success": True, "message": "Categories initialized"}

