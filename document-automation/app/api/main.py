"""
FastAPI メインアプリケーション
"""
import sys
print("=" * 80, file=sys.stderr)
print("🔥 MAIN.PY IS BEING EXECUTED 🔥", file=sys.stderr)
print("=" * 80, file=sys.stderr)
sys.stderr.flush()

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import upload, documents, export
from app.api.database_routes import router as database_router
from app.models.database import init_db
from config.settings import settings
from config.version import VERSION, get_version_info, get_version_history
import logging
import os
import importlib.util
from pathlib import Path
from typing import Optional, Dict

# ロギング設定（デバッグ用に最大化）
# NAS環境では統合データディレクトリを使用、ローカル環境では./logsを使用
if os.getenv('NAS_MODE') and os.path.exists('/app/logs'):
    log_dir = os.getenv('LOG_DIR', '/app/logs')
else:
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

# 共通認証モジュールのインポート
logger.info("[AUTH] 認証モジュールの読み込みを開始します")
nas_dashboard_path = Path('/nas-project/nas-dashboard')
logger.info(f"[AUTH] nas_dashboard_path: {nas_dashboard_path}")
logger.info(f"[AUTH] nas_dashboard_path.exists(): {nas_dashboard_path.exists()}")
if nas_dashboard_path.exists():
    sys.path.insert(0, str(nas_dashboard_path))
    logger.info(f"[AUTH] sys.pathに追加: {str(nas_dashboard_path)}")
    try:
        # 明示的にパスを指定してインポート
        auth_common_path = nas_dashboard_path / 'utils' / 'auth_common.py'
        logger.info(f"[AUTH] auth_common_path: {auth_common_path}")
        logger.info(f"[AUTH] auth_common_path.exists(): {auth_common_path.exists()}")
        if auth_common_path.exists():
            logger.info(f"[AUTH] 認証モジュールファイルを読み込み中...")
            spec = importlib.util.spec_from_file_location("auth_common", str(auth_common_path))
            if spec is None:
                logger.error(f"[AUTH] specがNoneです")
                AUTH_ENABLED = False
            else:
                auth_common = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(auth_common)
                get_current_user_from_request = auth_common.get_current_user_from_request
                get_dashboard_login_url = auth_common.get_dashboard_login_url
                AUTH_ENABLED = True
                logger.info("[AUTH] 認証モジュールを読み込みました")
        else:
            logger.warning(f"[AUTH] 認証モジュールファイルが見つかりません: {auth_common_path}")
            AUTH_ENABLED = False
    except Exception as e:
        logger.error(f"[AUTH] 認証モジュールをインポートできませんでした（認証機能は無効化されます）: {e}", exc_info=True)
        AUTH_ENABLED = False
else:
    logger.warning(f"[AUTH] 認証モジュールのパスが見つかりません（認証機能は無効化されます）: {nas_dashboard_path}")
    AUTH_ENABLED = False

logger.info(f"[AUTH] AUTH_ENABLED: {AUTH_ENABLED}")

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
        # ログインページにリダイレクト（元のページURLをnextパラメータとして追加）
        # サブフォルダパスを使用して元のパスを構築
        original_path = SUBFOLDER_PATH if SUBFOLDER_PATH else '/'
        
        # 現在のリクエストパスが'/'以外の場合、サブフォルダパスに追加
        current_path = str(request.url.path)
        if current_path and current_path != '/':
            # サブフォルダパスと現在のパスを結合
            original_path = f"{SUBFOLDER_PATH}{current_path}" if SUBFOLDER_PATH else current_path
        elif not SUBFOLDER_PATH:
            # サブフォルダパスがない場合は'/'を使用しない（ダッシュボードにリダイレクト）
            original_path = None
        
        logger.info(f"[AUTH] require_auth: SUBFOLDER_PATH={SUBFOLDER_PATH}, current_path={current_path}, original_path={original_path}")
        
        # ログインURLを取得
        login_url = get_dashboard_login_url(request)
        
        # 元のパスがある場合、nextパラメータとして追加
        if original_path and original_path != '/login' and original_path != '/':
            from urllib.parse import quote
            # nextパラメータが既に含まれていない場合のみ追加
            if 'next=' not in login_url:
                separator = '&' if '?' in login_url else '?'
                encoded_path = quote(original_path, safe='/')
                login_url = f'{login_url}{separator}next={encoded_path}'
                logger.info(f"[AUTH] 元のパスをnextパラメータとして追加: {original_path} -> {encoded_path}")
        
        logger.info(f"[AUTH] require_auth: 認証が必要です: {request.url.path} -> {login_url}")
        raise HTTPException(
            status_code=307,
            detail="認証が必要です",
            headers={"Location": login_url}
        )
    
    logger.info(f"[AUTH] require_auth: 認証成功: {request.url.path}, user={user.get('username') if user else 'None'}")
    return user

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

# サブフォルダ対応（Nginx Proxy Manager経由で /documents でアクセスされる場合）
SUBFOLDER_PATH = os.getenv('SUBFOLDER_PATH', '')
logger.info(f"[INIT] SUBFOLDER_PATH from env: {SUBFOLDER_PATH}")

# FastAPIアプリケーション
# root_pathを設定しない（静的ファイルは/staticにマウント）
# Nginx側で/documents/static/...を/static/...にリライトする
app = FastAPI(
    title="ドキュメント自動処理システム",
    description="PDF・画像からOCR、AI要約、自動分類を行うシステム",
    version=VERSION
    # root_pathは設定しない（静的ファイルのパスに影響するため）
    # 代わりに、Nginx側でリライトを行う
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
static_path = Path("app/static")
logger.info(f"[INIT] Static files path: {static_path}, exists: {static_path.exists()}")
if static_path.exists():
    # root_pathを設定している場合でも、静的ファイルは/staticにマウント
    # Nginx側で/documents/static/...を/static/...にリライトする
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    logger.info(f"[INIT] Static files mounted at /static from {static_path}")
else:
    logger.warning(f"[INIT] Static files directory not found: {static_path}")

templates = Jinja2Templates(directory="app/templates")

# ルーター登録
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(export.router, prefix="/api", tags=["export"])
app.include_router(database_router, prefix="/api", tags=["database"])
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
    logger.info(f"SUBFOLDER_PATH: {SUBFOLDER_PATH}")
    logger.info(f"Static files path: {static_path}")
    logger.info(f"Static files exists: {static_path.exists()}")
    
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
    logger.info(f"[INDEX] SUBFOLDER_PATH: {SUBFOLDER_PATH}")
    
    # 認証チェック（認証が必要な場合はHTMLを返してフロントエンドでリダイレクト）
    # Nginx Proxy Manager経由で307リダイレクトするとクエリパラメータが失われるため、
    # HTMLを返してフロントエンド（JavaScript）でリダイレクトを処理する
    # subfolder_pathが空の場合は/documentsをデフォルト値として使用
    subfolder_path = SUBFOLDER_PATH if SUBFOLDER_PATH else '/documents'
    
    if AUTH_ENABLED:
        user = get_current_user_from_request(request)
        if not user:
            # 認証が必要な場合でも、HTMLを返してフロントエンドでリダイレクトを処理
            # フロントエンドのJavaScriptが即座にAPIリクエストを実行して認証を確認し、
            # 認証エラーが返された場合はログインページにリダイレクトする
            logger.info(f"[INDEX] 認証が必要です: {request.url.path} -> フロントエンドでリダイレクト")
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "title": "ドキュメント自動処理システム",
                    "subfolder_path": subfolder_path,
                }
            )
    
    # 認証済みまたは認証が無効な場合はHTMLを返す
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "ドキュメント自動処理システム",
            "subfolder_path": subfolder_path,
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
async def system_status(request: Request, user: Optional[Dict] = Depends(require_auth)):
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

