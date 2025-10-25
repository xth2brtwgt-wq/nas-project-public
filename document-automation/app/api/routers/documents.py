"""
ドキュメント管理用ルーター
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.database import get_db
from app.models.document import Document
from typing import Optional
from datetime import datetime, timezone
from urllib.parse import quote
from pydantic import BaseModel
import logging
import pytz
import os
import zipfile
import io

router = APIRouter()
logger = logging.getLogger(__name__)

# タイムゾーン設定
JST = pytz.timezone('Asia/Tokyo')


# リクエストモデル
class BatchDownloadRequest(BaseModel):
    document_ids: list[int]


def to_jst_string(dt):
    """UTC datetime を JST 文字列に変換"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # タイムゾーン情報がない場合はUTCとして扱う
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(JST).isoformat()


@router.get("/documents")
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    ドキュメント一覧取得
    """
    try:
        query = db.query(Document)
        
        # フィルタ適用
        if status:
            query = query.filter(Document.status == status)
        if category:
            query = query.filter(Document.category == category)
        if search:
            query = query.filter(
                (Document.original_filename.contains(search)) |
                (Document.ocr_text.contains(search)) |
                (Document.summary.contains(search))
            )
        
        # ページング
        total = query.count()
        documents = query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.original_filename,
                    "file_type": doc.file_type,
                    "file_size": doc.file_size,
                    "status": doc.status,
                    "category": doc.category,
                    "summary": doc.summary[:200] if doc.summary else None,
                    "keywords": doc.keywords,
                    "created_at": to_jst_string(doc.created_at),
                    "processed_at": to_jst_string(doc.processed_at)
                }
                for doc in documents
            ]
        }
        
    except Exception as e:
        logger.error(f"ドキュメント一覧取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}")
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    ドキュメント詳細取得
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="ドキュメントが見つかりません")
        
        return {
            "id": document.id,
            "filename": document.original_filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "mime_type": document.mime_type,
            "status": document.status,
            "ocr_text": document.ocr_text,
            "ocr_confidence": document.ocr_confidence,
            "ocr_engine": document.ocr_engine,
            "summary": document.summary,
            "category": document.category,
            "keywords": document.keywords,
            "extracted_metadata": document.extracted_metadata,
            "processing_time": document.processing_time,
            "error_message": document.error_message,
            "notion_page_id": document.notion_page_id,
            "google_drive_file_id": document.google_drive_file_id,
            "created_at": to_jst_string(document.created_at),
            "processed_at": to_jst_string(document.processed_at),
            "is_exported": document.is_exported,
            "is_archived": document.is_archived
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ドキュメント詳細取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    元ファイルのダウンロード
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="ドキュメントが見つかりません")
        
        # ファイルの存在確認
        if not os.path.exists(document.file_path):
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")
        
        # RFC 5987形式でファイル名をエンコード
        encoded_filename = quote(document.original_filename)
        
        logger.info(f"ファイルダウンロード: ID {document_id}, ファイル名 {document.original_filename}")
        
        return FileResponse(
            path=document.file_path,
            filename=document.original_filename,
            media_type=document.mime_type or 'application/octet-stream',
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ファイルダウンロードエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/batch/download")
async def batch_download_documents(
    request: BatchDownloadRequest,
    db: Session = Depends(get_db)
):
    """
    複数の元ファイルをZIPでダウンロード
    """
    try:
        documents = db.query(Document).filter(Document.id.in_(request.document_ids)).all()
        if not documents:
            raise HTTPException(status_code=404, detail="ドキュメントが見つかりません")
        
        # ZIPファイルをメモリ上に作成
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for doc in documents:
                # ファイルの存在確認
                if not os.path.exists(doc.file_path):
                    logger.warning(f"ファイルが見つかりません: {doc.file_path}")
                    continue
                
                # 元ファイルをZIPに追加
                # 同名ファイルの衝突を避けるため、IDをプレフィックスとして追加
                safe_filename = f"{doc.id}_{doc.original_filename}"
                zip_file.write(doc.file_path, safe_filename)
        
        # ZIPファイルの内容を取得
        zip_buffer.seek(0)
        zip_content = zip_buffer.getvalue()
        
        logger.info(f"元ファイル一括ダウンロード成功: {len(documents)}件")
        
        # ZIPファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"original_files_{timestamp}.zip"
        encoded_filename = quote(zip_filename)
        
        return Response(
            content=zip_content,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"元ファイル一括ダウンロードエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    ドキュメント削除
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="ドキュメントが見つかりません")
        
        # ファイル削除
        import os
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # データベースから削除
        db.delete(document)
        db.commit()
        
        logger.info(f"ドキュメント削除: ID {document_id}")
        
        return {"status": "success", "message": "ドキュメントを削除しました"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ドキュメント削除エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def list_categories(db: Session = Depends(get_db)):
    """
    カテゴリ一覧取得
    """
    try:
        categories = db.query(Document.category).distinct().filter(
            Document.category.isnot(None)
        ).all()
        
        return {
            "categories": [cat[0] for cat in categories if cat[0]]
        }
        
    except Exception as e:
        logger.error(f"カテゴリ一覧取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """
    統計情報取得
    """
    try:
        total_documents = db.query(Document).count()
        pending_documents = db.query(Document).filter(Document.status == "pending").count()
        processing_documents = db.query(Document).filter(Document.status == "processing").count()
        completed_documents = db.query(Document).filter(Document.status == "completed").count()
        failed_documents = db.query(Document).filter(Document.status == "failed").count()
        
        # カテゴリ別集計
        categories = db.query(
            Document.category,
            func.count(Document.id)
        ).filter(
            Document.category.isnot(None)
        ).group_by(Document.category).all()
        
        return {
            "total_documents": total_documents,
            "status": {
                "pending": pending_documents,
                "processing": processing_documents,
                "completed": completed_documents,
                "failed": failed_documents
            },
            "categories": {cat: count for cat, count in categories if cat}
        }
        
    except Exception as e:
        logger.error(f"統計情報取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

