"""
データベースモデル定義
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Document(Base):
    """ドキュメントのメタデータ"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ファイル情報
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    mime_type = Column(String(100))
    
    # 処理状態
    status = Column(String(50), default="pending", index=True)
    # pending, processing, completed, failed
    
    # OCR結果
    ocr_text = Column(Text)
    ocr_confidence = Column(Float)
    ocr_engine = Column(String(50))  # cloud, local
    
    # AI要約・分類
    summary = Column(Text)
    category = Column(String(100), index=True)
    keywords = Column(JSON)  # ["keyword1", "keyword2", ...]
    
    # メタデータ抽出
    extracted_metadata = Column(JSON)
    # {
    #   "title": "文書タイトル",
    #   "date": "2025-10-18",
    #   "author": "作成者",
    #   "amount": 10000,
    #   ...
    # }
    
    # 処理情報
    processing_time = Column(Float)  # 秒
    error_message = Column(Text)
    
    # 外部連携
    notion_page_id = Column(String(255))
    google_drive_file_id = Column(String(255))
    
    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # フラグ
    is_exported = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"


class ProcessingLog(Base):
    """処理ログ"""
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True)
    
    # ログ情報
    level = Column(String(20))  # INFO, WARNING, ERROR
    message = Column(Text)
    step = Column(String(100))  # upload, ocr, ai_summary, export
    
    # 詳細
    details = Column(JSON)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<ProcessingLog(id={self.id}, document_id={self.document_id}, level={self.level})>"


class ExportHistory(Base):
    """エクスポート履歴"""
    __tablename__ = "export_history"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # エクスポート情報
    export_type = Column(String(50))  # markdown, pdf, summary
    document_ids = Column(JSON)  # [1, 2, 3, ...]
    file_path = Column(String(512))
    file_size = Column(Integer)
    
    # メタデータ
    title = Column(String(255))
    description = Column(Text)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<ExportHistory(id={self.id}, export_type={self.export_type})>"


class RAGQuery(Base):
    """RAGクエリ履歴"""
    __tablename__ = "rag_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # クエリ情報
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50), default="question")  # question, search, similar
    
    # フィルタ条件
    filters = Column(JSON)  # 適用されたフィルタ条件
    
    # 結果情報
    answer = Column(Text)
    sources_count = Column(Integer, default=0)
    similarity_threshold = Column(Float, default=0.7)
    
    # 処理情報
    processing_time = Column(Float)  # 秒
    error_message = Column(Text)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<RAGQuery(id={self.id}, query_text={self.query_text[:50]}...)>"


class RAGSource(Base):
    """RAG検索結果のソース"""
    __tablename__ = "rag_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, index=True)
    document_id = Column(Integer, index=True)
    
    # 検索結果情報
    similarity_score = Column(Float)
    rank = Column(Integer)  # 検索結果内での順位
    
    # 文書情報（スナップショット）
    filename = Column(String(255))
    category = Column(String(100))
    text_preview = Column(Text)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<RAGSource(id={self.id}, query_id={self.query_id}, document_id={self.document_id})>"


class VectorIndex(Base):
    """ベクトルインデックス管理"""
    __tablename__ = "vector_index"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, unique=True, index=True)
    
    # インデックス情報
    vector_id = Column(String(255), unique=True)  # Qdrant内のID
    embedding_model = Column(String(100))  # 使用したEmbeddingモデル
    embedding_dimension = Column(Integer)
    
    # 処理情報
    is_indexed = Column(Boolean, default=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<VectorIndex(id={self.id}, document_id={self.document_id}, is_indexed={self.is_indexed})>"

