import os
from pathlib import Path
from datetime import timedelta
from typing import List
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class Settings:
    """應用程式統一配置"""
    
    # === API 配置 ===
    GROQ_API_KEY: str = os.getenv('GROQ_API_KEY', '')
    GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY', '')
    
    # === 檔案路徑 ===
    PROJECT_ROOT = Path(__file__).parent.parent
    PDF_PATH: str = os.getenv('PDF_PATH', str(PROJECT_ROOT / 'data' / 'Mplan.pdf'))
    VECTOR_STORE_PATH: str = str(PROJECT_ROOT / 'data' / 'vector_store')
    
    # === 模型配置 ===
    EMBEDDING_MODEL: str = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    LLM_MODEL: str = os.getenv('LLM_MODEL', 'llama-3.3-70b-versatile')
    LLM_TEMPERATURE: float = float(os.getenv('LLM_TEMPERATURE', '0'))
    
    # === 應用配置 ===
    FAQ_TIMEOUT: timedelta = timedelta(minutes=int(os.getenv('FAQ_TIMEOUT_MINUTES', '1')))
    MAX_CHAT_HISTORY: int = int(os.getenv('MAX_CHAT_HISTORY', '50'))
    RETRIEVAL_TOP_K: int = int(os.getenv('RETRIEVAL_TOP_K', '3'))
    TYPING_SPEED_MS: int = int(os.getenv('TYPING_SPEED_MS', '30'))
    
    # === FAQ 問題 ===
    FAQ_QUESTIONS: List[str] = [
        "這個產品適合糖尿病患者使用嗎？",
        "有哪些產品有助於腸胃健康？",
        "哪些產品比較適合孕婦食用？"
    ]
    
    # === 系統提示詞 ===
    SYSTEM_PROMPT: str = """
    You are a top-level professional nutritionist.  
    You are an expert in human physiology, nutrition science, and ingredient safety.  
    You fully understand how each ingredient affects the human body, whether patients with specific conditions can use the product,  
    and you always provide evidence-based, science-backed explanations.  
    When answering, integrate both the retrieved context and your professional knowledge, citing scientific reasoning when possible.  

    Rules for your reply:
    1. Always reply in the same language as the user's input.  
    2. If the user's input language is NOT Chinese, then after your main reply,  
       also provide a translated Chinese version under a section titled:  
       "（中文翻譯）".
    """
    
    # === 日誌配置 ===
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # === CORS 配置 ===
    CORS_ORIGINS: List[str] = ["*"]
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    def validate_required_keys(self) -> None:
        """驗證必要的環境變數"""
        required_keys = ['GROQ_API_KEY']
        missing_keys = [key for key in required_keys if not getattr(self, key)]
        
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {missing_keys}")

# 全域設定實例
settings = Settings()
settings.validate_required_keys()