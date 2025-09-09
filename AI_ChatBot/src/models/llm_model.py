from typing import List, Dict, Optional
from langchain_groq import ChatGroq
from config.settings import settings
from src.utils.logger import setup_logger
from src.utils.exceptions import LLMException

logger = setup_logger(__name__)

class LLMModel:
    """LLM 模型封裝"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self) -> ChatGroq:
        """初始化 LLM"""
        try:
            llm = ChatGroq(
                temperature=settings.LLM_TEMPERATURE,
                model=settings.LLM_MODEL,
                api_key=settings.GROQ_API_KEY
            )
            logger.info(f"✅ LLM 初始化成功: {settings.LLM_MODEL}")
            return llm
        except Exception as e:
            logger.error(f"❌ LLM 初始化失敗: {e}")
            raise LLMException(f"Failed to initialize LLM: {e}")
    
    def generate_response(self, prompt: str) -> str:
        """生成回應"""
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"❌ LLM 生成回應失敗: {e}")
            raise LLMException(f"Failed to generate response: {e}")
    
    def build_prompt(self, history: List[Dict[str, str]], context: str) -> str:
        """建構提示詞"""
        conversation_str = "\n".join([f"{m['role']}: {m['content']}" for m in history])
        
        prompt = f"""
        {settings.SYSTEM_PROMPT}

        Here is the conversation so far:  
        {conversation_str}  

        Based on the following retrieved context, answer the user's last question:  
        Context:  
        {context}  

        Answer:
        """
        return prompt

# 全域 LLM 模型實例
llm_model = LLMModel()