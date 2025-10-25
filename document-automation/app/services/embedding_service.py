"""
Embedding生成サービス
"""
import logging
from typing import List, Optional
import openai
from sentence_transformers import SentenceTransformer
from config.settings import settings
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding生成サービス"""
    
    def __init__(self):
        self.openai_client = None
        self.local_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """モデルの初期化"""
        try:
            # OpenAI API設定
            if settings.openai_api_key:
                openai.api_key = settings.openai_api_key
                self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI Embedding model initialized")
            
            # ローカルモデルの初期化（フォールバック用）
            self.local_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            logger.info("Local embedding model initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding models: {e}")
            raise
    
    def generate_embeddings(
        self, 
        texts: List[str], 
        use_openai: bool = True
    ) -> List[List[float]]:
        """
        テキストのEmbeddingを生成
        
        Args:
            texts: テキストリスト
            use_openai: OpenAI使用フラグ
            
        Returns:
            Embeddingベクトルのリスト
        """
        try:
            if use_openai and self.openai_client:
                return self._generate_openai_embeddings(texts)
            else:
                return self._generate_local_embeddings(texts)
                
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            # フォールバック: ローカルモデルを使用
            if use_openai:
                logger.warning("Falling back to local model")
                return self._generate_local_embeddings(texts)
            else:
                raise
    
    def _generate_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """OpenAI Embedding生成"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {e}")
            raise
    
    def _generate_local_embeddings(self, texts: List[str]) -> List[List[float]]:
        """ローカルモデルでのEmbedding生成"""
        try:
            embeddings = self.local_model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Local embedding generation failed: {e}")
            raise
    
    def generate_single_embedding(self, text: str, use_openai: bool = True) -> List[float]:
        """単一テキストのEmbedding生成"""
        return self.generate_embeddings([text], use_openai)[0]
    
    def get_embedding_dimension(self, use_openai: bool = True) -> int:
        """Embeddingの次元数を取得"""
        if use_openai and self.openai_client:
            return 1536  # text-embedding-3-smallの次元数
        else:
            return 384  # all-MiniLM-L6-v2の次元数


# シングルトンインスタンス
embedding_service = EmbeddingService()




