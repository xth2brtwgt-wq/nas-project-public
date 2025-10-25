"""
エクスポート用ルーター
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.document import Document, ExportHistory
from app.services.export_service import export_to_markdown, export_summary
from config.settings import settings
from pydantic import BaseModel
import logging
import os
import zipfile
import io
from datetime import datetime
from urllib.parse import quote

router = APIRouter()
logger = logging.getLogger(__name__)


# リクエストモデル
class BatchExportRequest(BaseModel):
    document_ids: list[int]


class SummaryRequest(BaseModel):
    document_ids: list[int]
    title: str = "複数文書まとめ"


@router.get("/export/{document_id}/markdown")
async def export_document_markdown(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    個別ドキュメントをマークダウンでエクスポート
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="ドキュメントが見つかりません")
        
        # マークダウン生成
        markdown_content = export_to_markdown(document)
        
        # ファイル保存
        filename = f"{document.id}_{document.original_filename.rsplit('.', 1)[0]}.md"
        file_path = os.path.join(settings.export_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        # エクスポート履歴記録
        export_history = ExportHistory(
            export_type="markdown",
            document_ids=[document_id],
            file_path=file_path,
            file_size=len(markdown_content.encode("utf-8")),
            title=document.original_filename
        )
        db.add(export_history)
        
        # ドキュメントの is_exported フラグ更新
        document.is_exported = True
        db.commit()
        
        logger.info(f"マークダウンエクスポート成功: {filename}")
        
        # RFC 5987形式でファイル名をエンコード
        encoded_filename = quote(filename)
        
        return Response(
            content=markdown_content.encode("utf-8"),
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"マークダウンエクスポートエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/batch/markdown")
async def export_batch_markdown(
    request: BatchExportRequest,
    db: Session = Depends(get_db)
):
    """
    複数ドキュメントをマークダウンで一括エクスポート
    """
    try:
        documents = db.query(Document).filter(Document.id.in_(request.document_ids)).all()
        if not documents:
            raise HTTPException(status_code=404, detail="ドキュメントが見つかりません")
        
        title = "複数文書エクスポート"
        
        # 複数ドキュメントをマークダウンに結合
        markdown_parts = [f"# {title}\n\n", f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"]
        markdown_parts.append(f"文書数: {len(documents)}\n\n")
        markdown_parts.append("---\n\n")
        
        for i, doc in enumerate(documents, 1):
            markdown_parts.append(f"## {i}. {doc.original_filename}\n\n")
            markdown_parts.append(export_to_markdown(doc))
            markdown_parts.append("\n\n---\n\n")
        
        markdown_content = "".join(markdown_parts)
        
        # ファイル保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_export_{timestamp}.md"
        file_path = os.path.join(settings.export_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        # エクスポート履歴記録
        export_history = ExportHistory(
            export_type="markdown",
            document_ids=request.document_ids,
            file_path=file_path,
            file_size=len(markdown_content.encode("utf-8")),
            title=title
        )
        db.add(export_history)
        db.commit()
        
        logger.info(f"一括マークダウンエクスポート成功: {len(documents)}件")
        
        # RFC 5987形式でファイル名をエンコード
        encoded_filename = quote(filename)
        
        return Response(
            content=markdown_content.encode("utf-8"),
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"一括マークダウンエクスポートエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/batch/markdown-zip")
async def export_batch_markdown_zip(
    request: BatchExportRequest,
    db: Session = Depends(get_db)
):
    """
    複数ドキュメントを個別マークダウンファイルとしてZIPで一括エクスポート
    """
    try:
        documents = db.query(Document).filter(Document.id.in_(request.document_ids)).all()
        if not documents:
            raise HTTPException(status_code=404, detail="ドキュメントが見つかりません")
        
        # ZIPファイルをメモリ上に作成
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for doc in documents:
                # 各ドキュメントのマークダウンを生成
                markdown_content = export_to_markdown(doc)
                
                # ファイル名を生成（拡張子を除去してから.mdを追加）
                base_filename = doc.original_filename.rsplit('.', 1)[0]
                filename = f"{doc.id}_{base_filename}.md"
                
                # ZIPに追加
                zip_file.writestr(filename, markdown_content.encode('utf-8'))
        
        # ZIPファイルの内容を取得
        zip_buffer.seek(0)
        zip_content = zip_buffer.getvalue()
        
        # エクスポート履歴記録
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_history = ExportHistory(
            export_type="markdown_zip",
            document_ids=request.document_ids,
            file_path=f"/tmp/batch_markdown_{timestamp}.zip",
            file_size=len(zip_content),
            title=f"個別マークダウンエクスポート_{len(documents)}件"
        )
        db.add(export_history)
        db.commit()
        
        logger.info(f"個別マークダウンZIPエクスポート成功: {len(documents)}件")
        
        # ZIPファイル名を生成
        zip_filename = f"markdown_export_{timestamp}.zip"
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
        logger.error(f"個別マークダウンZIPエクスポートエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/summary")
async def export_combined_summary(
    request: SummaryRequest,
    db: Session = Depends(get_db)
):
    """
    複数ドキュメントの情報をまとめて要約
    """
    try:
        documents = db.query(Document).filter(Document.id.in_(request.document_ids)).all()
        if not documents:
            raise HTTPException(status_code=404, detail="ドキュメントが見つかりません")
        
        # 統合要約生成
        summary_content = await export_summary(documents, request.title)
        
        # ファイル保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{timestamp}.md"
        file_path = os.path.join(settings.export_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(summary_content)
        
        # エクスポート履歴記録
        export_history = ExportHistory(
            export_type="summary",
            document_ids=request.document_ids,
            file_path=file_path,
            file_size=len(summary_content.encode("utf-8")),
            title=request.title,
            description="複数文書の統合要約"
        )
        db.add(export_history)
        db.commit()
        
        logger.info(f"統合要約エクスポート成功: {len(documents)}件")
        
        return {
            "status": "success",
            "message": "統合要約を生成しました",
            "filename": filename,
            "file_path": file_path,
            "document_count": len(documents),
            "summary": summary_content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"統合要約エクスポートエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/history")
async def list_export_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    エクスポート履歴一覧
    """
    try:
        total = db.query(ExportHistory).count()
        history = db.query(ExportHistory).order_by(
            ExportHistory.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "history": [
                {
                    "id": h.id,
                    "export_type": h.export_type,
                    "title": h.title,
                    "document_count": len(h.document_ids),
                    "file_size": h.file_size,
                    "created_at": h.created_at.isoformat() if h.created_at else None
                }
                for h in history
            ]
        }
        
    except Exception as e:
        logger.error(f"エクスポート履歴取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

