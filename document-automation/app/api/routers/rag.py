"""
RAG機能のAPIルーター
"""
import logging
import time
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.services.rag_service import RAGService
from app.models.document import RAGQuery, RAGSource, VectorIndex

logger = logging.getLogger(__name__)

# ファイルがインポートされた時点でログ出力
logger.info("=== rag.py モジュールがインポートされました ===")

# ルーター作成前
logger.info("RAGルーター作成開始")
router = APIRouter(tags=["RAG"])
logger.info("RAGルーター作成完了")


# Pydanticモデル
class DocumentFilters(BaseModel):
    """文書フィルタ条件"""
    categories: Optional[List[str]] = None
    file_types: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    document_ids: Optional[List[int]] = None
    date_range: Optional[Dict[str, str]] = None
    metadata_filters: Optional[Dict[str, Any]] = None


class RAGQueryRequest(BaseModel):
    """RAG質問リクエスト"""
    query: str
    filters: Optional[DocumentFilters] = None
    limit: int = 5
    similarity_threshold: float = 0.7


class RAGQueryResponse(BaseModel):
    """RAG質問レスポンス"""
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    query_id: int


class SearchRequest(BaseModel):
    """検索リクエスト"""
    query: str
    filters: Optional[DocumentFilters] = None
    limit: int = 10
    similarity_threshold: float = 0.7


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(
    request: RAGQueryRequest,
    db: Session = Depends(get_db)
):
    """
    RAG質問応答
    
    自然言語での質問に対して、関連文書を検索して回答を生成します。
    """
    try:
        start_time = time.time()
        
        # RAGサービス初期化
        rag_service = RAGService(db)
        
        # フィルタ条件の変換
        filters_dict = None
        if request.filters:
            filters_dict = request.filters.dict(exclude_none=True)
        
        # RAG処理実行
        result = await rag_service.query_with_filters(
            query=request.query,
            filters=filters_dict,
            limit=request.limit,
            similarity_threshold=request.similarity_threshold
        )
        
        processing_time = time.time() - start_time
        
        # クエリ履歴を保存
        query_record = RAGQuery(
            query_text=request.query,
            query_type="question",
            filters=filters_dict,
            answer=result["answer"],
            sources_count=len(result["sources"]),
            similarity_threshold=request.similarity_threshold,
            processing_time=processing_time
        )
        db.add(query_record)
        db.commit()
        db.refresh(query_record)
        
        # ソース情報を保存
        for i, source in enumerate(result["sources"]):
            source_record = RAGSource(
                query_id=query_record.id,
                document_id=source["document_id"],
                similarity_score=source["score"],
                rank=i + 1,
                filename=source["filename"],
                category=source["category"],
                text_preview=source["text_preview"]
            )
            db.add(source_record)
        
        db.commit()
        
        # レスポンス作成
        response = RAGQueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            metadata={
                **result["metadata"],
                "processing_time": processing_time
            },
            query_id=query_record.id
        )
        
        logger.info(f"RAG query completed: {query_record.id}")
        return response
        
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")


@router.post("/search")
async def search_similar_documents(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    類似文書検索
    
    クエリに類似した文書を検索します。
    """
    try:
        # RAGサービス初期化
        rag_service = RAGService(db)
        
        # フィルタ条件の変換
        filters_dict = None
        if request.filters:
            filters_dict = request.filters.dict(exclude_none=True)
        
        # 類似文書検索
        results = await rag_service.search_similar_documents(
            query=request.query,
            filters=filters_dict,
            limit=request.limit,
            similarity_threshold=request.similarity_threshold
        )
        
        logger.info(f"Found {len(results)} similar documents")
        return {
            "results": results,
            "total_count": len(results),
            "query": request.query,
            "filters": filters_dict
        }
        
    except Exception as e:
        logger.error(f"Similar document search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/filters")
async def get_available_filters(db: Session = Depends(get_db)):
    """利用可能なフィルタ情報を取得"""
    logger.info("RAGフィルターエンドポイントが呼ばれました")
    """
    利用可能なフィルタ情報を取得
    
    カテゴリ、ファイル形式、キーワード等の利用可能なフィルタ条件を返します。
    """
    try:
        rag_service = RAGService(db)
        filters = rag_service.get_available_filters()
        
        return {
            "filters": filters,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to get available filters: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get filters: {str(e)}")


@router.get("/queries")
async def get_query_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    クエリ履歴を取得
    
    過去のRAGクエリ履歴を取得します。
    """
    try:
        queries = db.query(RAGQuery).order_by(
            RAGQuery.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return {
            "queries": [
                {
                    "id": q.id,
                    "query_text": q.query_text,
                    "query_type": q.query_type,
                    "sources_count": q.sources_count,
                    "processing_time": q.processing_time,
                    "created_at": q.created_at
                }
                for q in queries
            ],
            "total_count": db.query(RAGQuery).count(),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to get query history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get query history: {str(e)}")


@router.get("/queries/{query_id}")
async def get_query_details(
    query_id: int,
    db: Session = Depends(get_db)
):
    """
    クエリ詳細を取得
    
    特定のクエリの詳細情報とソースを取得します。
    """
    try:
        # クエリ情報取得
        query = db.query(RAGQuery).filter(RAGQuery.id == query_id).first()
        if not query:
            raise HTTPException(status_code=404, detail="Query not found")
        
        # ソース情報取得
        sources = db.query(RAGSource).filter(
            RAGSource.query_id == query_id
        ).order_by(RAGSource.rank).all()
        
        return {
            "query": {
                "id": query.id,
                "query_text": query.query_text,
                "query_type": query.query_type,
                "filters": query.filters,
                "answer": query.answer,
                "sources_count": query.sources_count,
                "similarity_threshold": query.similarity_threshold,
                "processing_time": query.processing_time,
                "created_at": query.created_at
            },
            "sources": [
                {
                    "document_id": s.document_id,
                    "similarity_score": s.similarity_score,
                    "rank": s.rank,
                    "filename": s.filename,
                    "category": s.category,
                    "text_preview": s.text_preview
                }
                for s in sources
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get query details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get query details: {str(e)}")


@router.get("/index/status")
async def get_index_status(db: Session = Depends(get_db)):
    """
    ベクトルインデックスの状態を取得
    
    ベクトル化済み文書数やインデックス状態を取得します。
    """
    try:
        # インデックス統計
        total_documents = db.query(VectorIndex).count()
        indexed_documents = db.query(VectorIndex).filter(
            VectorIndex.is_indexed == True
        ).count()
        failed_documents = db.query(VectorIndex).filter(
            VectorIndex.error_message.isnot(None)
        ).count()
        
        return {
            "total_documents": total_documents,
            "indexed_documents": indexed_documents,
            "failed_documents": failed_documents,
            "indexing_rate": indexed_documents / total_documents if total_documents > 0 else 0,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to get index status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get index status: {str(e)}")


@router.post("/index/rebuild")
async def rebuild_index(db: Session = Depends(get_db)):
    """
    ベクトルインデックスの再構築
    
    全文書のベクトル化を再実行します。
    """
    try:
        # TODO: 実際の再構築処理を実装
        # これはCeleryタスクとして実装する予定
        
        return {
            "message": "Index rebuild task started",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to rebuild index: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rebuild index: {str(e)}")


# ルーター登録完了の確認
logger.info(f"=== RAGルーター: {len(router.routes)}個のエンドポイント登録済み ===")
for route in router.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        logger.info(f"  - {route.methods} {route.path}")
