"""
アプリケーション設定
"""
from pydantic_settings import BaseSettings
from typing import Literal
import os


class Settings(BaseSettings):
    """環境変数からの設定読み込み"""
    
    # データベース
    database_url: str = "postgresql://docuser:docpass@db:5432/document_automation"
    redis_url: str = "redis://redis:6379/0"
    
    # Google Cloud
    google_cloud_project_id: str = ""
    google_application_credentials: str = "/app/config/google-credentials.json"
    gemini_api_key: str = ""
    
    # 処理モード
    processing_mode: Literal["hybrid", "cloud", "local"] = "hybrid"
    cost_mode: Literal["save", "balanced", "performance"] = "balanced"
    
    # OCR設定
    ocr_engine: Literal["cloud", "local"] = "cloud"
    ocr_language: str = "jpn,eng"  # Tesseractの言語コード
    
    # AI設定
    ai_provider: Literal["gemini", "openai", "claude", "local"] = "gemini"
    gemini_model: str = "gemini-2.5-flash"
    openai_api_key: str = ""
    
    # RAG設定
    qdrant_url: str = "http://qdrant:6333"
    embedding_model: Literal["openai", "local"] = "local"
    embedding_dimension: int = 384  # sentence-transformers/all-MiniLM-L6-v2
    vector_collection_name: str = "documents"
    similarity_threshold: float = 0.7
    max_search_results: int = 10
    
    # Notion (Phase 2)
    notion_api_key: str = ""
    notion_database_id: str = ""
    
    # Google Drive (Phase 2)
    google_drive_folder_id: str = ""
    
    # ファイル設定
    upload_dir: str = "/app/uploads"
    processed_dir: str = "/app/processed"
    export_dir: str = "/app/exports"
    cache_dir: str = "/app/cache"
    max_file_size: int = 52428800  # 50MB
    max_concurrent_tasks: int = 5
    allowed_extensions: str = "pdf,jpg,jpeg,png"
    
    # ログ設定
    log_level: str = "INFO"
    log_file: str = "/app/logs/app.log"
    
    # セキュリティ
    secret_key: str = "change-this-in-production"
    api_key: str = ""
    
    # タイムゾーン
    tz: str = "Asia/Tokyo"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# シングルトンインスタンス
settings = Settings()


def get_allowed_extensions():
    """許可された拡張子のリストを取得"""
    return [ext.strip() for ext in settings.allowed_extensions.split(",")]


def is_cloud_mode():
    """クラウド処理モードかチェック"""
    return settings.processing_mode in ["cloud", "hybrid"]


def is_cost_saving_mode():
    """コスト節約モードかチェック"""
    return settings.cost_mode == "save"

