"""AI-powered analysis service using Gemini or OpenAI"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from collections import defaultdict, Counter

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.purchase import Purchase, Category, AnalysisResult
from config.settings import settings

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI-powered purchase analysis (supports Gemini and OpenAI)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_provider = settings.AI_PROVIDER
        self.client = None
        self.gemini_model = None
        
        # Initialize AI provider
        if self.ai_provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
                logger.info(f"Using Gemini AI: {settings.GEMINI_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.gemini_model = None
        elif self.ai_provider == "openai" and settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info(f"Using OpenAI: {settings.OPENAI_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
                self.client = None
        
        if not self.gemini_model and not self.client:
            logger.warning("No AI provider configured. AI features will not work.")
    
    def classify_product_category(self, product_name: str) -> Optional[str]:
        """
        Classify product into category using AI
        
        Args:
            product_name: Product name
            
        Returns:
            Category name in Japanese
        """
        categories = self.db.query(Category).all()
        category_list = [cat.name for cat in categories]
        
        prompt = f"""以下の商品を適切なカテゴリに分類してください。

商品名: {product_name}

利用可能なカテゴリ:
{', '.join(category_list)}

商品の内容を理解し、最も適切なカテゴリ名を1つだけ返してください。
カテゴリ名のみを返し、他の説明は不要です。"""

        try:
            if self.gemini_model:
                # Gemini API
                response = self.gemini_model.generate_content(prompt)
                category_name = response.text.strip()
            elif self.client:
                # OpenAI API
                response = self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "あなたは商品分類の専門家です。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=50,
                )
                category_name = response.choices[0].message.content.strip()
            else:
                logger.warning("No AI provider available")
                return 'その他'
            
            # Validate category exists
            category = self.db.query(Category).filter(
                Category.name == category_name
            ).first()
            
            if category:
                return category_name
            else:
                logger.warning(f"AI returned unknown category: {category_name}")
                return 'その他'
                
        except Exception as e:
            logger.error(f"Failed to classify product: {e}")
            return 'その他'
    
    def auto_classify_purchases(self, limit: Optional[int] = None):
        """Auto-classify purchases without categories"""
        import time
        
        query = self.db.query(Purchase).filter(Purchase.category_id.is_(None))
        
        if limit:
            query = query.limit(limit)
        
        purchases = query.all()
        
        logger.info(f"Auto-classifying {len(purchases)} purchases using {self.ai_provider}")
        
        classified_count = 0
        consecutive_errors = 0
        max_consecutive_errors = 5  # Stop after 5 consecutive errors
        
        for i, purchase in enumerate(purchases):
            try:
                category_name = self.classify_product_category(purchase.product_name)
                category = self.db.query(Category).filter(
                    Category.name == category_name
                ).first()
                
                if category:
                    purchase.category_id = category.id
                    classified_count += 1
                    consecutive_errors = 0  # Reset error counter on success
                
                # Rate limiting: Wait 4 seconds between requests (15 req/min)
                if (i + 1) % 10 == 0:
                    logger.info(f"Classified {i + 1}/{len(purchases)}, pausing to respect rate limits...")
                    time.sleep(4)
                    
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Failed to classify {purchase.product_name}: {e}")
                
                # Stop if too many consecutive errors
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(f"Too many consecutive errors ({consecutive_errors}), stopping classification")
                    break
                
                # If rate limit error, wait longer
                if "429" in str(e) or "quota" in str(e).lower():
                    # Check if it's daily quota limit (more comprehensive check)
                    error_str = str(e)
                    logger.info(f"Error string: {error_str[:200]}...")  # Debug log
                    
                    # More specific check for daily quota
                    is_daily_quota = (
                        "GenerateRequestsPerDayPerProjectPerModel" in error_str or
                        "FreeTier" in error_str or
                        "limit: 50" in error_str or
                        "quota_value: 50" in error_str
                    )
                    
                    if is_daily_quota:
                        logger.error("Daily quota limit reached. Stopping classification.")
                        logger.error("Please wait until tomorrow or upgrade to a paid plan.")
                        break
                    
                    # Extract retry delay from error message if available
                    retry_delay = 60  # Default fallback
                    if "retry_delay" in str(e):
                        try:
                            import re
                            delay_match = re.search(r'retry_delay.*?(\d+)', str(e))
                            if delay_match:
                                retry_delay = int(delay_match.group(1))
                        except:
                            pass
                    
                    logger.warning(f"Rate limit hit, waiting {retry_delay} seconds...")
                    time.sleep(retry_delay)
                continue
        
        self.db.commit()
        logger.info(f"Auto-classification complete: {classified_count}/{len(purchases)} successful")
    
    def analyze_impulse_buying(self, days: int = 7) -> Dict[str, Any]:
        """
        Detect impulse buying patterns
        
        Args:
            days: Time window for impulse detection
            
        Returns:
            Analysis results
        """
        cutoff_date = datetime.now() - timedelta(days=30)
        
        purchases = self.db.query(Purchase)\
            .filter(Purchase.order_date >= cutoff_date)\
            .order_by(Purchase.order_date)\
            .all()
        
        # Group by category and week
        category_purchases = defaultdict(list)
        for purchase in purchases:
            if purchase.category:
                week = purchase.order_date.isocalendar()[1]
                category_purchases[purchase.category.name].append({
                    'week': week,
                    'date': purchase.order_date,
                    'amount': purchase.total_owed,
                    'product': purchase.product_name,
                })
        
        impulse_patterns = []
        
        # Detect patterns
        for category, items in category_purchases.items():
            # Check for multiple purchases in short period
            weekly_counts = Counter(item['week'] for item in items)
            
            for week, count in weekly_counts.items():
                if count >= settings.IMPULSE_BUY_COUNT:
                    week_items = [item for item in items if item['week'] == week]
                    total_amount = sum(item['amount'] for item in week_items)
                    
                    impulse_patterns.append({
                        'category': category,
                        'week': week,
                        'purchase_count': count,
                        'total_amount': total_amount,
                        'products': [item['product'] for item in week_items],
                    })
        
        return {
            'detected_patterns': impulse_patterns,
            'pattern_count': len(impulse_patterns),
            'analysis_date': datetime.now().isoformat(),
        }
    
    def analyze_recurring_purchases(self, min_occurrences: int = 3) -> List[Dict[str, Any]]:
        """
        Detect recurring purchase patterns
        
        Args:
            min_occurrences: Minimum number of purchases to consider recurring
            
        Returns:
            List of recurring purchase patterns
        """
        # Get purchases with similar product names
        cutoff_date = datetime.now() - timedelta(days=180)
        
        purchases = self.db.query(Purchase)\
            .filter(Purchase.order_date >= cutoff_date)\
            .order_by(Purchase.product_name, Purchase.order_date)\
            .all()
        
        # Group by similar product names (simplified)
        product_groups = defaultdict(list)
        for purchase in purchases:
            # Use ASIN for exact matching, or first 50 chars for similarity
            key = purchase.asin if purchase.asin else purchase.product_name[:50]
            product_groups[key].append(purchase)
        
        recurring = []
        
        for key, items in product_groups.items():
            if len(items) >= min_occurrences:
                # Calculate average interval
                dates = sorted([item.order_date for item in items])
                intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    
                    recurring.append({
                        'product_name': items[0].product_name,
                        'asin': items[0].asin,
                        'purchase_count': len(items),
                        'avg_interval_days': round(avg_interval, 1),
                        'total_spent': sum(item.total_owed for item in items),
                        'last_purchase': max(item.order_date for item in items).isoformat(),
                    })
        
        # Sort by purchase count
        recurring.sort(key=lambda x: x['purchase_count'], reverse=True)
        
        return recurring
    
    def generate_monthly_insights(self, year: int, month: int) -> str:
        """
        Generate AI-powered insights for a specific month
        
        Args:
            year: Year
            month: Month
            
        Returns:
            Generated insights text
        """
        if not self.gemini_model and not self.client:
            return "AI APIが設定されていません。設定ファイルでGEMINI_API_KEYまたはOPENAI_API_KEYを設定してください。"
        
        # Get monthly data
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        purchases = self.db.query(Purchase)\
            .filter(and_(
                Purchase.order_date >= start_date,
                Purchase.order_date < end_date
            ))\
            .all()
        
        if not purchases:
            return f"{year}年{month}月は購入がありませんでした。"
        
        # Aggregate data
        total_spent = sum(p.total_owed for p in purchases)
        category_spending = defaultdict(float)
        top_products = []
        
        for purchase in purchases:
            if purchase.category:
                category_spending[purchase.category.name] += purchase.total_owed
            top_products.append({
                'name': purchase.product_name,
                'price': purchase.total_owed
            })
        
        # Sort categories by spending
        top_categories = sorted(
            category_spending.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Sort products by price
        top_products.sort(key=lambda x: x['price'], reverse=True)
        top_products = top_products[:5]
        
        # Create prompt
        prompt = f"""以下は{year}年{month}月のAmazon購入データです。このデータを分析し、節約のためのアドバイスを含む洞察を提供してください。

総支出額: ¥{total_spent:,.0f}
購入件数: {len(purchases)}件

カテゴリ別支出（上位5件）:
{chr(10).join([f'- {cat}: ¥{amount:,.0f}' for cat, amount in top_categories])}

高額購入商品（上位5件）:
{chr(10).join([f'- {prod["name"][:50]}: ¥{prod["price"]:,.0f}' for prod in top_products])}

以下の観点で分析してください:
1. 支出パターンの特徴
2. 気づいた点や注意点
3. 節約のための具体的なアドバイス
4. おすすめの改善案

簡潔で読みやすい形式で、3-5つのポイントにまとめてください。"""

        try:
            if self.gemini_model:
                # Gemini API
                response = self.gemini_model.generate_content(prompt)
                return response.text.strip()
            elif self.client:
                # OpenAI API
                response = self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "あなたは家計管理の専門家です。購買データを分析し、実用的なアドバイスを提供します。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                )
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return f"月次分析の生成中にエラーが発生しました: {str(e)}"
    
    def save_analysis_result(
        self,
        analysis_type: str,
        target_period: str,
        result_data: Dict[str, Any],
        summary: Optional[str] = None
    ):
        """Save analysis result to database"""
        result = AnalysisResult(
            analysis_type=analysis_type,
            target_period=target_period,
            result_data=result_data,
            summary=summary,
        )
        self.db.add(result)
        self.db.commit()
        
        logger.info(f"Saved analysis result: {analysis_type} - {target_period}")
