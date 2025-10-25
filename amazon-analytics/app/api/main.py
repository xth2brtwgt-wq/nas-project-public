"""Main FastAPI application"""
import logging
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
import shutil

from config.settings import settings
from config.version import VERSION as __version__, get_version_info
from app.models.database import get_db, init_db
from app.services.data_processor import DataProcessor
from app.services.ai_analyzer import AIAnalyzer
from app.api import routes
from app.api import report_routes

# Configure logging
import os
log_dir = os.getenv('LOG_DIR', './data/logs')
os.makedirs(log_dir, exist_ok=True)

# ファイルハンドラーを追加
log_file = os.path.join(log_dir, 'app.log')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        file_handler,
        logging.StreamHandler()  # 標準出力も維持
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=__version__,
    description="Amazon購入履歴分析システム",
)

# Mount static files
static_path = settings.BASE_DIR / "app" / "static"
templates_path = settings.BASE_DIR / "app" / "templates"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

templates = Jinja2Templates(directory=str(templates_path))


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{__version__}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": settings.APP_NAME,
        "version": __version__,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

