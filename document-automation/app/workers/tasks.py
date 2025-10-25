"""
非同期処理タスク
"""
from app.workers.celery_app import celery_app
from app.models.database import get_db_session
from app.models.document import Document, ProcessingLog
from app.services.ocr_service import OCRService
from app.services.ai_service import AIService
from datetime import datetime
import logging
import time

# RAGタスクをインポート
from app.workers.rag_tasks import index_document_to_vector, rebuild_vector_index

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.tasks.process_document_task")
def process_document_task(document_id: int):
    """
    ドキュメント処理タスク
    """
    logger.info(f"ドキュメント処理開始: ID {document_id}")
    start_time = time.time()
    
    try:
        with get_db_session() as db:
            # ドキュメント取得
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.error(f"ドキュメントが見つかりません: ID {document_id}")
                return
            
            # ステータス更新: processing
            document.status = "processing"
            db.commit()
            
            # ログ記録
            log_processing(db, document_id, "INFO", "processing_started", "処理を開始しました")
            
            try:
                # 1. OCR処理
                logger.info(f"OCR処理開始: {document.original_filename}")
                log_processing(db, document_id, "INFO", "ocr_started", "OCR処理を開始")
                
                ocr_service = OCRService()
                ocr_result = ocr_service.__class__().process_document(document.file_path)
                # 同期的に実行（awaitを使わない）
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                ocr_result = loop.run_until_complete(ocr_service.process_document(document.file_path))
                loop.close()
                
                document.ocr_text = ocr_result["text"]
                document.ocr_confidence = ocr_result["confidence"]
                document.ocr_engine = ocr_result["engine"]
                db.commit()
                
                log_processing(db, document_id, "INFO", "ocr_completed", 
                             f"OCR完了: {len(ocr_result['text'])}文字, 信頼度{ocr_result['confidence']:.2f}")
                
                # 2. AI要約・分類
                logger.info(f"AI分析開始: {document.original_filename}")
                log_processing(db, document_id, "INFO", "ai_started", "AI分析を開始")
                
                ai_service = AIService()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                ai_result = loop.run_until_complete(
                    ai_service.analyze_document(document.ocr_text, document.original_filename)
                )
                loop.close()
                
                document.summary = ai_result["summary"]
                document.category = ai_result["category"]
                document.keywords = ai_result["keywords"]
                document.extracted_metadata = ai_result["metadata"]
                db.commit()
                
                log_processing(db, document_id, "INFO", "ai_completed", 
                             f"AI分析完了: カテゴリ={ai_result['category']}")
                
                # 3. 処理完了
                processing_time = time.time() - start_time
                document.status = "completed"
                document.processing_time = processing_time
                document.processed_at = datetime.utcnow()
                db.commit()
                
                log_processing(db, document_id, "INFO", "processing_completed", 
                             f"処理完了: {processing_time:.2f}秒")
                
                logger.info(f"ドキュメント処理完了: ID {document_id} ({processing_time:.2f}秒)")
                
                return {
                    "status": "success",
                    "document_id": document_id,
                    "processing_time": processing_time
                }
                
            except Exception as e:
                # エラーハンドリング
                logger.error(f"ドキュメント処理エラー: {e}")
                
                document.status = "failed"
                document.error_message = str(e)
                document.processing_time = time.time() - start_time
                db.commit()
                
                log_processing(db, document_id, "ERROR", "processing_failed", str(e))
                
                raise
                
    except Exception as e:
        logger.error(f"タスク実行エラー: {e}")
        raise


def log_processing(db, document_id: int, level: str, step: str, message: str, details: dict = None):
    """処理ログを記録"""
    try:
        log = ProcessingLog(
            document_id=document_id,
            level=level,
            step=step,
            message=message,
            details=details or {}
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"ログ記録エラー: {e}")


@celery_app.task(name="app.workers.tasks.batch_process_task")
def batch_process_task(document_ids: list[int]):
    """
    バッチ処理タスク
    """
    logger.info(f"バッチ処理開始: {len(document_ids)}件")
    
    results = []
    for document_id in document_ids:
        try:
            result = process_document_task(document_id)
            results.append(result)
        except Exception as e:
            logger.error(f"バッチ処理エラー (ID {document_id}): {e}")
            results.append({
                "status": "error",
                "document_id": document_id,
                "error": str(e)
            })
    
    logger.info(f"バッチ処理完了: {len(results)}件")
    return results


@celery_app.task(name="app.workers.tasks.cleanup_old_files_task")
def cleanup_old_files_task():
    """
    古いファイルのクリーンアップタスク（定期実行用）
    """
    logger.info("古いファイルのクリーンアップ開始")
    
    try:
        from datetime import timedelta
        import os
        
        with get_db_session() as db:
            # 30日以上前のアーカイブ済みドキュメント
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            old_documents = db.query(Document).filter(
                Document.is_archived == True,
                Document.created_at < cutoff_date
            ).all()
            
            deleted_count = 0
            for doc in old_documents:
                try:
                    # ファイル削除
                    if os.path.exists(doc.file_path):
                        os.remove(doc.file_path)
                    
                    # DB削除
                    db.delete(doc)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"ファイル削除エラー (ID {doc.id}): {e}")
            
            db.commit()
            
            logger.info(f"クリーンアップ完了: {deleted_count}件削除")
            return {"deleted_count": deleted_count}
            
    except Exception as e:
        logger.error(f"クリーンアップエラー: {e}")
        raise

