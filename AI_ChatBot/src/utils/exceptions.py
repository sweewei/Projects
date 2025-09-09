class ChatSystemException(Exception):
    """聊天系統基礎異常"""
    pass

class VectorStoreException(ChatSystemException):
    """向量資料庫相關異常"""
    pass

class LLMException(ChatSystemException):
    """LLM 相關異常"""
    pass

class DocumentLoadException(ChatSystemException):
    """文檔載入異常"""
    pass
