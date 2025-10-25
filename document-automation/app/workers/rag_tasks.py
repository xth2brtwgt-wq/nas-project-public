"""
RAG関連のCeleryタスク
"""
import logging
from typing import List, Dict, Any
from celery import Celery
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.document import Document, VectorIndex
from app.services.embedding_service import embedding_service
from app.services.vector_store_service import vector_store_service
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def index_document_to_vector(self, document_id: int):
    """
    単一文書をベクトル化してQdrantに登録
    
    Args:
        document_id: 文書ID
    """
    try:
        db = SessionLocal()
        
        # 文書情報取得
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error(f"Document {document_id} not found")
            return {"status": "error", "message": "Document not found"}
        
        if document.status != "completed":
            logger.warning(f"Document {document_id} is not completed yet")
            return {"status": "skipped", "message": "Document not completed"}
        
        # 既存のベクトルインデックスをチェック
        existing_index = db.query(VectorIndex).filter(
            VectorIndex.document_id == document_id
        ).first()
        
        if existing_index and existing_index.is_indexed:
            logger.info(f"Document {document_id} already indexed")
            return {"status": "skipped", "message": "Already indexed"}
        
        # テキスト準備
        text_content = ""
        if document.ocr_text:
            text_content += document.ocr_text
        if document.summary:
            text_content += f"\n\n要約: {document.summary}"
        
        if not text_content.strip():
            logger.warning(f"Document {document_id} has no text content")
            return {"status": "skipped", "message": "No text content"}
        
        # Embedding生成
        embedding = embedding_service.generate_single_embedding(text_content)
        
        # 文書データ準備
        doc_data = {
            "id": document.id,
            "filename": document.filename,
            "category": document.category,
            "file_type": document.file_type,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "keywords": document.keywords or [],
            "extracted_metadata": document.extracted_metadata or {},
            "text": text_content,
            "summary": document.summary
        }
        
        # Qdrantに登録
        success = vector_store_service.add_documents([doc_data], [embedding])
        
        if success:
            # ベクトルインデックス情報を保存
            if existing_index:
                existing_index.is_indexed = True
                existing_index.vector_id = f"doc_{document_id}"
                existing_index.embedding_model = "text-embedding-3-small"
                existing_index.embedding_dimension = len(embedding)
                existing_index.error_message = None
            else:
                vector_index = VectorIndex(
                    document_id=document_id,
                    vector_id=f"doc_{document_id}",
                    embedding_model="text-embedding-3-small",
                    embedding_dimension=len(embedding),
                    is_indexed=True
                )
                db.add(vector_index)
            
            db.commit()
            logger.info(f"Successfully indexed document {document_id}")
            return {"status": "success", "document_id": document_id}
        else:
            # エラー情報を保存
            if existing_index:
                existing_index.error_message = "Failed to add to vector store"
            else:
                vector_index = VectorIndex(
                    document_id=document_id,
                    is_indexed=False,
                    error_message="Failed to add to vector store"
                )
                db.add(vector_index)
            
            db.commit()
            logger.error(f"Failed to index document {document_id}")
            return {"status": "error", "message": "Failed to add to vector store"}
            
    except Exception as e:
        logger.error(f"Error indexing document {document_id}: {e}")
        
        # エラー情報を保存
        try:
            db = SessionLocal()
            existing_index = db.query(VectorIndex).filter(
                VectorIndex.document_id == document_id
            ).first()
            
            if existing_index:
                existing_index.error_message = str(e)
            else:
                vector_index = VectorIndex(
                    document_id=document_id,
                    is_indexed=False,
                    error_message=str(e)
                )
                db.add(vector_index)
            
            db.commit()
        except Exception as db_error:
            logger.error(f"Failed to save error info: {db_error}")
        
        return {"status": "error", "message": str(e)}
    
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True)
def batch_index_documents(self, document_ids: List[int] = None):
    """
    複数文書をバッチでベクトル化
    
    Args:
        document_ids: 文書IDリスト（Noneの場合は全処理済み文書）
    """
    try:
        db = SessionLocal()
        
        # 対象文書の取得
        if document_ids:
            documents = db.query(Document).filter(
                Document.id.in_(document_ids),
                Document.status == "completed"
            ).all()
        else:
            documents = db.query(Document).filter(
                Document.status == "completed"
            ).all()
        
        logger.info(f"Starting batch indexing for {len(documents)} documents")
        
        # 各文書をベクトル化
        results = []
        for document in documents:
            result = index_document_to_vector.delay(document.id)
            results.append({
                "document_id": document.id,
                "task_id": result.id
            })
        
        logger.info(f"Started indexing tasks for {len(results)} documents")
        return {
            "status": "started",
            "total_documents": len(documents),
            "tasks": results
        }
        
    except Exception as e:
        logger.error(f"Error in batch indexing: {e}")
        return {"status": "error", "message": str(e)}
    
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True)
def rebuild_vector_index(self):
    """
    ベクトルインデックスの再構築
    
    全文書のベクトル化を再実行します。
    """
    try:
        db = SessionLocal()
        
        # 全処理済み文書を取得
        documents = db.query(Document).filter(
            Document.status == "completed"
        ).all()
        
        logger.info(f"Starting vector index rebuild for {len(documents)} documents")
        
        # 既存のベクトルインデックスをリセット
        db.query(VectorIndex).update({"is_indexed": False, "error_message": None})
        db.commit()
        
        # バッチ処理でベクトル化
        results = []
        for document in documents:
            result = index_document_to_vector.delay(document.id)
            results.append({
                "document_id": document.id,
                "task_id": result.id
            })
        
        logger.info(f"Started rebuild tasks for {len(results)} documents")
        return {
            "status": "started",
            "total_documents": len(documents),
            "tasks": results
        }
        
    except Exception as e:
        logger.error(f"Error in vector index rebuild: {e}")
        return {"status": "error", "message": str(e)}
    
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True)
def cleanup_vector_index(self):
    """
    ベクトルインデックスのクリーンアップ
    
    削除された文書のベクトルをQdrantから削除します。
    """
    try:
        db = SessionLocal()
        
        # 削除された文書のベクトルインデックスを取得
        deleted_indexes = db.query(VectorIndex).filter(
            VectorIndex.is_indexed == True
        ).join(Document, VectorIndex.document_id == Document.id, isouter=True).filter(
            Document.id.is_(None)
        ).all()
        
        logger.info(f"Found {len(deleted_indexes)} orphaned vector indexes")
        
        # Qdrantから削除
        deleted_count = 0
        for index in deleted_indexes:
            success = vector_store_service.delete_document(index.document_id)
            if success:
                db.delete(index)
                deleted_count += 1
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted_count} orphaned vector indexes")
        return {
            "status": "success",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error in vector index cleanup: {e}")
        return {"status": "error", "message": str(e)}
    
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True)
def sync_new_documents(self):
    """
    新規文書の同期
    
    処理完了した新規文書をベクトル化します。
    """
    try:
        db = SessionLocal()
        
        # ベクトル化されていない処理済み文書を取得
        documents = db.query(Document).filter(
            Document.status == "completed"
        ).outerjoin(VectorIndex, Document.id == VectorIndex.document_id).filter(
            VectorIndex.document_id.is_(None)
        ).all()
        
        logger.info(f"Found {len(documents)} new documents to sync")
        
        if not documents:
            return {"status": "success", "message": "No new documents to sync"}
        
        # 各文書をベクトル化
        results = []
        for document in documents:
            result = index_document_to_vector.delay(document.id)
            results.append({
                "document_id": document.id,
                "task_id": result.id
            })
        
        logger.info(f"Started sync tasks for {len(results)} documents")
        return {
            "status": "started",
            "new_documents": len(documents),
            "tasks": results
        }
        
    except Exception as e:
        logger.error(f"Error in new documents sync: {e}")
        return {"status": "error", "message": str(e)}
    
    finally:
        if 'db' in locals():
            db.close()




