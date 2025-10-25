"""Report generation API routes"""
import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.report_generator import ReportGenerator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/report/monthly")
async def get_monthly_report(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Get monthly report data"""
    generator = ReportGenerator(db)
    report = generator.generate_monthly_report(year, month)
    return report


@router.get("/report/yearly")
async def get_yearly_report(
    year: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db)
):
    """Get yearly report data"""
    generator = ReportGenerator(db)
    report = generator.generate_yearly_report(year)
    return report


@router.get("/report/chart/category")
async def generate_category_chart(
    year: int = Query(..., ge=2000, le=2100),
    month: Optional[int] = Query(None, ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Generate category pie chart"""
    generator = ReportGenerator(db)
    
    try:
        chart_path = generator.generate_category_chart(year, month)
        
        if not chart_path or not chart_path.exists():
            raise HTTPException(status_code=404, detail="No data available for chart")
        
        return FileResponse(
            chart_path,
            media_type="image/png",
            filename=chart_path.name
        )
        
    except Exception as e:
        logger.error(f"Failed to generate chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/chart/trend")
async def generate_trend_chart(
    year: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db)
):
    """Generate monthly trend chart"""
    generator = ReportGenerator(db)
    
    try:
        chart_path = generator.generate_trend_chart(year)
        
        if not chart_path or not chart_path.exists():
            raise HTTPException(status_code=404, detail="No data available for chart")
        
        return FileResponse(
            chart_path,
            media_type="image/png",
            filename=chart_path.name
        )
        
    except Exception as e:
        logger.error(f"Failed to generate trend chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/export/csv")
async def export_csv(
    year: int = Query(..., ge=2000, le=2100),
    month: Optional[int] = Query(None, ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Export purchases to CSV"""
    generator = ReportGenerator(db)
    
    try:
        csv_path = generator.export_to_csv(year, month)
        
        if not csv_path or not csv_path.exists():
            raise HTTPException(status_code=404, detail="No data available for export")
        
        return FileResponse(
            csv_path,
            media_type="text/csv",
            filename=csv_path.name
        )
        
    except Exception as e:
        logger.error(f"Failed to export CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

