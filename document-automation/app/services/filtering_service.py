"""
フィルタリングサービス
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.document import Document

logger = logging.getLogger(__name__)


class FilteringService:
    """フィルタリングサービス"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def apply_filters(self, filters: Dict[str, Any]) -> List[int]:
        """
        フィルタ条件を適用して文書IDリストを取得
        
        Args:
            filters: フィルタ条件の辞書
            
        Returns:
            フィルタ済み文書IDのリスト
        """
        try:
            query = self.db.query(Document)
            
            # 処理済み文書のみ対象
            query = query.filter(Document.status == "completed")
            
            # カテゴリ絞り込み
            if filters.get("categories"):
                query = query.filter(Document.category.in_(filters["categories"]))
            
            # 日付範囲絞り込み
            if filters.get("date_range"):
                date_range = filters["date_range"]
                if date_range.get("start"):
                    start_date = datetime.fromisoformat(date_range["start"])
                    query = query.filter(Document.created_at >= start_date)
                if date_range.get("end"):
                    end_date = datetime.fromisoformat(date_range["end"])
                    query = query.filter(Document.created_at <= end_date)
            
            # ファイル形式絞り込み
            if filters.get("file_types"):
                query = query.filter(Document.file_type.in_(filters["file_types"]))
            
            # キーワード絞り込み
            if filters.get("keywords"):
                keyword_conditions = []
                for keyword in filters["keywords"]:
                    keyword_conditions.append(
                        Document.keywords.contains([keyword])
                    )
                if keyword_conditions:
                    query = query.filter(or_(*keyword_conditions))
            
            # 特定文書指定
            if filters.get("document_ids"):
                query = query.filter(Document.id.in_(filters["document_ids"]))
            
            # メタデータ絞り込み
            if filters.get("metadata_filters"):
                metadata_filters = filters["metadata_filters"]
                for key, value in metadata_filters.items():
                    if isinstance(value, dict):
                        # 範囲指定（例: {"min": 1000, "max": 5000}）
                        if "min" in value:
                            query = query.filter(
                                Document.extracted_metadata[key].astext.cast(float) >= value["min"]
                            )
                        if "max" in value:
                            query = query.filter(
                                Document.extracted_metadata[key].astext.cast(float) <= value["max"]
                            )
                    else:
                        # 完全一致
                        query = query.filter(
                            Document.extracted_metadata[key].astext == str(value)
                        )
            
            # アーカイブされていない文書のみ
            query = query.filter(Document.is_archived == False)
            
            # 結果取得
            documents = query.all()
            document_ids = [doc.id for doc in documents]
            
            logger.info(f"Filtered {len(document_ids)} documents")
            return document_ids
            
        except Exception as e:
            logger.error(f"Failed to apply filters: {e}")
            return []
    
    def get_available_categories(self) -> List[str]:
        """利用可能なカテゴリ一覧を取得"""
        try:
            categories = self.db.query(Document.category).filter(
                Document.status == "completed",
                Document.category.isnot(None),
                Document.is_archived == False
            ).distinct().all()
            
            return [cat[0] for cat in categories if cat[0]]
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []
    
    def get_available_file_types(self) -> List[str]:
        """利用可能なファイル形式一覧を取得"""
        try:
            file_types = self.db.query(Document.file_type).filter(
                Document.status == "completed",
                Document.file_type.isnot(None),
                Document.is_archived == False
            ).distinct().all()
            
            return [ft[0] for ft in file_types if ft[0]]
        except Exception as e:
            logger.error(f"Failed to get file types: {e}")
            return []
    
    def get_available_keywords(self, limit: int = 50) -> List[str]:
        """利用可能なキーワード一覧を取得"""
        try:
            # キーワードを展開して取得
            documents = self.db.query(Document.keywords).filter(
                Document.status == "completed",
                Document.keywords.isnot(None),
                Document.is_archived == False
            ).all()
            
            keywords = set()
            for doc_keywords in documents:
                if doc_keywords[0]:
                    keywords.update(doc_keywords[0])
            
            return list(keywords)[:limit]
        except Exception as e:
            logger.error(f"Failed to get keywords: {e}")
            return []
    
    def get_document_metadata(self, document_id: int) -> Optional[Dict[str, Any]]:
        """特定文書のメタデータを取得"""
        try:
            document = self.db.query(Document).filter(
                Document.id == document_id,
                Document.status == "completed"
            ).first()
            
            if document:
                return {
                    "id": document.id,
                    "filename": document.filename,
                    "category": document.category,
                    "file_type": document.file_type,
                    "created_at": document.created_at,
                    "keywords": document.keywords or [],
                    "metadata": document.extracted_metadata or {},
                    "summary": document.summary
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document metadata: {e}")
            return None




