import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# ========== 数据库配置 ==========
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_DATABASE", "analysis_db"),
    "charset": "utf8mb4"
}

# ========== DeepSeek大模型配置 ==========
DEEPSEEK_CONFIG = {
    "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-v4-flash",
    "temperature": 0.7,
    "max_tokens": 2000
}

# ========== LangGraph配置 ==========
LANGGRAPH_CONFIG = {
    "max_retries": 3,
    "retry_delay": 1
}

# ========== 应用配置 ==========
APP_CONFIG = {
    "title": "AI数据分析智能体",
    "server_name": "127.0.0.1",
    "server_port": 7861,
    "debug": False
}
