"""
ファイルアップロード用ルーター
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.document import Document
from app.workers.tasks import process_document_task
from config.settings import settings, get_allowed_extensions
import os
import uuid
import magic
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


def validate_file(file: UploadFile) -> tuple[bool, str]:
    """ファイルのバリデーション"""
    # ファイル名チェック
    if not file.filename:
        return False, "ファイル名が不正です"
    
    # 拡張子チェック
    ext = file.filename.split(".")[-1].lower()
    if ext not in get_allowed_extensions():
        return False, f"許可されていないファイル形式です: {ext}"
    
    # ファイルサイズは後でチェック
    return True, "OK"


async def save_uploaded_file(file: UploadFile) -> tuple[str, int]:
    """アップロードファイルを保存"""
    # ユニークなファイル名生成
    file_id = str(uuid.uuid4())
    ext = file.filename.split(".")[-1].lower()
    new_filename = f"{file_id}.{ext}"
    file_path = os.path.join(settings.upload_dir, new_filename)
    
    # ファイル保存
    total_size = 0
    with open(file_path, "wb") as f:
        while chunk := await file.read(8192):
            total_size += len(chunk)
            if total_size > settings.max_file_size:
                os.remove(file_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"ファイルサイズが上限を超えています: {settings.max_file_size / 1024 / 1024}MB"
                )
            f.write(chunk)
    
    return file_path, total_size


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    ファイルアップロード
    """
    try:
        # バリデーション
        is_valid, message = validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        # ファイル保存
        file_path, file_size = await save_uploaded_file(file)
        
        # MIMEタイプ取得
        mime_type = magic.from_file(file_path, mime=True)
        
        # データベースに記録
        document = Document(
            filename=os.path.basename(file_path),
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file.filename.split(".")[-1].lower(),
            mime_type=mime_type,
            status="pending"
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # 非同期処理タスクをキューに登録
        process_document_task.delay(document.id)
        
        logger.info(f"ファイルアップロード成功: {file.filename} (ID: {document.id})")
        
        return {
            "status": "success",
            "message": "ファイルをアップロードしました",
            "document_id": document.id,
            "filename": file.filename,
            "file_size": file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"アップロードエラー: {e}")
        raise HTTPException(status_code=500, detail=f"アップロードに失敗しました: {str(e)}")


@router.post("/upload/batch")
async def upload_batch_files(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    複数ファイルの一括アップロード
    """
    results = []
    errors = []
    
    for file in files:
        try:
            # バリデーション
            is_valid, message = validate_file(file)
            if not is_valid:
                errors.append({"filename": file.filename, "error": message})
                continue
            
            # ファイル保存
            file_path, file_size = await save_uploaded_file(file)
            
            # MIMEタイプ取得
            mime_type = magic.from_file(file_path, mime=True)
            
            # データベースに記録
            document = Document(
                filename=os.path.basename(file_path),
                original_filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file.filename.split(".")[-1].lower(),
                mime_type=mime_type,
                status="pending"
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            
            # 非同期処理タスクをキューに登録
            process_document_task.delay(document.id)
            
            results.append({
                "document_id": document.id,
                "filename": file.filename,
                "status": "success"
            })
            
        except Exception as e:
            errors.append({"filename": file.filename, "error": str(e)})
    
    return {
        "status": "completed",
        "total": len(files),
        "success": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }

