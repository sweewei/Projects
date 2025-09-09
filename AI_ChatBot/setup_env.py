import os
from pathlib import Path

def create_env_files():
    """建立環境變數檔案"""
    
    # .env.example 內容
    env_example_content = '''# ===========================================
# 智能對話系統 - 環境變數配置範例
# ===========================================
# 複製此檔案為 .env 並填入你的實際值

# === API Keys ===
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# === 檔案路徑 ===
PDF_PATH=./data/Mplan.pdf

# === 模型配置 ===
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0

# === 應用配置 ===
FAQ_TIMEOUT_MINUTES=1
MAX_CHAT_HISTORY=50
RETRIEVAL_TOP_K=3
TYPING_SPEED_MS=30

# === 日誌配置 ===
LOG_LEVEL=INFO
'''
    
    # 建立 .env.example
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_example_content)
    print("✅ 已建立 .env.example")
    
    # 如果 .env 不存在，則建立
    if not Path('.env').exists():
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_example_content)
        print("✅ 已建立 .env（請記得修改裡面的 API Key）")
    else:
        print("⚠️  .env 已存在，未覆蓋")

if __name__ == "__main__":
    create_env_files()