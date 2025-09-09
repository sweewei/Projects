import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from config.settings import settings
from src.services.chat_service import chat_service
from src.utils.logger import setup_logger
from src.utils.exceptions import ChatSystemException

# 設置日誌
logger = setup_logger(__name__)

app = FastAPI(
    title="智能對話系統",
    description="基於 RAG 的營養諮詢聊天機器人",
    version="2.0.0"
)

# CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# 靜態文件服務
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    message: Optional[str] = None

class ChatResponse(BaseModel):
    reply: Optional[str]
    retrieved_docs: list
    last_interaction_time: str
    show_faq: bool
    faq_questions: list
    chat_history_length: Optional[int] = None

@app.get("/")
async def root():
    """根路由"""
    return {"message": "智能對話系統 API", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "chat_history_length": len(chat_service.chat_history)
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """聊天端點（非串流模式）"""
    try:
        now = datetime.now()
        show_faq = chat_service.should_show_faq()
        
        # 如果只是檢查 FAQ 狀態
        if req.message is None:
            return ChatResponse(
                reply=None,
                retrieved_docs=[],
                last_interaction_time=now.isoformat(),
                show_faq=show_faq,
                faq_questions=chat_service.get_faq_questions() if show_faq else []
            )
        
        # 處理聊天消息
        response = chat_service.get_response(req.message)
        
        return ChatResponse(
            **response,
            show_faq=False,
            faq_questions=[]
        )
        
    except ChatSystemException as e:
        logger.error(f"聊天系統錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"聊天系統錯誤: {str(e)}")
    except Exception as e:
        logger.error(f"未預期錯誤: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用，請稍後再試")

@app.post("/chat_stream")
async def chat_stream(req: ChatRequest):
    """聊天端點（串流模式）"""
    try:
        if not req.message:
            raise HTTPException(status_code=400, detail="訊息不能為空")
        
        response = chat_service.get_response(req.message)
        
        async def generate():
            reply = response["reply"]
            speed = 2 if len(reply) > 500 else 1
            
            for i in range(0, len(reply), speed):
                chunk = reply[i:i + speed]
                yield chunk
                await asyncio.sleep(settings.TYPING_SPEED_MS / 1000)
            
            yield "[[END]]"  # 結束標記
        
        return StreamingResponse(generate(), media_type="text/plain")
        
    except ChatSystemException as e:
        logger.error(f"串流聊天錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"串流聊天錯誤: {str(e)}")
    except Exception as e:
        logger.error(f"未預期錯誤: {e}")
        raise HTTPException(status_code=500, detail="服務暫時不可用，請稍後再試")

@app.post("/reset")
async def reset_endpoint():
    """重置聊天記憶"""
    try:
        chat_service.reset_memory()
        return {
            "status": "success",
            "message": "聊天記憶已重置",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"重置記憶失敗: {e}")
        raise HTTPException(status_code=500, detail="重置失敗，請稍後再試")

@app.get("/stats")
async def get_stats():
    """獲取系統統計"""
    return {
        "chat_history_length": len(chat_service.chat_history),
        "last_interaction_time": chat_service.last_interaction_time.isoformat() if chat_service.last_interaction_time else None,
        "should_show_faq": chat_service.should_show_faq(),
        "settings": {
            "max_chat_history": settings.MAX_CHAT_HISTORY,
            "retrieval_top_k": settings.RETRIEVAL_TOP_K,
            "llm_model": settings.LLM_MODEL
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 啟動智能對話系統...")
    uvicorn.run(app, host="127.0.0.1", port=8000)