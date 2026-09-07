# check_db.py（临时测试用，测完可以删）
from database import get_db_manager

db = get_db_manager()
if db.connect():
    print("✅ 数据库连接成功")

    # 获取表结构
    tables = db.get_table_info()
    print(f"📊 共找到 {len(tables)} 张表：")
    for t in tables:
        print(f"  - {t['table_name']} ({t['table_comment']})，{len(t['columns'])}个字段")

    # 查一下用户表
    success, result = db.execute_query("SELECT COUNT(*) as cnt FROM users")
    if success:
        print(f"👤 users表共有 {result[0]['cnt']} 条用户数据")

    db.disconnect()
else:
    print("❌ 数据库连接失败，请检查密码和配置")
