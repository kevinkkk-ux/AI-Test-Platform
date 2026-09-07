# data_analyzer.py
import json
import pandas as pd
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage, HumanMessage
from config import DEEPSEEK_API_KEY, DB_SCHEMA
from database import get_db_manager

# 初始化大模型
llm = ChatDeepSeek(
    model="deepseek-v4-flash",
    api_key=DEEPSEEK_API_KEY,
    temperature=0.1
)


def nl_to_sql(question: str) -> str:
    """
    自然语言转SQL
    :param question: 自然语言查询
    :return: SQL语句
    """
    system_prompt = f"""你是一个专业的MySQL数据库查询专家。请根据用户的自然语言问题，生成正确的MySQL查询语句。

数据库表结构：
{DB_SCHEMA}

严格要求：
1. 只生成SELECT查询语句，绝对禁止INSERT、UPDATE、DELETE、DROP、ALTER等任何修改数据或表结构的操作
2. 只返回SQL语句本身，不要任何解释、不要markdown代码块、不要多余文字
3. 表名和字段名必须和上面提供的表结构完全一致
4. 如果用户要求修改数据或表结构，回复：本系统只支持查询操作，不支持修改
5. SQL语句要简洁高效，使用正确的MySQL语法
6. 字段别名使用中文，方便阅读
7. 时间字段使用DATE_FORMAT格式化，例如 DATE_FORMAT(create_time, '%Y-%m-%d')
8. 查询detail表的具体字段值时，使用JSON_EXTRACT函数，例如 JSON_EXTRACT(field_values, '$.账号')
9. 统计各功能模块数量时，直接查test_case_main表，按case_type分组
10. 如果问题不明确，优先返回最可能的查询语句"""

    user_prompt = f"用户问题：{question}\n\n请生成对应的MySQL查询语句："

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        sql = response.content.strip()

        # 清理可能的markdown代码块
        if sql.startswith("```sql"):
            sql = sql[6:]
        elif sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        sql = sql.strip()

        # 安全检查：确保是SELECT语句
        if not sql.lower().startswith("select"):
            return "错误：本系统只支持SELECT查询操作"

        return sql
    except Exception as e:
        return f"SQL生成失败: {e}"


def execute_sql(sql: str) -> pd.DataFrame:
    """
    执行SQL查询，返回DataFrame
    """
    try:
        db = get_db_manager()
        conn = db.get_connection()
        df = pd.read_sql(sql, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame({"错误": [str(e)]})


def generate_report(question: str, df: pd.DataFrame) -> str:
    """
    根据查询结果生成分析报告
    """
    if df.empty or "错误" in df.columns:
        return "查询结果为空或执行出错，无法生成分析报告。"

    # 把数据转成文本，限制长度
    data_text = df.to_string(max_rows=20, max_cols=10)
    if len(data_text) > 3000:
        data_text = data_text[:3000] + "\n...(数据过多，已截断)"

    system_prompt = """你是一个专业的数据分析师。请根据用户的查询问题和数据库查询结果，生成一份简洁明了的数据分析报告。

报告要求：
1. 先总结查询结果的核心发现（2-3句话）
2. 列出关键数据指标
3. 如果有趋势或分布，简要分析
4. 语言简洁专业，不要废话
5. 不要编造数据，只基于查询结果分析
6. 用中文回答
7. 使用Markdown格式，适当使用加粗和列表"""

    user_prompt = f"""用户查询问题：{question}

查询结果：
{data_text}

请生成数据分析报告："""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        return response.content.strip()
    except Exception as e:
        return f"报告生成失败: {e}"


def analyze(question: str) -> tuple:
    """
    完整的数据分析流程：自然语言→SQL→执行→报告
    :return: (SQL语句, 查询结果DataFrame, 分析报告)
    """
    # 1. 自然语言转SQL
    sql = nl_to_sql(question)
    if sql.startswith("错误") or sql.startswith("SQL生成失败"):
        return sql, pd.DataFrame(), sql

    # 2. 执行SQL
    df = execute_sql(sql)

    # 3. 生成分析报告
    report = generate_report(question, df)

    return sql, df, report


# 控制台测试
if __name__ == "__main__":
    test_question = "统计各功能模块的测试用例数量"
    sql, df, report = analyze(test_question)
    print("=" * 50)
    print("生成的SQL：")
    print(sql)
    print("=" * 50)
    print("查询结果：")
    print(df)
    print("=" * 50)
    print("分析报告：")
    print(report)
