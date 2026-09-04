# config.py 项目全部配置
import os
from dotenv import load_dotenv

load_dotenv()

# ========== LLM大模型配置 ==========
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = "deepseek-v4-flash"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# ========== 测试用例生成配置 ==========
CASE_GENERATE_TYPE = {
    "EQUIV": 0,
    "BOUND": 1,
    "AI": 2
}

# ========== 数据库配置（暂时不用，保留） ==========
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": os.getenv("DB_PASSWORD", ""),
    "database": "soft_test_db"
}

# ========== 三个模块的Excel输出路径（任务要求） ==========
OUTPUT_PATHS = {
    "login": "files/login_testcases.xlsx",
    "register": "files/register_testcases.xlsx",
    "modify_profile": "files/modify_profile_testcases.xlsx"
}

# 确保files目录存在
os.makedirs("files", exist_ok=True)
# ========== Selenium自动化脚本配置 ==========
SCRIPT_DIR = "files/scripts"  # 生成的脚本保存目录
os.makedirs(SCRIPT_DIR, exist_ok=True)
