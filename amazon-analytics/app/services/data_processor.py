"""Data processing and storage service"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.purchase import Purchase, ImportHistory, Category
from app.services.csv_parser import csv_parser

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and store purchase data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def import_csv_file(self, file_path: Path) -> ImportHistory:
        """
        Import CSV file and store in database
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            ImportHistory record
        """
        start_time = datetime.now()
        
        # Create import history record
        import_record = ImportHistory(
            filename=file_path.name,
            status='processing',
        )
        self.db.add(import_record)
        self.db.commit()
        
        try:
            # Detect format
            csv_format = csv_parser.detect_csv_format(file_path)
            if not csv_format:
                raise ValueError(f"Unknown CSV format: {file_path.name}")
            
            logger.info(f"Detected CSV format: {csv_format}")
            
            # Parse CSV
            if csv_format == 'Retail.OrderHistory':
                orders = csv_parser.parse_retail_order_history(file_path)
            else:
                raise ValueError(f"Unsupported format: {csv_format}")
            
            if not orders:
                raise ValueError("No valid orders found in CSV")
            
            # Store orders in database
            saved_count = self._store_orders(orders)
            
            # Update import record
            processing_time = (datetime.now() - start_time).total_seconds()
            import_record.record_count = saved_count
            import_record.status = 'success'
            import_record.processing_time = processing_time
            self.db.commit()
            
            logger.info(f"Successfully imported {saved_count} orders in {processing_time:.2f}s")
            return import_record
            
        except Exception as e:
            logger.error(f"Failed to import CSV: {e}")
            import_record.status = 'failed'
            import_record.error_message = str(e)
            self.db.commit()
            raise
    
    def _store_orders(self, orders: List[Dict[str, Any]]) -> int:
        """Store orders in database with deduplication"""
        saved_count = 0
        
        for order_data in orders:
            # Check if order already exists
            existing = self.db.query(Purchase).filter(
                Purchase.order_id == order_data['order_id'],
                Purchase.product_name == order_data['product_name'],
                Purchase.order_date == order_data['order_date'],
            ).first()
            
            if existing:
                logger.debug(f"Skipping duplicate order: {order_data['order_id']}")
                continue
            
            # Create new purchase record
            purchase = Purchase(**order_data)
            self.db.add(purchase)
            saved_count += 1
        
        self.db.commit()
        return saved_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        total_purchases = self.db.query(func.count(Purchase.id)).scalar()
        total_spent = self.db.query(func.sum(Purchase.total_owed)).scalar() or 0
        unique_orders = self.db.query(func.count(func.distinct(Purchase.order_id))).scalar()
        
        # Date range
        date_range = self.db.query(
            func.min(Purchase.order_date),
            func.max(Purchase.order_date)
        ).first()
        
        return {
            'total_purchases': total_purchases,
            'total_spent': float(total_spent),
            'unique_orders': unique_orders,
            'date_range': {
                'start': date_range[0].isoformat() if date_range[0] else None,
                'end': date_range[1].isoformat() if date_range[1] else None,
            }
        }
    
    def get_recent_purchases(self, limit: int = 10) -> List[Purchase]:
        """Get recent purchases"""
        return self.db.query(Purchase)\
            .order_by(Purchase.order_date.desc())\
            .limit(limit)\
            .all()
    
    def initialize_categories(self):
        """Initialize default categories"""
        default_categories = [
            {'name': '食品・飲料', 'name_en': 'Food & Beverage'},
            {'name': '日用品・消耗品', 'name_en': 'Daily Necessities'},
            {'name': '家電・PC関連', 'name_en': 'Electronics & PC'},
            {'name': '本・メディア', 'name_en': 'Books & Media'},
            {'name': 'ファッション', 'name_en': 'Fashion'},
            {'name': 'ホビー・趣味', 'name_en': 'Hobbies'},
            {'name': '健康・美容', 'name_en': 'Health & Beauty'},
            {'name': 'ペット用品', 'name_en': 'Pet Supplies'},
            {'name': 'その他', 'name_en': 'Other'},
        ]
        
        for cat_data in default_categories:
            existing = self.db.query(Category).filter(
                Category.name == cat_data['name']
            ).first()
            
            if not existing:
                category = Category(**cat_data)
                self.db.add(category)
        
        self.db.commit()
        logger.info("Initialized default categories")

