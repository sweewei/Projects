from datetime import datetime
from typing import List, Dict, Optional, Any
from src.models.llm_model import llm_model
from src.services.vector_service import vector_service
from config.settings import settings
from src.utils.logger import setup_logger
from src.utils.exceptions import ChatSystemException

logger = setup_logger(__name__)

class ChatService:
    """聊天服務"""
    
    def __init__(self):
        self.chat_history: List[Dict[str, str]] = []
        self.last_interaction_time: Optional[datetime] = None
    
    def should_show_faq(self) -> bool:
        """檢查是否應該顯示 FAQ"""
        if not self.last_interaction_time:
            return False
        return datetime.now() - self.last_interaction_time > settings.FAQ_TIMEOUT
    
    def get_faq_questions(self) -> List[str]:
        """獲取 FAQ 問題列表"""
        return settings.FAQ_QUESTIONS.copy()
    
    def reset_memory(self) -> None:
        """清除聊天記憶"""
        self.chat_history = []
        self.last_interaction_time = None
        logger.info("🧹 聊天記憶已清除")
    
    def _manage_history_size(self) -> None:
        """管理聊天歷史大小，防止記憶體洩漏"""
        if len(self.chat_history) > settings.MAX_CHAT_HISTORY:
            # 保留最近的對話，但保留第一條系統消息（如果有）
            keep_count = settings.MAX_CHAT_HISTORY - 10
            self.chat_history = self.chat_history[-keep_count:]
            logger.info(f"📝 聊天歷史已截斷至 {len(self.chat_history)} 條")
    
    def get_response(self, user_message: str) -> Dict[str, Any]:
        """獲取聊天回應"""
        try:
            # 更新互動時間
            self.last_interaction_time = datetime.now()
            
            # 檢索相關文檔
            retrieved_docs_with_score = vector_service.similarity_search_with_score(
                user_message, k=settings.RETRIEVAL_TOP_K
            )
            
            # 記錄檢索結果
            self._log_retrieval_results(retrieved_docs_with_score)
            
            # 建構上下文
            context = self._build_context(retrieved_docs_with_score)
            
            # 添加用戶消息到歷史
            self.chat_history.append({"role": "user", "content": user_message})
            
            # 建構提示詞
            prompt = llm_model.build_prompt(self.chat_history, context)
            
            # 生成回應
            generated_answer = llm_model.generate_response(prompt)
            
            # 添加助手回應到歷史
            self.chat_history.append({"role": "assistant", "content": generated_answer})
            
            # 管理歷史大小
            self._manage_history_size()
            
            # 整理檢索文檔摘要
            retrieved_docs_summary = [
                {
                    "source": doc.metadata.get("source", ""),
                    "score": float(score),
                    "preview": doc.page_content[:200]
                }
                for doc, score in retrieved_docs_with_score
            ]
            
            return {
                "reply": generated_answer,
                "retrieved_docs": retrieved_docs_summary,
                "last_interaction_time": self.last_interaction_time.isoformat(),
                "chat_history_length": len(self.chat_history)
            }
            
        except Exception as e:
            logger.error(f"❌ 獲取聊天回應失敗: {e}")
            raise ChatSystemException(f"Failed to get chat response: {e}")
    
    def _build_context(self, retrieved_docs_with_score) -> str:
        """建構檢索上下文"""
        context_lines = []
        for doc, score in retrieved_docs_with_score:
            context_lines.append(f"[Score: {score:.4f}] {doc.page_content}")
        return "\n".join(context_lines)
    
    def _log_retrieval_results(self, retrieved_docs_with_score) -> None:
        """記錄檢索結果"""
        logger.info("=== 檢索結果 (含分數) ===")
        for doc, score in retrieved_docs_with_score:
            source = doc.metadata.get('source', 'Unknown')
            preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            logger.info(f"[Score: {score:.4f}] {source}: {preview}")

# 全域聊天服務實例
chat_service = ChatService()