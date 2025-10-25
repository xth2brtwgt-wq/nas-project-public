"""Purchase-related database models"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Purchase(Base):
    """Purchase history table"""
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), nullable=False, index=True)
    order_date = Column(DateTime, nullable=False, index=True)
    product_name = Column(Text, nullable=False)
    seller = Column(String(500))
    asin = Column(String(20), index=True)
    
    # Prices
    unit_price = Column(Float, nullable=False)
    unit_price_tax = Column(Float, default=0)
    shipping_charge = Column(Float, default=0)
    total_discounts = Column(Float, default=0)
    total_owed = Column(Float, nullable=False)
    
    # Product info
    quantity = Column(Integer, default=1)
    product_condition = Column(String(50))
    
    # Status
    order_status = Column(String(50))
    shipment_status = Column(String(50))
    ship_date = Column(DateTime)
    
    # Category (AI classified)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="purchases")
    
    # Address
    shipping_address = Column(Text)
    billing_address = Column(Text)
    
    # Metadata
    currency = Column(String(10), default="JPY")
    website = Column(String(100), default="Amazon.co.jp")
    raw_data = Column(JSON)  # Store original CSV row
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Indexes for common queries
    __table_args__ = (
        Index('idx_order_date_category', 'order_date', 'category_id'),
        Index('idx_product_asin', 'asin'),
    )

    def __repr__(self):
        return f"<Purchase(id={self.id}, order_id={self.order_id}, product={self.product_name[:30]})>"


class Category(Base):
    """Product category master"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    name_en = Column(String(100))
    description = Column(Text)
    budget = Column(Float, default=0)  # Monthly budget
    
    purchases = relationship("Purchase", back_populates="category")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"


class AnalysisResult(Base):
    """Analysis results storage"""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_type = Column(String(50), nullable=False)  # monthly, yearly, pattern, etc.
    target_period = Column(String(50))  # e.g., "2025-10", "2025"
    result_data = Column(JSON, nullable=False)
    summary = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_analysis_type_period', 'analysis_type', 'target_period'),
    )

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, type={self.analysis_type}, period={self.target_period})>"


class ImportHistory(Base):
    """CSV import history"""
    __tablename__ = "import_history"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    import_date = Column(DateTime, server_default=func.now())
    record_count = Column(Integer, default=0)
    status = Column(String(50), nullable=False)  # success, failed, partial
    error_message = Column(Text)
    processing_time = Column(Float)  # seconds
    
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ImportHistory(id={self.id}, filename={self.filename}, status={self.status})>"

