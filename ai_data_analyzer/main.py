import os
os.environ["GRADIO_CONCURRENCY_LIMIT"] = "1"

import gradio as gr
import logging
from database import get_db_manager
from sql_generator import SQLGenerator
from data_analyzer import DataAnalyzer
from visualizer import Visualizer
from report_generator import ReportGenerator
from agent import DataAnalysisAgent
from config import DEEPSEEK_CONFIG, APP_CONFIG

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ========== 全局变量 ==========
agent = None
db = None
report_generator = None


def initialize_system():
    """初始化系统：连接数据库、获取表结构、初始化各模块"""
    global agent, db, report_generator

    print("=" * 50)
    print("正在初始化AI数据分析智能体系统...")
    print("=" * 50)

    # 1. 连接数据库
    print("\n[1/5] 连接数据库...")
    db = get_db_manager()
    if not db.connect():
        print("❌ 数据库连接失败")
        return False
    print("✅ 数据库连接成功")

    # 2. 获取表结构
    print("\n[2/5] 获取数据库表结构...")
    table_info = db.get_table_info()
    print(f"✅ 获取到 {len(table_info)} 张表")
    for t in table_info:
        print(f"   - {t['table_name']} ({t.get('table_comment', '')})")

    # 3. 初始化各模块
    print("\n[3/5] 初始化SQL生成器...")
    sql_generator = SQLGenerator(DEEPSEEK_CONFIG, table_info)
    print("✅ SQL生成器初始化完成")

    print("\n[4/5] 初始化数据分析器、可视化器、报告生成器...")
    data_analyzer = DataAnalyzer(DEEPSEEK_CONFIG)
    visualizer = Visualizer()
    report_generator = ReportGenerator()
    print("✅ 各模块初始化完成")

    # 4. 初始化智能体
    print("\n[5/5] 初始化数据分析智能体（LangGraph工作流）...")
    agent = DataAnalysisAgent(
        db_manager=db,
        sql_generator=sql_generator,
        data_analyzer=data_analyzer,
        visualizer=visualizer,
        report_generator=report_generator
    )
    print("✅ 智能体初始化完成")

    print("\n" + "=" * 50)
    print("🎉 系统初始化完成！")
    print("=" * 50)
    return True


def process_query(query: str):
    """处理用户查询"""
    if not agent:
        return "系统未初始化，请先运行初始化", "", None, "❌ 系统未初始化"

    if not query or not query.strip():
        return "请输入查询问题", "", None, "⚠️ 请输入查询问题"

    print(f"\n收到查询：{query}")

    try:
        result = agent.run(query)

        sql = result.get("sql", "无")
        query_result = result.get("query_result", [])
        error = result.get("error")

        if error:
            status = f"⚠️ 查询完成，但有错误：{error}"
        else:
            status = f"✅ 查询完成，共 {len(query_result)} 条数据"

        import pandas as pd
        if query_result:
            df = pd.DataFrame(query_result)
        else:
            df = pd.DataFrame()

        report_html = report_generator.generate_html(
            query=query,
            sql=sql,
            query_result=query_result,
            analysis=result.get("analysis"),
            visualization=result.get("visualization")
        )

        return report_html, sql, df, status

    except Exception as e:
        logger.error(f"查询处理失败: {str(e)}")
        return f"查询处理失败：{str(e)}", "", None, f"❌ 查询处理失败：{str(e)}"


def build_ui():
    """构建Gradio界面"""
    # ========== 关键：用head注入全局CSS，直接样式化<gradio-app>自定义元素 ==========
    global_head = """
    <style>
        /* 样式化最外层的gradio-app自定义元素 —— 这才是控制页面布局的关键 */
        gradio-app {
            max-width: 1200px !important;
            margin: 0 auto !important;
            width: 100% !important;
            display: block !important;
        }
        /* 同时样式化内部容器，双保险 */
        .gradio-container {
            max-width: 1200px !important;
            margin: 0 auto !important;
            float: none !important;
            width: 100% !important;
            padding: 20px !important;
        }
    </style>
    """

    with gr.Blocks(
        title=APP_CONFIG.get("title", "AI数据分析智能体"),
        head=global_head
    ) as demo:
        gr.Markdown("# 📊 AI数据分析智能体")
        gr.Markdown("基于LangGraph工作流 + DeepSeek大模型，通过自然语言查询电商数据库并生成分析报告")
        gr.Markdown("⚠️ **温馨提示**：大模型生成需要时间，单次查询约10-30秒，请耐心等待，**不要重复点击按钮**")

        with gr.Row():
            with gr.Column(scale=3):
                query_input = gr.Textbox(
                    label="🔍 请输入您的查询问题",
                    placeholder="例如：统计各会员等级的用户数量、查询销量最高的前5个产品、分析每月订单趋势...",
                    lines=2
                )
            with gr.Column(scale=1):
                query_btn = gr.Button("🚀 开始分析", variant="primary", size="lg")

        gr.Markdown("### 💡 快捷查询示例（点击可填充）")
        with gr.Row():
            examples = [
                "统计各会员等级的用户数量",
                "查询销量最高的前5个产品",
                "分析每个月的订单数量和销售额趋势",
                "统计各省份的用户分布",
                "查询评价评分最低的3个产品",
                "分析不同会员等级的平均消费金额"
            ]
            example_buttons = [gr.Button(ex, size="sm") for ex in examples]
            for btn, ex in zip(example_buttons, examples):
                btn.click(lambda x=ex: x, outputs=query_input)

        status_output = gr.Textbox(label="📋 执行状态", lines=1)

        with gr.Tabs():
            with gr.Tab("📄 完整分析报告"):
                report_output = gr.HTML(label="分析报告")

            with gr.Tab("🔧 SQL与查询结果"):
                with gr.Row():
                    with gr.Column(scale=1):
                        sql_output = gr.Code(
                            label="生成的SQL语句",
                            language="sql",
                            lines=12
                        )
                    with gr.Column(scale=2):
                        result_output = gr.Dataframe(
                            label="查询结果",
                            wrap=True
                        )

        query_btn.click(
            process_query,
            inputs=[query_input],
            outputs=[report_output, sql_output, result_output, status_output]
        )

        query_input.submit(
            process_query,
            inputs=[query_input],
            outputs=[report_output, sql_output, result_output, status_output]
        )

    return demo


if __name__ == "__main__":
    success = initialize_system()

    if success:
        demo = build_ui()
        print(f"\n🚀 系统启动成功！请在浏览器中访问：http://127.0.0.1:{APP_CONFIG.get('server_port', 7861)}")
        demo.launch(
            server_name="127.0.0.1",
            server_port=APP_CONFIG.get("server_port", 7861),
            theme=gr.themes.Soft()
        )
    else:
        print("❌ 系统初始化失败，请检查配置")
