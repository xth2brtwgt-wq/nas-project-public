"""
ベクトルストアサービス（Qdrant）
"""
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http import models
import uuid
from config.settings import settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """ベクトルストアサービス"""
    
    def __init__(self):
        self.client = None
        self.collection_name = "documents"
        self._initialize_client()
    
    def _initialize_client(self):
        """Qdrantクライアントの初期化"""
        try:
            # Qdrantクライアントの初期化
            self.client = QdrantClient(
                host="qdrant",
                port=6333,
                timeout=30
            )
            
            # コレクションの作成
            self._create_collection()
            logger.info("Qdrant client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            raise
    
    def _create_collection(self):
        """コレクションの作成"""
        try:
            # コレクションが存在するかチェック
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # コレクション作成
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI embedding dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def add_documents(
        self, 
        documents: List[Dict[str, Any]], 
        embeddings: List[List[float]]
    ) -> bool:
        """
        文書をベクトルストアに追加
        
        Args:
            documents: 文書メタデータのリスト
            embeddings: 対応するEmbeddingベクトル
            
        Returns:
            成功フラグ
        """
        try:
            points = []
            for doc, embedding in zip(documents, embeddings):
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "document_id": doc["id"],
                        "filename": doc["filename"],
                        "category": doc.get("category"),
                        "file_type": doc.get("file_type"),
                        "created_at": doc.get("created_at"),
                        "keywords": doc.get("keywords", []),
                        "metadata": doc.get("extracted_metadata", {}),
                        "text": doc.get("text", ""),
                        "summary": doc.get("summary", "")
                    }
                )
                points.append(point)
            
            # バッチで追加
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Added {len(points)} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")
            return False
    
    def search_similar(
        self, 
        query_embedding: List[float], 
        limit: int = 5,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        類似文書を検索
        
        Args:
            query_embedding: クエリのEmbedding
            limit: 取得件数
            score_threshold: 類似度閾値
            filters: フィルタ条件
            
        Returns:
            検索結果のリスト
        """
        try:
            # フィルタ条件の構築
            search_filter = None
            if filters:
                conditions = []
                
                if "categories" in filters:
                    conditions.append(
                        FieldCondition(
                            key="category",
                            match=MatchAny(any=filters["categories"])
                        )
                    )
                
                if "file_types" in filters:
                    conditions.append(
                        FieldCondition(
                            key="file_type",
                            match=MatchAny(any=filters["file_types"])
                        )
                    )
                
                if "document_ids" in filters:
                    # document_idsはリストなので、MatchAny条件を使用
                    conditions.append(
                        FieldCondition(
                            key="document_id",
                            match=MatchAny(any=filters["document_ids"])
                        )
                    )
                
                if conditions:
                    search_filter = Filter(must=conditions)
            
            # 検索実行
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter
            )
            
            # 結果の整形
            results = []
            for result in search_results:
                results.append({
                    "id": result.id,
                    "score": result.score,
                    "document_id": result.payload.get("document_id"),
                    "filename": result.payload.get("filename"),
                    "category": result.payload.get("category"),
                    "text": result.payload.get("text"),
                    "summary": result.payload.get("summary"),
                    "metadata": result.payload.get("metadata", {}),
                    "keywords": result.payload.get("keywords", [])
                })
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            return []
    
    def delete_document(self, document_id: int) -> bool:
        """文書を削除"""
        try:
            # フィルタで文書を特定して削除
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
            
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=filter_condition
            )
            
            logger.info(f"Deleted document {document_id} from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """コレクション情報を取得"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}


# シングルトンインスタンス
vector_store_service = VectorStoreService()
