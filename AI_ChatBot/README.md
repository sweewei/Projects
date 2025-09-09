智能對話系統/
├── .env                     # ✅ 環境變數檔案
├── .env.example            # ✅ 環境變數範例檔案
├── .gitignore              # ✅ Git 忽略檔案
├── requirements.txt        # ✅ 依賴清單
├── main.py                 # ✅ 主程式
├── README.md              # ✅ 說明文檔
├── config/
│   ├── init.py         # ✅ 必須建立
│   └── settings.py         # ✅ 配置檔案
├── src/
│   ├── init.py         # ✅ 必須建立
│   ├── models/
│   │   ├── init.py     # ✅ 必須建立
│   │   └── llm_model.py    # ✅ LLM 模型
│   ├── services/
│   │   ├── init.py     # ✅ 必須建立
│   │   ├── chat_service.py # ✅ 聊天服務
│   │   └── vector_service.py # ✅ 向量服務
│   └── utils/
│       ├── init.py     # ✅ 必須建立
│       ├── logger.py       # ✅ 日誌工具
│       └── exceptions.py   # ✅ 異常處理
├── static/
│   └── index.html          # ✅ 前端頁面
└── data/                   # ✅ 資料目錄
    ├── Mplan.pdf          # ✅ 你的 PDF 檔案
    └── vector_store/       # ✅ 向量資料庫（自動生成）