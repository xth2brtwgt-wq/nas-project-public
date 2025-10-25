"""
データベース接続とセッション管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config.settings import settings
from app.models.document import Base
import logging

logger = logging.getLogger(__name__)

# データベースエンジン
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False
)

# セッションファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """データベースの初期化"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("データベースを初期化しました")
    except Exception as e:
        logger.error(f"データベース初期化エラー: {e}")
        raise


def get_db() -> Session:
    """データベースセッションの取得（FastAPI用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """データベースセッションの取得（一般用）"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

