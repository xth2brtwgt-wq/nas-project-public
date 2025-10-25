"""CSV parsing service for Amazon order history"""
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class AmazonCSVParser:
    """Parser for Amazon order history CSV files"""
    
    def __init__(self):
        self.supported_formats = [
            "Retail.OrderHistory",  # Main retail orders
            "Digital Orders",       # Digital purchases
        ]
    
    def parse_retail_order_history(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse Retail.OrderHistory.3.csv format
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of parsed order dictionaries
        """
        try:
            # Read CSV with proper encoding
            df = pd.read_csv(file_path, encoding='utf-8')
            
            logger.info(f"Loaded {len(df)} rows from {file_path.name}")
            
            orders = []
            for idx, row in df.iterrows():
                try:
                    order = self._parse_retail_row(row)
                    if order:
                        orders.append(order)
                except Exception as e:
                    logger.warning(f"Failed to parse row {idx}: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(orders)} orders")
            return orders
            
        except Exception as e:
            logger.error(f"Failed to parse CSV file: {e}")
            raise
    
    def _parse_retail_row(self, row: pd.Series) -> Optional[Dict[str, Any]]:
        """Parse a single retail order row"""
        
        # Skip if essential fields are missing
        if pd.isna(row.get('Order ID')) or pd.isna(row.get('Product Name')):
            return None
        
        # Parse order date
        order_date = self._parse_date(row.get('Order Date'))
        if not order_date:
            return None
        
        # Parse ship date (optional)
        ship_date = self._parse_date(row.get('Ship Date'))
        
        # Parse prices
        unit_price = self._parse_price(row.get('Unit Price', '0'))
        unit_price_tax = self._parse_price(row.get('Unit Price Tax', '0'))
        shipping_charge = self._parse_price(row.get('Shipping Charge', '0'))
        total_discounts = self._parse_price(row.get('Total Discounts', '0'))
        total_owed = self._parse_price(row.get('Total Owed', '0'))
        
        # Extract quantity
        quantity = int(row.get('Quantity', 1))
        
        order = {
            'order_id': str(row['Order ID']),
            'order_date': order_date,
            'product_name': str(row['Product Name']),
            'seller': str(row.get('Billing Address', 'Amazon')),
            'asin': str(row.get('ASIN', '')),
            'unit_price': unit_price,
            'unit_price_tax': unit_price_tax,
            'shipping_charge': shipping_charge,
            'total_discounts': abs(total_discounts),  # Make discounts positive
            'total_owed': total_owed,
            'quantity': quantity,
            'product_condition': str(row.get('Product Condition', 'New')),
            'order_status': str(row.get('Order Status', 'Unknown')),
            'shipment_status': str(row.get('Shipment Status', 'Unknown')),
            'ship_date': ship_date,
            'shipping_address': str(row.get('Shipping Address', '')),
            'billing_address': str(row.get('Billing Address', '')),
            'currency': str(row.get('Currency', 'JPY')),
            'website': str(row.get('Website', 'Amazon.co.jp')),
            'raw_data': row.to_dict(),
        }
        
        return order
    
    def _parse_date(self, date_str: Any) -> Optional[datetime]:
        """Parse date string to datetime"""
        if pd.isna(date_str) or date_str == 'Not Available':
            return None
        
        try:
            # Try ISO format first (2025-10-17T20:33:51.287Z)
            if 'T' in str(date_str):
                return pd.to_datetime(date_str, utc=True).replace(tzinfo=None)
            # Try standard format
            return pd.to_datetime(date_str)
        except Exception as e:
            logger.debug(f"Failed to parse date '{date_str}': {e}")
            return None
    
    def _parse_price(self, price_str: Any) -> float:
        """Parse price string to float"""
        if pd.isna(price_str) or price_str == 'Not Available':
            return 0.0
        
        try:
            # Remove currency symbols and commas
            price_str = str(price_str).replace('¥', '').replace(',', '').replace("'", '').strip()
            
            # Handle quotes in numbers
            if price_str.startswith("'") or price_str.startswith('"'):
                price_str = price_str[1:]
            if price_str.endswith("'") or price_str.endswith('"'):
                price_str = price_str[:-1]
            
            return float(price_str)
        except (ValueError, AttributeError) as e:
            logger.debug(f"Failed to parse price '{price_str}': {e}")
            return 0.0
    
    def detect_csv_format(self, file_path: Path) -> Optional[str]:
        """
        Detect the format of the CSV file
        
        Returns:
            Format name or None if unknown
        """
        try:
            # Read first row to check headers
            df = pd.read_csv(file_path, nrows=1)
            columns = set(df.columns)
            
            # Check for Retail.OrderHistory format
            if 'Order ID' in columns and 'Product Name' in columns and 'ASIN' in columns:
                return 'Retail.OrderHistory'
            
            # Check for Digital Orders format
            if 'OrderId' in columns and 'Marketplace' in columns:
                return 'Digital Orders'
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect CSV format: {e}")
            return None
    
    def get_order_summary(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary statistics for parsed orders"""
        if not orders:
            return {
                'total_orders': 0,
                'total_items': 0,
                'total_spent': 0,
                'date_range': None,
            }
        
        df = pd.DataFrame(orders)
        
        return {
            'total_orders': len(df['order_id'].unique()),
            'total_items': len(orders),
            'total_spent': float(df['total_owed'].sum()),
            'date_range': {
                'start': df['order_date'].min().isoformat() if not df['order_date'].isna().all() else None,
                'end': df['order_date'].max().isoformat() if not df['order_date'].isna().all() else None,
            },
            'unique_products': len(df['product_name'].unique()),
        }


# Create singleton instance
csv_parser = AmazonCSVParser()

