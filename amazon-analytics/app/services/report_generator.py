"""Report generation service"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.purchase import Purchase, Category
from config.settings import settings

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate reports and visualizations"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Set Japanese font for matplotlib
        try:
            plt.rcParams['font.family'] = 'DejaVu Sans'
        except:
            pass
    
    def generate_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        """
        Generate monthly spending report
        
        Args:
            year: Year
            month: Month
            
        Returns:
            Report data dictionary
        """
        # Date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Get purchases for the month
        purchases = self.db.query(Purchase)\
            .filter(and_(
                Purchase.order_date >= start_date,
                Purchase.order_date < end_date
            ))\
            .all()
        
        if not purchases:
            return {
                'period': f'{year}年{month}月',
                'total_spent': 0,
                'purchase_count': 0,
                'categories': {},
                'top_products': [],
            }
        
        # Calculate totals
        total_spent = sum(p.total_owed for p in purchases)
        
        # Category breakdown
        category_spending = defaultdict(float)
        for purchase in purchases:
            if purchase.category:
                category_spending[purchase.category.name] += purchase.total_owed
            else:
                category_spending['未分類'] += purchase.total_owed
        
        # Top products
        product_list = []
        for purchase in purchases:
            product_list.append({
                'name': purchase.product_name,
                'price': purchase.total_owed,
                'date': purchase.order_date,
                'category': purchase.category.name if purchase.category else '未分類',
            })
        
        product_list.sort(key=lambda x: x['price'], reverse=True)
        top_products = product_list[:10]
        
        # Calculate previous month comparison
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        prev_start = datetime(prev_year, prev_month, 1)
        prev_end = start_date
        
        prev_total = self.db.query(func.sum(Purchase.total_owed))\
            .filter(and_(
                Purchase.order_date >= prev_start,
                Purchase.order_date < prev_end
            )).scalar() or 0
        
        change_pct = 0
        if prev_total > 0:
            change_pct = ((total_spent - prev_total) / prev_total) * 100
        
        return {
            'period': f'{year}年{month}月',
            'total_spent': float(total_spent),
            'purchase_count': len(purchases),
            'unique_orders': len(set(p.order_id for p in purchases)),
            'categories': {
                k: float(v) for k, v in sorted(
                    category_spending.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            },
            'top_products': top_products,
            'comparison': {
                'previous_month': float(prev_total),
                'change_amount': float(total_spent - prev_total),
                'change_percentage': round(change_pct, 1),
            }
        }
    
    def generate_yearly_report(self, year: int) -> Dict[str, Any]:
        """
        Generate yearly spending report
        
        Args:
            year: Year
            
        Returns:
            Report data dictionary
        """
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
        
        # Get all purchases for the year
        purchases = self.db.query(Purchase)\
            .filter(and_(
                Purchase.order_date >= start_date,
                Purchase.order_date < end_date
            ))\
            .all()
        
        if not purchases:
            return {
                'year': year,
                'total_spent': 0,
                'monthly_breakdown': {},
                'categories': {},
                'top_products': [],
            }
        
        # Total spending
        total_spent = sum(p.total_owed for p in purchases)
        
        # Monthly breakdown
        monthly_spending = defaultdict(float)
        for purchase in purchases:
            month_key = purchase.order_date.strftime('%Y-%m')
            monthly_spending[month_key] += purchase.total_owed
        
        # Category totals
        category_totals = defaultdict(float)
        for purchase in purchases:
            if purchase.category:
                category_totals[purchase.category.name] += purchase.total_owed
            else:
                category_totals['未分類'] += purchase.total_owed
        
        # Top products (by frequency)
        product_counts = defaultdict(lambda: {'count': 0, 'total': 0, 'name': ''})
        for purchase in purchases:
            key = purchase.asin if purchase.asin else purchase.product_name[:50]
            product_counts[key]['count'] += 1
            product_counts[key]['total'] += purchase.total_owed
            product_counts[key]['name'] = purchase.product_name
        
        top_by_freq = sorted(
            product_counts.values(),
            key=lambda x: x['count'],
            reverse=True
        )[:10]
        
        return {
            'year': year,
            'total_spent': float(total_spent),
            'purchase_count': len(purchases),
            'unique_orders': len(set(p.order_id for p in purchases)),
            'monthly_breakdown': {
                k: float(v) for k, v in sorted(monthly_spending.items())
            },
            'categories': {
                k: float(v) for k, v in sorted(
                    category_totals.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            },
            'top_products_by_frequency': top_by_freq,
        }
    
    def generate_category_chart(
        self,
        year: int,
        month: Optional[int] = None,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate category pie chart
        
        Args:
            year: Year
            month: Month (optional, if None generates yearly chart)
            output_path: Output file path
            
        Returns:
            Path to generated chart
        """
        # Get data
        if month:
            report = self.generate_monthly_report(year, month)
            title = f'{year}年{month}月 カテゴリ別支出'
        else:
            report = self.generate_yearly_report(year)
            title = f'{year}年 カテゴリ別支出'
        
        categories = report['categories']
        
        if not categories:
            logger.warning("No data to generate chart")
            return None
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 8))
        
        labels = list(categories.keys())
        sizes = list(categories.values())
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90
        )
        
        # Enhance text
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_weight('bold')
        
        ax.set_title(title, fontsize=14, pad=20)
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        # Save chart
        if not output_path:
            filename = f'category_chart_{year}'
            if month:
                filename += f'_{month:02d}'
            filename += '.png'
            output_path = settings.EXPORT_DIR / filename
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Generated chart: {output_path}")
        return output_path
    
    def generate_trend_chart(self, year: int, output_path: Optional[Path] = None) -> Path:
        """
        Generate monthly spending trend chart
        
        Args:
            year: Year
            output_path: Output file path
            
        Returns:
            Path to generated chart
        """
        report = self.generate_yearly_report(year)
        monthly_data = report['monthly_breakdown']
        
        if not monthly_data:
            logger.warning("No data to generate trend chart")
            return None
        
        # Prepare data
        months = sorted(monthly_data.keys())
        values = [monthly_data[m] for m in months]
        
        # Create chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(range(len(months)), values, marker='o', linewidth=2, markersize=8)
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels([m.split('-')[1] + '月' for m in months])
        ax.set_ylabel('支出額 (円)', fontsize=12)
        ax.set_title(f'{year}年 月別支出推移', fontsize=14, pad=20)
        ax.grid(True, alpha=0.3)
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'¥{int(x):,}'))
        
        # Save chart
        if not output_path:
            output_path = settings.EXPORT_DIR / f'trend_chart_{year}.png'
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Generated trend chart: {output_path}")
        return output_path
    
    def export_to_csv(
        self,
        year: int,
        month: Optional[int] = None,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Export purchases to CSV
        
        Args:
            year: Year
            month: Month (optional)
            output_path: Output file path
            
        Returns:
            Path to generated CSV
        """
        # Build query
        start_date = datetime(year, month if month else 1, 1)
        
        if month:
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            filename = f'purchases_{year}_{month:02d}.csv'
        else:
            end_date = datetime(year + 1, 1, 1)
            filename = f'purchases_{year}.csv'
        
        # Get purchases
        purchases = self.db.query(Purchase)\
            .filter(and_(
                Purchase.order_date >= start_date,
                Purchase.order_date < end_date
            ))\
            .order_by(Purchase.order_date)\
            .all()
        
        if not purchases:
            logger.warning("No data to export")
            return None
        
        # Convert to DataFrame
        data = []
        for p in purchases:
            data.append({
                '注文日': p.order_date.strftime('%Y-%m-%d'),
                '注文番号': p.order_id,
                '商品名': p.product_name,
                'カテゴリ': p.category.name if p.category else '未分類',
                '単価': p.unit_price,
                '数量': p.quantity,
                '合計金額': p.total_owed,
                'ASIN': p.asin,
            })
        
        df = pd.DataFrame(data)
        
        # Save to CSV
        if not output_path:
            output_path = settings.EXPORT_DIR / filename
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        logger.info(f"Exported to CSV: {output_path}")
        return output_path

