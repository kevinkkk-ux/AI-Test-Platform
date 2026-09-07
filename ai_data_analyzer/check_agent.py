# check_agent.py
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
from visualizer import Visualizer
from database import get_db_manager
from sql_generator import SQLGenerator
from agent import DataAnalysisAgent
from data_analyzer import DataAnalyzer
from config import DEEPSEEK_CONFIG
from report_generator import ReportGenerator
# 1. 连接数据库
print("=" * 50)
print("1. 连接数据库...")
db = get_db_manager()
if not db.connect():
    print("❌ 数据库连接失败")
    exit()
print("✅ 数据库连接成功")

# 2. 获取表结构
print("\n" + "=" * 50)
print("2. 获取表结构...")
table_info = db.get_table_info()
print(f"✅ 获取到 {len(table_info)} 张表")

# 3. 初始化SQL生成器
print("\n" + "=" * 50)
print("3. 初始化SQL生成器...")
sql_gen = SQLGenerator(DEEPSEEK_CONFIG, table_info)
print("✅ SQL生成器初始化完成")

# 4. 初始化数据分析器
print("\n" + "=" * 50)
print("4. 初始化数据分析器...")
data_analyzer = DataAnalyzer(DEEPSEEK_CONFIG)
print("✅ 数据分析器初始化完成")
visualizer = Visualizer()
report_gen = ReportGenerator()
# 5. 初始化智能体（传入data_analyzer）
print("\n" + "=" * 50)
print("5. 初始化数据分析智能体...")
agent = DataAnalysisAgent(
    db_manager=db,
    sql_generator=sql_gen,
    data_analyzer=data_analyzer,
    visualizer=visualizer,
    report_generator=report_gen

)
print("✅ 智能体初始化完成")

# 6. 运行查询
print("\n" + "=" * 50)
print("6. 运行测试查询...")
test_query = "统计各会员等级的用户数量"
print(f"查询问题：{test_query}")

result = agent.run(test_query)

# 7. 输出结果
print("\n" + "=" * 50)
print("7. 查询结果：")
print(f"生成的SQL：\n{result.get('sql')}")
print(f"\n查询到 {len(result.get('query_result', []))} 条数据：")
for row in result.get('query_result', []):
    print(f"  {row}")
print(f"\n分析结果：\n{result.get('analysis')}")
print(f"\n最终报告：\n{result.get('report')}")

if result.get('error'):
    print(f"\n⚠️ 错误信息：{result.get('error')}")

db.disconnect()
print("\n✅ 测试完成")
# 检查是否生成了图表
if result.get('visualization'):
    print(f"\n✅ 已生成可视化图表（base64编码，长度：{len(result['visualization'])}字符）")
else:
    print("\n⚠️ 未生成可视化图表")
