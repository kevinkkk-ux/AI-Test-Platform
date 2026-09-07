# web_ui.py
import os
os.environ["GRADIO_CONCURRENCY_LIMIT"] = "1"

import json
import gradio as gr
from data_generator import (
    generate_login_case,
    generate_register_case,
    generate_modify_profile_case
)
from config import OUTPUT_PATHS
from api_doc_parser import parse_doc_for_selenium
from selenium_generator import generate_selenium_script
from auto_test import execute_login_cases, execute_register_cases
from data_analyzer import analyze


# ========== 测试用例生成相关函数 ==========
def on_login_click(group_num):
    df, main_id = generate_login_case(int(group_num))
    return df, OUTPUT_PATHS["login"]


def on_register_click(group_num):
    df, main_id = generate_register_case(int(group_num))
    return df, OUTPUT_PATHS["register"]


def on_modify_click(group_num):
    df, main_id = generate_modify_profile_case(int(group_num))
    return df, OUTPUT_PATHS["modify_profile"]


def on_all_click(group_num):
    """一键生成全部三套"""
    df1, _ = generate_login_case(int(group_num))
    df2, _ = generate_register_case(int(group_num))
    df3, _ = generate_modify_profile_case(int(group_num))
    return (
        df1, OUTPUT_PATHS["login"],
        df2, OUTPUT_PATHS["register"],
        df3, OUTPUT_PATHS["modify_profile"]
    )


# ========== Selenium脚本生成相关函数 ==========
def on_parse_click(file_obj):
    """智能解析接口文档"""
    if not file_obj:
        return (
            json.dumps({"url": "", "elements": [], "function_desc": "请先上传文档"}, ensure_ascii=False, indent=2),
            "请先上传文档"
        )
    try:
        result = parse_doc_for_selenium(file_obj.name)
        config_json = json.dumps(result, ensure_ascii=False, indent=2)
        element_count = len(result.get("elements", []))
        status = f"✅ 解析成功！识别到 {element_count} 个元素，功能：{result.get('function_desc', '未识别')}"
        return config_json, status
    except Exception as e:
        return (
            json.dumps({"url": "", "elements": [], "function_desc": f"解析失败: {e}"}, ensure_ascii=False, indent=2),
            f"❌ 解析失败: {e}"
        )


def on_generate_script(config_json, case_file):
    """生成Selenium脚本"""
    if not case_file:
        return "请先上传测试用例Excel文件", ""
    try:
        code, file_path = generate_selenium_script(config_json, case_file.name)
        if file_path:
            save_msg = f"✅ 脚本已生成并保存至: {file_path}"
        else:
            save_msg = "⚠️ 脚本生成失败，请查看错误信息"
        return code, save_msg
    except Exception as e:
        return f"生成失败: {e}", ""


# ========== 自动化测试执行相关函数 ==========
def on_execute_click(url, case_file, headless, exec_type):
    """执行自动化测试"""
    case_path = case_file.name if case_file else None
    try:
        if exec_type == "登录":
            summary, logs = execute_login_cases(
                url=url,
                case_file=case_path,
                headless=headless
            )
        else:
            summary, logs = execute_register_cases(
                url=url,
                case_file=case_path,
                headless=headless
            )
        return summary, logs
    except Exception as e:
        return f"执行失败: {e}", str(e)


# ========== 数据分析智能体相关函数 ==========
def on_analyze_click(question, chart_type):
    """执行数据分析"""
    if not question.strip():
        return "请输入查询问题", None, "请输入查询问题", None

    try:
        sql, df, report = analyze(question)

        # 生成图表
        chart = None
        if not df.empty and "错误" not in df.columns:
            try:
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
                plt.rcParams['axes.unicode_minus'] = False

                fig, ax = plt.subplots(figsize=(10, 6))
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

                if chart_type == "饼图" or (chart_type == "自动选择" and len(df) <= 8 and len(numeric_cols) >= 1):
                    if len(df.columns) >= 2 and len(numeric_cols) >= 1:
                        labels = df.iloc[:, 0].astype(str).tolist()
                        values = df[numeric_cols[0]].tolist()
                        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
                        ax.set_title(question)
                        chart = fig
                elif chart_type == "柱状图" or (chart_type == "自动选择" and len(numeric_cols) >= 1):
                    if len(df.columns) >= 2 and len(numeric_cols) >= 1:
                        x = df.iloc[:, 0].astype(str).tolist()
                        y = df[numeric_cols[0]].tolist()
                        bars = ax.bar(x, y, color='steelblue')
                        ax.set_xlabel(df.columns[0])
                        ax.set_ylabel(numeric_cols[0])
                        ax.set_title(question)
                        plt.xticks(rotation=45, ha='right')
                        for bar in bars:
                            height = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width()/2., height,
                                    f'{int(height)}', ha='center', va='bottom')
                        plt.tight_layout()
                        chart = fig
                elif chart_type == "折线图":
                    if len(df.columns) >= 2 and len(numeric_cols) >= 1:
                        x = df.iloc[:, 0].astype(str).tolist()
                        y = df[numeric_cols[0]].tolist()
                        ax.plot(x, y, marker='o', linewidth=2, color='steelblue')
                        ax.set_xlabel(df.columns[0])
                        ax.set_ylabel(numeric_cols[0])
                        ax.set_title(question)
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()
                        chart = fig
            except Exception as e:
                print(f"图表生成失败: {e}")

        return sql, df, report, chart
    except Exception as e:
        return f"分析失败: {e}", None, f"分析失败: {e}", None


# ========== Gradio界面 ==========
with gr.Blocks(title="AI辅助测试用例生成系统") as demo:
    gr.Markdown("# 📝 AI辅助测试用例生成系统")
    gr.Markdown("⚠️ **温馨提示**：大模型生成需要时间，单模块约20-40秒，全部生成约1-2分钟，请耐心等待，**不要重复点击按钮**")

    # ========== 选项卡1：测试用例生成 ==========
    with gr.Tab("测试用例生成"):
        gr.Markdown("## 选择功能模块，设置用例数量，点击生成")

        with gr.Row():
            group_num = gr.Number(value=10, label="生成用例数量", minimum=5, maximum=50, step=1)
            btn_all = gr.Button("🔴 一键生成全部三套（约1-2分钟）", variant="primary", scale=2)

        # 登录模块
        with gr.Accordion("🔐 模块1：登录模块", open=True):
            gr.Markdown("**字段规则**：账号（1-20位字母数字）、密码（6-16位字母数字）")
            btn_login = gr.Button("生成登录测试用例")
            gr.Markdown("⏱️ 预计耗时：20-40秒")
            with gr.Row():
                login_table = gr.Dataframe(label="登录用例预览", wrap=True)
                login_file = gr.File(label="下载登录用例Excel")

        # 注册模块
        with gr.Accordion("📝 模块2：注册模块", open=False):
            gr.Markdown("**字段规则**：账号、密码、确认密码、邮箱、手机号")
            btn_register = gr.Button("生成注册测试用例")
            gr.Markdown("⏱️ 预计耗时：20-40秒")
            with gr.Row():
                register_table = gr.Dataframe(label="注册用例预览", wrap=True)
                register_file = gr.File(label="下载注册用例Excel")

        # 修改个人信息模块
        with gr.Accordion("👤 模块3：修改个人信息模块", open=False):
            gr.Markdown("**字段规则**：昵称、手机号、邮箱")
            btn_modify = gr.Button("生成修改个人信息测试用例")
            gr.Markdown("⏱️ 预计耗时：20-40秒")
            with gr.Row():
                modify_table = gr.Dataframe(label="修改个人信息用例预览", wrap=True)
                modify_file = gr.File(label="下载修改个人信息用例Excel")

    # ========== 选项卡2：自动化脚本生成 ==========
    with gr.Tab("自动化脚本生成"):
        gr.Markdown("## 🤖 AI协同Selenium自动化测试脚本生成")
        gr.Markdown("上传接口文档→智能解析元素配置→上传测试用例Excel→生成Selenium自动化脚本")

        with gr.Row():
            # 左侧：上传文档与解析
            with gr.Column(scale=1):
                gr.Markdown("### 上传接口文档（智能解析）")
                doc_upload = gr.File(
                    label="上传文档（支持txt, docx, pdf, md）",
                    file_count="single",
                    file_types=[".txt", ".docx", ".pdf", ".md"]
                )
                parse_btn = gr.Button("🚀 智能解析接口文档", variant="primary")
                parse_status = gr.Textbox(label="解析状态", lines=1)

                gr.Markdown("---")
                gr.Markdown("### 上传测试用例Excel")
                case_file_upload = gr.File(
                    label="测试用例文件（Excel格式）",
                    file_count="single",
                    file_types=[".xlsx"]
                )

            # 右侧：解析结果展示（可编辑）
            with gr.Column(scale=1):
                gr.Markdown("### 解析结果配置（可编辑）")
                parsed_config = gr.Textbox(
                    label="解析结果配置（JSON格式，可编辑）",
                    value=json.dumps({
                        "url": "http://127.0.0.1:8080/login",
                        "elements": [
                            {"name": "用户名输入框", "locator_type": "id", "locator_value": "username"},
                            {"name": "密码输入框", "locator_type": "id", "locator_value": "password"},
                            {"name": "登录按钮", "locator_type": "id", "locator_value": "loginBtn"}
                        ],
                        "function_desc": "登录功能"
                    }, ensure_ascii=False, indent=2),
                    lines=15,
                    interactive=True
                )

        gr.Markdown("---")
        generate_script_btn = gr.Button("🛠️ 生成Selenium脚本", variant="primary", size="lg")
        script_save_msg = gr.Textbox(label="保存结果", lines=1)
        script_code = gr.Code(
            label="生成的Selenium脚本代码",
            language="python",
            lines=25,
            interactive=True
        )

    # ========== 选项卡3：自动化测试执行 ==========
    with gr.Tab("自动化测试执行"):
        gr.Markdown("## 🚀 自动化测试执行")
        gr.Markdown("配置目标页面和测试用例，一键执行自动化测试，输出执行结果和通过率")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 执行配置")
                exec_url = gr.Textbox(
                    label="目标页面URL",
                    value=r"file:///C:/Users/hp/PycharmProjects/PythonProject6/login.html",
                    lines=1
                )
                exec_case_file = gr.File(
                    label="测试用例Excel（不选则用默认）",
                    file_count="single",
                    file_types=[".xlsx"]
                )
                exec_headless = gr.Checkbox(label="无头模式（不显示浏览器窗口）", value=True)
                exec_type = gr.Radio(
                    choices=["登录", "注册"],
                    value="登录",
                    label="测试类型"
                )
                exec_btn = gr.Button("▶️ 开始执行自动化测试", variant="primary", size="lg")

            with gr.Column(scale=1):
                gr.Markdown("### 执行结果")
                exec_summary = gr.Textbox(label="执行摘要", lines=2)
                exec_logs = gr.Textbox(label="执行日志", lines=15, max_lines=30)

    # ========== 选项卡4：数据分析智能体 ==========
    with gr.Tab("数据分析智能体"):
        gr.Markdown("## 📊 AI数据分析智能体")
        gr.Markdown("输入自然语言查询，AI自动生成SQL、执行查询、生成分析报告和可视化图表")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 查询输入")
                analyze_question = gr.Textbox(
                    label="输入自然语言查询",
                    placeholder="例如：统计各功能模块的测试用例数量",
                    lines=3
                )
                chart_type = gr.Dropdown(
                    choices=["自动选择", "饼图", "柱状图", "折线图", "表格"],
                    value="自动选择",
                    label="图表类型"
                )
                analyze_btn = gr.Button("🔍 执行分析", variant="primary", size="lg")

                gr.Markdown("### 示例查询")
                gr.Markdown("""
                1. 统计各功能模块的测试用例数量
                2. 查看最近生成的10条测试用例记录
                3. 统计各种用例类型的分布情况
                4. 计算每天生成的用例数量趋势
                5. 查看所有操作日志记录
                6. 统计登录模块的有效等价类用例数量
                """)

            with gr.Column(scale=1):
                gr.Markdown("### 输出结果")
                analyze_sql = gr.Code(label="生成的SQL语句", language="sql", lines=5)
                with gr.Tabs():
                    with gr.TabItem("分析报告"):
                        analyze_report = gr.Markdown()
                    with gr.TabItem("查询结果"):
                        analyze_df = gr.Dataframe(label="查询结果", wrap=True)
                    with gr.TabItem("可视化图表"):
                        analyze_chart = gr.Plot(label="可视化图表")

    # ========== 选项卡5：关于系统 ==========
    with gr.Tab("关于系统"):
        gr.Markdown("""
        ## 系统说明
        - **技术栈**：Python + LangChain + DeepSeek大模型 + Gradio + MySQL + Selenium
        - **生成方法**：等价类划分法 + 健壮边界值法
        - **输出格式**：Excel（.xlsx）+ MySQL数据库记录 + Selenium自动化脚本
        - **用例类型**：有效等价类、无效等价类、健壮边界值(合法边界)、健壮边界值(非法边界)

        ## 功能模块
        ### 1. 测试用例生成
        - 登录模块 → `files/login_testcases.xlsx`
        - 注册模块 → `files/register_testcases.xlsx`
        - 修改个人信息模块 → `files/modify_profile_testcases.xlsx`

        ### 2. 自动化脚本生成
        - 上传接口文档，AI智能解析页面元素配置
        - 结合测试用例Excel，生成Selenium自动化测试脚本
        - 脚本保存至 `files/scripts/` 目录

        ### 3. 自动化测试执行
        - 配置目标页面URL和测试用例Excel
        - 一键执行自动化测试
        - 输出执行摘要、详细日志和通过率
        - 结果自动写回Excel

        ### 4. 数据分析智能体
        - 自然语言转SQL查询
        - 自动执行数据库查询
        - 生成数据分析报告
        - 可视化图表展示

        ## 数据库表结构
        - `test_case_main`：用例主表，记录每次生成的基本信息
        - `test_case_detail`：用例明细表，记录每一条具体测试用例
        - `operation_log`：操作日志表

        ## 使用说明
        1. 在"测试用例生成"选项卡中，设置用例数量，点击生成
        2. 在"自动化脚本生成"选项卡中，上传接口文档→解析→上传测试用例→生成脚本
        3. 在"自动化测试执行"选项卡中，配置执行参数，点击开始执行
        4. 在"数据分析智能体"选项卡中，输入自然语言查询，点击执行分析
        5. 生成结果可在页面预览，或下载文件
        """)

    # ========== 绑定事件 ==========
    # 测试用例生成
    btn_login.click(on_login_click, inputs=[group_num], outputs=[login_table, login_file])
    btn_register.click(on_register_click, inputs=[group_num], outputs=[register_table, register_file])
    btn_modify.click(on_modify_click, inputs=[group_num], outputs=[modify_table, modify_file])
    btn_all.click(
        on_all_click,
        inputs=[group_num],
        outputs=[
            login_table, login_file,
            register_table, register_file,
            modify_table, modify_file
        ]
    )

    # Selenium脚本生成
    parse_btn.click(on_parse_click, inputs=[doc_upload], outputs=[parsed_config, parse_status])
    generate_script_btn.click(
        on_generate_script,
        inputs=[parsed_config, case_file_upload],
        outputs=[script_code, script_save_msg]
    )

    # 自动化测试执行
    exec_btn.click(
        on_execute_click,
        inputs=[exec_url, exec_case_file, exec_headless, exec_type],
        outputs=[exec_summary, exec_logs]
    )

    # 数据分析智能体
    analyze_btn.click(
        on_analyze_click,
        inputs=[analyze_question, chart_type],
        outputs=[analyze_sql, analyze_df, analyze_report, analyze_chart]
    )


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        theme=gr.themes.Soft()
    )
