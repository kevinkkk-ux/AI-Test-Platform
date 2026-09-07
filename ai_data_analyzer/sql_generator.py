# sql_generator.py
from typing import Dict, Any, List, Optional
import re
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class SQLGenerator:
    """SQL语句生成器"""

    def __init__(self, config: Dict[str, Any], table_info: List[Dict[str, Any]]):
        self.config = config
        self.table_info = table_info
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"]
        )

    def build_schema_prompt(self) -> str:
        """构建数据库Schema提示文本"""
        schema_parts = []
        for table in self.table_info:
            schema_parts.append(f"表名: {table['table_name']} ({table.get('table_comment', '')})")
            for col in table["columns"]:
                col_desc = f"  - {col['name']} ({col['type']})"
                if col.get("comment"):
                    col_desc += f" - {col['comment']}"
                if col.get("key"):
                    col_desc += f" [KEY: {col['key']}]"
                schema_parts.append(col_desc)
            schema_parts.append("")  # 空行分隔
        return "\n".join(schema_parts)

    def generate_sql(self, natural_query: str) -> Optional[str]:
        """根据自然语言生成SQL语句"""
        schema_prompt = self.build_schema_prompt()

        system_prompt = f"""你是一个专业的SQL专家，请根据用户的自然语言查询生成对应的MySQL SQL语句。

数据库Schema信息：
{schema_prompt}

注意事项：
1. 只生成SELECT查询语句，不生成INSERT、UPDATE、DELETE等修改语句
2. 使用标准MySQL语法
3. 查询结果限制在1000条以内
4. 表名和字段名使用反引号包裹
5. 返回格式：仅返回SQL语句，不要包含其他解释文字
6. 确保SQL语句正确性，考虑字段类型和可能的NULL值
7. 对于聚合查询，使用合适的GROUP BY和HAVING子句
8. 按需求添加ORDER BY排序
9. 使用LIMIT限制结果数量"""

        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请生成SQL查询语句：{natural_query}"}
                ],
                temperature=self.config.get("temperature", 0.1),
                max_tokens=self.config.get("max_tokens", 2000)
            )
            sql = response.choices[0].message.content.strip()

            # 清理SQL语句（去除可能的markdown标记）
            sql = re.sub(r'```sql\n?', '', sql)
            sql = re.sub(r'\n?```$', '', sql)
            sql = sql.strip()

            # 验证SQL语句
            if not sql.upper().startswith("SELECT"):
                logger.warning("生成的SQL不是SELECT语句")
                return None

            logger.info(f"生成SQL: {sql}")
            return sql

        except Exception as e:
            logger.error(f"SQL生成失败: {str(e)}")
            return None

    def validate_sql(self, sql: str) -> bool:
        """验证SQL语句安全性"""
        # 禁止的关键字（修改数据或表结构的操作）
        forbidden_keywords = [
            "INSERT", "UPDATE", "DELETE", "DROP", "CREATE",
            "ALTER", "TRUNCATE", "GRANT", "REVOKE"
        ]
        sql_upper = sql.upper().strip()

        # 检查是否以禁止关键字开头
        for keyword in forbidden_keywords:
            if sql_upper.startswith(keyword):
                logger.warning(f"SQL包含禁止的关键字: {keyword}")
                return False

        # 检查危险的操作模式
        dangerous_patterns = [
            r"INTO\s+OUTFILE",
            r"INTO\s+DUMPFILE",
            r"LOAD_FILE",
            r"BENCHMARK",
            r"SLEEP"
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, sql_upper):
                logger.warning(f"SQL包含危险的操作模式: {pattern}")
                return False

        return True


# 全局实例（在main.py中初始化）
_sql_generator = None


def get_sql_generator() -> Optional[SQLGenerator]:
    """获取SQL生成器实例"""
    return _sql_generator


def init_sql_generator(config: Dict[str, Any], table_info: List[Dict[str, Any]]):
    """初始化SQL生成器"""
    global _sql_generator
    _sql_generator = SQLGenerator(config, table_info)
