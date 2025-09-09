import os
from pathlib import Path
from typing import List, Tuple, Optional
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

from config.settings import settings
from src.utils.logger import setup_logger
from src.utils.exceptions import VectorStoreException, DocumentLoadException

logger = setup_logger(__name__)

class VectorService:
    """向量檢索服務"""
    
    def __init__(self):
        self.embedding_model = None
        self.vector_store = None
        self._initialize()
    
    def _initialize(self) -> None:
        """初始化服務"""
        try:
            # 設置環境變數（避免 TensorFlow 警告）
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            
            # 初始化 embedding 模型
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL
            )
            
            # 嘗試載入現有向量資料庫，否則重新建立
            if self._load_existing_vector_store():
                logger.info("✅ 成功載入現有向量資料庫")
            else:
                logger.info("🔄 建立新的向量資料庫...")
                self._build_vector_store()
                
        except Exception as e:
            logger.error(f"❌ 向量服務初始化失敗: {e}")
            raise VectorStoreException(f"Failed to initialize vector service: {e}")
    
    def _load_existing_vector_store(self) -> bool:
        """嘗試載入現有的向量資料庫"""
        try:
            vector_store_path = Path(settings.VECTOR_STORE_PATH)
            if vector_store_path.exists():
                self.vector_store = FAISS.load_local(
                    str(vector_store_path), 
                    self.embedding_model,
                    allow_dangerous_deserialization=True
                )
                return True
        except Exception as e:
            logger.warning(f"⚠️ 載入現有向量資料庫失敗: {e}")
        return False
    
    def _build_vector_store(self) -> None:
        """建立新的向量資料庫"""
        try:
            # 載入 PDF 文檔
            docs = self._load_pdf_documents()
            
            # 建立向量資料庫
            self.vector_store = FAISS.from_documents(docs, self.embedding_model)
            
            # 保存向量資料庫
            self._save_vector_store()
            
            logger.info(f"✅ 成功建立向量資料庫，共 {len(docs)} 個文檔")
            
        except Exception as e:
            logger.error(f"❌ 建立向量資料庫失敗: {e}")
            raise VectorStoreException(f"Failed to build vector store: {e}")
    
    def _load_pdf_documents(self) -> List[Document]:
        """載入並處理 PDF 文檔"""
        try:
            if not Path(settings.PDF_PATH).exists():
                raise DocumentLoadException(f"PDF 文件不存在: {settings.PDF_PATH}")
            
            loader = PyPDFLoader(settings.PDF_PATH)
            pdf_docs = loader.load()
            
            docs = []
            for i, doc in enumerate(pdf_docs):
                content = doc.page_content.strip()
                if content:
                    docs.append(Document(
                        page_content=content, 
                        metadata={"source": f"{settings.PDF_PATH}#page_{i+1}"}
                    ))
            
            if not docs:
                raise DocumentLoadException("PDF 文件中沒有有效內容")
                
            return docs
            
        except Exception as e:
            logger.error(f"❌ PDF 文檔載入失敗: {e}")
            raise DocumentLoadException(f"Failed to load PDF documents: {e}")
    
    def _save_vector_store(self) -> None:
        """保存向量資料庫到本地"""
        try:
            vector_store_path = Path(settings.VECTOR_STORE_PATH)
            vector_store_path.parent.mkdir(parents=True, exist_ok=True)
            self.vector_store.save_local(str(vector_store_path))
            logger.info(f"💾 向量資料庫已保存至: {vector_store_path}")
        except Exception as e:
            logger.warning(f"⚠️ 保存向量資料庫失敗: {e}")
    
    def similarity_search_with_score(self, query: str, k: int = None) -> List[Tuple[Document, float]]:
        """執行相似度搜尋"""
        if not self.vector_store:
            raise VectorStoreException("向量資料庫未初始化")
        
        k = k or settings.RETRIEVAL_TOP_K
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            logger.info(f"🔍 檢索查詢: '{query}' -> {len(results)} 個結果")
            return results
        except Exception as e:
            logger.error(f"❌ 向量檢索失敗: {e}")
            raise VectorStoreException(f"Vector search failed: {e}")

# 全域向量服務實例
vector_service = VectorService()