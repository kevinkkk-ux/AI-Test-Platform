# database.py
import pymysql
from typing import List, Tuple, Optional, Any, Dict
import pandas as pd
from contextlib import contextmanager
import logging
from config import DB_CONFIG

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None

    def connect(self) -> bool:
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config["database"],
                charset=self.config["charset"],
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            return False

    def disconnect(self):
        """断开数据库连接"""
        if self.connection and self.connection.open:
            self.connection.close()
            logger.info("数据库连接已关闭")

    @contextmanager
    def get_cursor(self):
        """获取数据库游标（上下文管理器）"""
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def execute_query(self, sql: str) -> Tuple[bool, Any]:
        """执行SQL查询"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(sql)
                if sql.strip().upper().startswith("SELECT"):
                    result = cursor.fetchall()
                    return True, result
                else:
                    self.connection.commit()
                    return True, {"affected_rows": cursor.rowcount}
        except Exception as e:
            logger.error(f"SQL执行失败: {str(e)}")
            return False, str(e)

    def get_table_info(self) -> List[Dict[str, Any]]:
        """获取数据库所有表的结构信息"""
        try:
            with self.get_cursor() as cursor:
                # 获取所有表
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()

                table_info = []
                for table in tables:
                    table_name = list(table.values())[0]

                    # 获取表字段
                    cursor.execute(f"DESCRIBE `{table_name}`")
                    columns = cursor.fetchall()

                    # 获取表注释
                    cursor.execute(f"""
                        SELECT TABLE_COMMENT 
                        FROM information_schema.TABLES 
                        WHERE TABLE_SCHEMA = '{self.config["database"]}' 
                        AND TABLE_NAME = '{table_name}'
                    """)
                    table_comment_row = cursor.fetchone()
                    comment = table_comment_row.get("TABLE_COMMENT", "") if table_comment_row else ""

                    table_info.append({
                        "table_name": table_name,
                        "table_comment": comment,
                        "columns": [
                            {
                                "name": col.get("Field", ""),
                                "type": col.get("Type", ""),
                                "comment": col.get("Comment", ""),
                                "key": col.get("Key", "")
                            }
                            for col in columns
                        ]
                    })
                return table_info
        except Exception as e:
            logger.error(f"获取表结构失败: {str(e)}")
            return []

    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """获取某个表的前几条示例数据"""
        try:
            sql = f"SELECT * FROM `{table_name}` LIMIT {limit}"
            success, result = self.execute_query(sql)
            if success:
                return result
            return []
        except Exception as e:
            logger.error(f"获取示例数据失败: {str(e)}")
            return []


# 单例模式
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """获取数据库管理器单例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(DB_CONFIG)
    return _db_manager
