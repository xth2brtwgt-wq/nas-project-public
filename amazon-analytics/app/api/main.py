"""Main FastAPI application"""
import os
import sys
import logging
from pathlib import Path
import importlib.util
from typing import Optional, Dict

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import shutil

from config.settings import settings
from config.version import VERSION as __version__, get_version_info
from app.models.database import get_db, init_db
from app.services.data_processor import DataProcessor
from app.services.ai_analyzer import AIAnalyzer
from app.api import routes
from app.api import report_routes
from app.api import database_routes
from app.workers.cleanup_worker import amazon_analytics_cleanup_worker
from app.services.db_size_monitor import amazon_analytics_db_size_monitor

# ロガーの初期化（認証モジュールのインポート前に必要）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 共通認証モジュールのインポート
nas_dashboard_path = Path('/nas-project/nas-dashboard')
if nas_dashboard_path.exists():
    sys.path.insert(0, str(nas_dashboard_path))
    try:
        # 明示的にパスを指定してインポート
        auth_common_path = nas_dashboard_path / 'utils' / 'auth_common.py'
        if auth_common_path.exists():
            spec = importlib.util.spec_from_file_location("auth_common", str(auth_common_path))
            auth_common = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(auth_common)
            get_current_user_from_request = auth_common.get_current_user_from_request
            get_dashboard_login_url = auth_common.get_dashboard_login_url
            AUTH_ENABLED = True
            logger.info("認証モジュールを読み込みました")
        else:
            logger.warning(f"認証モジュールファイルが見つかりません: {auth_common_path}")
            AUTH_ENABLED = False
    except Exception as e:
        logger.warning(f"認証モジュールをインポートできませんでした（認証機能は無効化されます）: {e}")
        AUTH_ENABLED = False
else:
    logger.warning("認証モジュールのパスが見つかりません（認証機能は無効化されます）")
    AUTH_ENABLED = False

# Configure logging
# NAS環境では統合データディレクトリを使用、ローカル環境では./data/logsを使用
if os.getenv('NAS_MODE') and os.path.exists('/app/data'):
    log_dir = os.getenv('LOG_DIR', '/app/data/logs')
else:
    log_dir = os.getenv('LOG_DIR', './data/logs')
os.makedirs(log_dir, exist_ok=True)

# ファイルハンドラーを追加
log_file = os.path.join(log_dir, 'app.log')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# ロガーにファイルハンドラーを追加（既に初期化済みのロガーに追加）
logger.addHandler(file_handler)

# FastAPI用の認証依存性関数
async def require_auth(request: Request) -> Optional[Dict]:
    """認証が必要なエンドポイントの依存性"""
    if not AUTH_ENABLED:
        # 認証が無効な場合はそのまま通す
        return None
    
    # Cookieの確認
    session_id = request.cookies.get('session_id')
    logger.info(f"[AUTH] require_auth: path={request.url.path}, session_id={'存在' if session_id else 'なし'}")
    
    user = get_current_user_from_request(request)
    if not user:
        # ログインページにリダイレクト
        login_url = get_dashboard_login_url(request)
        logger.info(f"[AUTH] require_auth: 認証が必要です: {request.url.path} -> {login_url}")
        raise HTTPException(
            status_code=307,
            detail="認証が必要です",
            headers={"Location": login_url}
        )
    
    logger.info(f"[AUTH] require_auth: 認証成功: {request.url.path}, user={user.get('username') if user else 'None'}")
    return user

# サブフォルダ対応（Nginx Proxy Manager経由で /analytics でアクセスされる場合）
SUBFOLDER_PATH = os.getenv('SUBFOLDER_PATH', '')

# Create FastAPI app
# root_pathを設定しない（静的ファイルは/staticにマウント）
# Nginx側で/analytics/static/...を/static/...にリライトする
app = FastAPI(
    title=settings.APP_NAME,
    version=__version__,
    description="Amazon購入履歴分析システム",
    # root_pathは設定しない（静的ファイルのパスに影響するため）
    # 代わりに、Nginx側でリライトを行う
)

# Mount static files
static_path = settings.BASE_DIR / "app" / "static"
templates_path = settings.BASE_DIR / "app" / "templates"

if static_path.exists():
    # root_pathを設定している場合でも、静的ファイルは/staticにマウント
    # Nginx側で/analytics/static/...を/static/...にリライトする
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    logger.info(f"Static files mounted at /static from {static_path}")
else:
    logger.warning(f"Static files directory not found: {static_path}")

templates = Jinja2Templates(directory=str(templates_path))


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{__version__}")
    logger.info(f"SUBFOLDER_PATH: {SUBFOLDER_PATH}")
    logger.info(f"root_path: {app.root_path if hasattr(app, 'root_path') else 'None'}")
    logger.info(f"Static files path: {static_path}")
    logger.info(f"Static files exists: {static_path.exists()}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Start background workers
    try:
        import asyncio
        asyncio.create_task(amazon_analytics_cleanup_worker.start())
        asyncio.create_task(amazon_analytics_db_size_monitor.start_periodic_check())
        logger.info("Background workers started")
    except Exception as e:
        logger.error(f"Failed to start background workers: {e}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user: Optional[Dict] = Depends(require_auth)):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": settings.APP_NAME,
        "version": __version__,
        "subfolder_path": SUBFOLDER_PATH,
    })


@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint"""
    from fastapi.responses import FileResponse
    favicon_path = settings.BASE_DIR / "app" / "static" / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return JSONResponse({"message": "No favicon"}, status_code=404)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": __version__,
        "app": settings.APP_NAME,
    }


@app.get("/api/version")
async def version_info():
    """Get detailed version information"""
    return get_version_info()


# Include other routes
app.include_router(routes.router, prefix="/api")
app.include_router(report_routes.router, prefix="/api")
app.include_router(database_routes.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

