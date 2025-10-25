"""
FastAPI メインアプリケーション
"""
import sys
print("=" * 80, file=sys.stderr)
print("🔥 MAIN.PY IS BEING EXECUTED 🔥", file=sys.stderr)
print("=" * 80, file=sys.stderr)
sys.stderr.flush()

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import upload, documents, export
from app.models.database import init_db
from config.settings import settings
from config.version import VERSION, get_version_info, get_version_history
import logging
import os

# ロギング設定（デバッグ用に最大化）
log_dir = os.getenv('LOG_DIR', './logs')
os.makedirs(log_dir, exist_ok=True)

# ファイルハンドラーを追加
log_file = os.path.join(log_dir, 'app.log')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        file_handler,
        logging.StreamHandler()  # 標準出力も維持
    ]
)
logger = logging.getLogger(__name__)

# RAGルーターのインポート（詳細エラーハンドリング付き）
logger.info("=== RAGルーター登録開始 ===")
try:
    logger.info("RAGルーターのインポート開始...")
    from app.api.routers import rag
    RAG_AVAILABLE = True
    logger.info("✅ RAGルーターのインポート成功")
except Exception as e:
    logger.error(f"❌ RAGルーターのインポート失敗: {str(e)}")
    logger.error(f"エラータイプ: {type(e).__name__}")
    import traceback
    logger.error(f"トレースバック:\n{traceback.format_exc()}")
    RAG_AVAILABLE = False
    rag = None

# FastAPIアプリケーション
app = FastAPI(
    title="ドキュメント自動処理システム",
    description="PDF・画像からOCR、AI要約、自動分類を行うシステム",
    version=VERSION
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイルとテンプレート
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ルーター登録
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(export.router, prefix="/api", tags=["export"])
# RAGルーターの登録（暫定対処）
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"

if RAG_ENABLED:
    try:
        logger.info("=== RAG機能: 有効化試行 ===")
        if RAG_AVAILABLE and rag:
            logger.info("RAGルーターの登録開始...")
            app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
            logger.info("✅ RAGルーターの登録成功")
        else:
            logger.warning("RAGルーターが利用不可、フォールバック実行...")
            # フォールバック: 手動でRAGルーターを登録
            from app.api.routers import rag as rag_fallback
            app.include_router(rag_fallback.router, prefix="/api", tags=["rag"])
            logger.info("✅ RAGルーターのフォールバック登録成功")
            
        # 登録確認
        rag_routes = [route for route in app.routes if hasattr(route, 'path') and '/rag' in route.path]
        logger.info(f"📊 RAGルート登録数: {len(rag_routes)}")
        for route in rag_routes:
            logger.info(f"  - {route.methods} {route.path}")
        
    except Exception as e:
        logger.error(f"❌ RAGルーターの登録失敗: {str(e)}")
        logger.error(f"エラータイプ: {type(e).__name__}")
        import traceback
        logger.error(f"トレースバック:\n{traceback.format_exc()}")
        logger.warning("⚠️ RAG機能: 無効化 (エラーのため)")
else:
    logger.info("ℹ️ RAG機能: 環境変数により無効化")


@app.on_event("startup")
async def startup_event():
    """起動時の処理"""
    logger.info("アプリケーションを起動中...")
    
    # ディレクトリ作成
    for directory in [settings.upload_dir, settings.processed_dir, 
                     settings.export_dir, settings.cache_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # データベース初期化
    try:
        init_db()
        logger.info("データベース接続成功")
    except Exception as e:
        logger.error(f"データベース接続エラー: {e}")
    
    # RAGルーターの遅延登録
    try:
        logger.info("=== RAGルーターの遅延登録開始 ===")
        from app.api.routers import rag
        app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
        logger.info("✅ RAGルーターの遅延登録成功")
        
        # 登録確認
        rag_routes = [route for route in app.routes if hasattr(route, 'path') and '/api/rag' in route.path]
        logger.info(f"📊 遅延登録後のRAGルート数: {len(rag_routes)}")
        for route in rag_routes:
            logger.info(f"  - {route.methods} {route.path}")
            
    except Exception as e:
        logger.error(f"❌ RAGルーターの遅延登録失敗: {str(e)}")
        import traceback
        logger.error(f"トレースバック:\n{traceback.format_exc()}")
    
    logger.info("アプリケーション起動完了")


@app.on_event("shutdown")
async def shutdown_event():
    """終了時の処理"""
    logger.info("アプリケーションを終了中...")


@app.get("/")
async def index(request: Request):
    """トップページ"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "ドキュメント自動処理システム"
        }
    )


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "version": VERSION,
        "mode": settings.processing_mode,
        "ocr_engine": settings.ocr_engine,
        "ai_provider": settings.ai_provider
    }


@app.get("/status")
async def system_status():
    """システム状態"""
    version_info = get_version_info()
    return {
        "version": version_info["version"],
        "version_name": version_info["version_name"],
        "release_date": version_info["release_date"],
        "processing_mode": settings.processing_mode,
        "cost_mode": settings.cost_mode,
        "ocr_engine": settings.ocr_engine,
        "ai_provider": settings.ai_provider,
        "max_concurrent_tasks": settings.max_concurrent_tasks,
        "allowed_extensions": settings.allowed_extensions.split(",")
    }


@app.get("/version")
async def version_info():
    """バージョン情報"""
    return get_version_info()


@app.get("/version/history")
async def version_history():
    """バージョン履歴"""
    return get_version_history()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

