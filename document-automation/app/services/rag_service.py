"""
RAG（Retrieval-Augmented Generation）サービス
"""
import logging
from typing import List, Dict, Any, Optional
from app.services.embedding_service import embedding_service
from app.services.vector_store_service import vector_store_service
from app.services.filtering_service import FilteringService
from app.services.ai_service import ai_service
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class RAGService:
    """RAGサービス"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.filtering_service = FilteringService(db_session)
    
    async def query_with_filters(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        フィルタ付きRAG質問応答
        
        Args:
            query: ユーザーの質問
            filters: フィルタ条件
            limit: 取得文書数
            similarity_threshold: 類似度閾値
            
        Returns:
            RAG結果（回答、引用元等）
        """
        try:
            # 1. フィルタ適用
            filtered_doc_ids = []
            if filters:
                filtered_doc_ids = self.filtering_service.apply_filters(filters)
                if not filtered_doc_ids:
                    return {
                        "answer": "指定された条件に合致する文書が見つかりませんでした。",
                        "sources": [],
                        "metadata": {"filtered_count": 0}
                    }
            
            # 2. クエリのEmbedding生成
            query_embedding = embedding_service.generate_single_embedding(query, use_openai=False)
            
            # 3. ベクトル検索
            search_filters = {}
            if filtered_doc_ids:
                search_filters["document_ids"] = filtered_doc_ids
            
            similar_docs = vector_store_service.search_similar(
                query_embedding=query_embedding,
                limit=limit,
                score_threshold=similarity_threshold,
                filters=search_filters
            )
            
            if not similar_docs:
                return {
                    "answer": "関連する文書が見つかりませんでした。",
                    "sources": [],
                    "metadata": {"similarity_threshold": similarity_threshold}
                }
            
            # 4. コンテキスト構築
            context = self._build_context(similar_docs)
            
            # 5. LLMによる回答生成
            answer = await self._generate_answer(query, context, similar_docs)
            
            # 6. 結果整形
            result = {
                "answer": answer,
                "sources": [
                    {
                        "document_id": doc["document_id"],
                        "filename": doc["filename"],
                        "category": doc["category"],
                        "score": doc["score"],
                        "text_preview": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"]
                    }
                    for doc in similar_docs
                ],
                "metadata": {
                    "total_sources": len(similar_docs),
                    "filtered_count": len(filtered_doc_ids) if filtered_doc_ids else "all",
                    "similarity_threshold": similarity_threshold
                }
            }
            
            logger.info(f"RAG query completed: {len(similar_docs)} sources found")
            return result
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return {
                "answer": "エラーが発生しました。しばらく時間をおいて再度お試しください。",
                "sources": [],
                "metadata": {"error": str(e)}
            }
    
    async def search_similar_documents(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        類似文書検索
        
        Args:
            query: 検索クエリ
            filters: フィルタ条件
            limit: 取得件数
            similarity_threshold: 類似度閾値
            
        Returns:
            類似文書のリスト
        """
        try:
            # 1. フィルタ適用
            filtered_doc_ids = []
            if filters:
                filtered_doc_ids = self.filtering_service.apply_filters(filters)
                if not filtered_doc_ids:
                    return []
            
            # 2. クエリのEmbedding生成
            query_embedding = embedding_service.generate_single_embedding(query, use_openai=False)
            
            # 3. ベクトル検索
            search_filters = {}
            if filtered_doc_ids:
                search_filters["document_ids"] = filtered_doc_ids
            
            similar_docs = vector_store_service.search_similar(
                query_embedding=query_embedding,
                limit=limit,
                score_threshold=similarity_threshold,
                filters=search_filters
            )
            
            logger.info(f"Found {len(similar_docs)} similar documents")
            return similar_docs
            
        except Exception as e:
            logger.error(f"Similar document search failed: {e}")
            return []
    
    def _build_context(self, similar_docs: List[Dict[str, Any]]) -> str:
        """検索結果からコンテキストを構築"""
        context_parts = []
        
        for i, doc in enumerate(similar_docs, 1):
            context_part = f"""
文書{i}: {doc['filename']}
カテゴリ: {doc['category']}
関連度: {doc['score']:.3f}
内容: {doc['text'][:500]}...
"""
            if doc.get('summary'):
                context_part += f"要約: {doc['summary']}\n"
            
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    async def _generate_answer(
        self, 
        query: str, 
        context: str, 
        sources: List[Dict[str, Any]]
    ) -> str:
        """LLMによる回答生成"""
        try:
            prompt = f"""
以下の文書を参考にして、ユーザーの質問に答えてください。

質問: {query}

参考文書:
{context}

回答の際は以下の点に注意してください:
1. 参考文書の内容に基づいて回答してください
2. 不確実な情報は推測ではなく「文書に記載がありません」と明記してください
3. 回答の根拠となる文書名を明記してください
4. 日本語で回答してください
"""
            
            answer = await ai_service.generate_summary(prompt)
            return answer
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return "回答の生成に失敗しました。"
    
    def get_available_filters(self) -> Dict[str, Any]:
        """利用可能なフィルタ情報を取得"""
        try:
            return {
                "categories": self.filtering_service.get_available_categories(),
                "file_types": self.filtering_service.get_available_file_types(),
                "keywords": self.filtering_service.get_available_keywords(),
                "collection_info": vector_store_service.get_collection_info()
            }
        except Exception as e:
            logger.error(f"Failed to get available filters: {e}")
            return {}
