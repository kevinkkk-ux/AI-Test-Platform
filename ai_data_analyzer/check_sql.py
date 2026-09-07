# check_sql.py
from database import get_db_manager
from sql_generator import SQLGenerator
from config import DEEPSEEK_CONFIG

# 连接数据库
db = get_db_manager()
if not db.connect():
    print("❌ 数据库连接失败")
    exit()

# 获取表结构
table_info = db.get_table_info()
print(f"✅ 获取到 {len(table_info)} 张表的结构信息")

# 初始化SQL生成器
sql_gen = SQLGenerator(DEEPSEEK_CONFIG, table_info)

# 测试生成SQL
test_query = "显示所有用户的会员等级分布"
print(f"\n📝 测试查询：{test_query}")

sql = sql_gen.generate_sql(test_query)
if sql:
    print(f"✅ 生成的SQL：\n{sql}")

    # 验证安全性
    is_valid = sql_gen.validate_sql(sql)
    print(f"🔒 安全验证：{'通过' if is_valid else '不通过'}")

    # 执行查询
    success, result = db.execute_query(sql)
    if success:
        print(f"📊 查询结果：共 {len(result)} 条")
        for row in result[:5]:
            print(f"  {row}")
    else:
        print(f"❌ 查询失败：{result}")
else:
    print("❌ SQL生成失败")

db.disconnect()
