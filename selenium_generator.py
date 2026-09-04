# selenium_generator.py
import os
import json
import pandas as pd
from datetime import datetime
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import DEEPSEEK_API_KEY, SCRIPT_DIR

# 初始化大模型
llm = ChatDeepSeek(
    model="deepseek-v4-flash",
    api_key=DEEPSEEK_API_KEY,
    temperature=0.1
)


def generate_selenium_script(config_json: str, test_case_file: str) -> tuple:
    """
    根据元素配置JSON和测试用例Excel，生成Selenium自动化脚本
    返回：(脚本代码, 保存路径)
    """
    # 1. 解析配置JSON
    try:
        config = json.loads(config_json)
    except json.JSONDecodeError as e:
        return f"配置JSON解析失败: {e}", ""

    url = config.get("url", "")
    elements = config.get("elements", [])
    func_desc = config.get("function_desc", "未指定功能")

    # 2. 读取测试用例Excel，获取字段列表
    try:
        df = pd.read_excel(test_case_file, dtype=str)
        case_columns = df.columns.tolist()
        case_count = len(df)
    except Exception as e:
        return f"读取测试用例文件失败: {e}", ""

    # 3. 构建元素描述
    elements_description = "\n".join([
        f"- {e.get('name', '')}: 定位方式={e.get('locator_type', 'id')}, 定位值={e.get('locator_value', '')}"
        for e in elements
    ])

    # 4. 构建提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个Selenium自动化测试专家。请为以下测试场景生成完整的Selenium自动化测试Python脚本。
只输出Python代码，不要任何解释或markdown标记。

要求：
1. 生成完整的Python脚本，可以直接运行
2. 使用Edge浏览器驱动，通过webdriver_manager自动管理
3. 读取测试用例Excel文件，逐条执行测试
4. 根据页面元素配置，自动填充输入框并点击提交按钮
5. 包含异常处理和日志输出
6. 使用pytest框架编写测试函数
7. 测试用例文件名从测试用例字段中读取对应的值进行填充
8. 提交按钮点击后，等待页面响应并验证结果
9. 代码要简洁、健壮、可维护
10. 符合PEP8规范"""),
        ("human", """## 测试场景信息
- 功能描述: {func_desc}
- 目标页面URL: {url}
- 测试用例文件路径: {test_case_file}
- 测试用例字段: {case_columns}
- 测试用例数量: {case_count}条

## 页面元素信息
{elements_description}

请生成完整的Selenium自动化测试脚本。""")
    ])

    # 5. 调用大模型生成脚本
    try:
        chain = prompt | llm | StrOutputParser()
        script_code = chain.invoke({
            "func_desc": func_desc,
            "url": url,
            "test_case_file": test_case_file,
            "case_columns": ", ".join(case_columns),
            "case_count": case_count,
            "elements_description": elements_description
        })

        # 6. 清理代码格式
        script_code = script_code.strip()
        if script_code.startswith("```python"):
            script_code = script_code[9:]
        elif script_code.startswith("```"):
            script_code = script_code[3:]
        if script_code.endswith("```"):
            script_code = script_code[:-3]
        script_code = script_code.strip()

    except Exception as e:
        return f"大模型生成脚本失败: {e}", ""

    # 7. 保存脚本到文件
    os.makedirs(SCRIPT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_func = func_desc.replace(" ", "_").replace("功能", "")
    filename = f"selenium_{clean_func}_{timestamp}.py"
    file_path = os.path.join(SCRIPT_DIR, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(script_code)

    return script_code, file_path


# 控制台测试
if __name__ == "__main__":
    test_config = json.dumps({
        "url": "http://127.0.0.1:8080/login",
        "elements": [
            {"name": "用户名输入框", "locator_type": "id", "locator_value": "username"},
            {"name": "密码输入框", "locator_type": "id", "locator_value": "password"},
            {"name": "登录按钮", "locator_type": "id", "locator_value": "loginBtn"}
        ],
        "function_desc": "登录功能"
    }, ensure_ascii=False)

    code, path = generate_selenium_script(test_config, "files/login_testcases.xlsx")
    print(f"脚本已保存到: {path}")
    print("=" * 50)
    print(code)
