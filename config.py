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
# ========== Selenium自动化执行配置 ==========
SELENIUM_TARGET = {
    # 本地测试页面（用你项目里的login.html）
    "login_url": r"file:///C:/Users/hp/PycharmProjects/PythonProject6/login.html",
    "register_url": "http://127.0.0.1:8080/register",
    # 元素定位器
    "login_username": "username",
    "login_password": "password",
    "login_submit": "loginBtn",
}

# ========== 默认测试用例文件路径 ==========
CASE_PATH = "files/testcases.xlsx"
# ========== 数据分析智能体表结构配置 ==========
DB_SCHEMA = """
表1：test_case_main（测试用例主表）
  - id: 主键ID，整数，自增
  - case_type: 用例类型，字符串（登录/注册/修改个人信息）
  - group_num: 本次生成用例数量，整数
  - case_title: 用例组标题，字符串
  - case_content: 用例字段规则，text类型
  - generate_type: 生成方式，整数（0=等价类, 1=边界值, 2=AI, 3=RAG）
  - create_time: 创建时间，datetime

表2：test_case_detail（测试用例明细表）
  - id: 主键ID，整数，自增
  - main_id: 关联主表ID，整数
  - case_no: 用例编号，字符串（如TC01、TC02）
  - field_values: 字段值，JSON类型，存储所有输入字段的值，格式如 {"账号":"user123", "密码":"123456"}
  - scene_desc: 场景描述，字符串
  - case_type: 用例类型，字符串（有效等价类/无效等价类/健壮边界值(合法边界)/健壮边界值(非法边界)）
  - expected_result: 预期结果，字符串
  - create_time: 创建时间，datetime

表3：operation_log（操作日志表）
  - id: 主键ID，整数
  - user_id: 用户ID，整数
  - operation_type: 操作类型，字符串
  - operation_content: 操作内容，字符串
  - related_id: 关联ID，整数
  - create_time: 创建时间，datetime

关联关系：
- test_case_detail.main_id = test_case_main.id

注意：
1. 查询detail表的具体字段值时，使用JSON_EXTRACT函数，例如 JSON_EXTRACT(field_values, '$.账号')
2. 统计类查询优先查main表，不需要join detail表
3. 时间格式化使用 DATE_FORMAT(create_time, '%Y-%m-%d')
"""
