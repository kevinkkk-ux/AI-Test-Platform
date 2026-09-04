# database.py
import mysql.connector
from mysql.connector import Error
import json
from config import DB_CONFIG


class DatabaseManager:
    """数据库管理类，封装所有数据库操作"""

    def __init__(self):
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        """连接数据库"""
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            if self.conn.is_connected():
                self.cursor = self.conn.cursor(dictionary=True)
                print("✅ 数据库连接成功")
        except Error as e:
            print(f"❌ 数据库连接失败：{e}")
            self.conn = None
            self.cursor = None

    def insert_test_case_main(self, case_type, group_num, case_title, case_content, generate_type=2):
        """插入用例主表，返回主表ID"""
        if not self.cursor:
            return None
        try:
            sql = """
                INSERT INTO test_case_main 
                (case_type, group_num, case_title, case_content, generate_type)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (case_type, group_num, case_title, str(case_content), generate_type))
            self.conn.commit()
            main_id = self.cursor.lastrowid
            print(f"✅ 主表插入成功，ID={main_id}")
            return main_id
        except Error as e:
            print(f"❌ 主表插入失败：{e}")
            self.conn.rollback()
            return None

    def batch_insert_case_detail(self, main_id, df_records):
        """批量插入用例明细表"""
        if not self.cursor or not main_id:
            return False
        try:
            sql = """
                INSERT INTO test_case_detail 
                (main_id, case_no, field_values, scene_desc, case_type, expected_result)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            batch_data = []
            for row in df_records:
                # 提取固定列
                case_no = row.get("用例ID", "")
                scene_desc = row.get("场景描述", "")
                case_type = row.get("用例类型", "")
                expected_result = row.get("预期结果", "")
                # 剩下的列都是字段值，存成JSON
                field_values = {}
                for k, v in row.items():
                    if k not in ["用例ID", "场景描述", "用例类型", "预期结果"]:
                        field_values[k] = v
                batch_data.append((
                    main_id, case_no,
                    json.dumps(field_values, ensure_ascii=False),
                    scene_desc, case_type, expected_result
                ))

            self.cursor.executemany(sql, batch_data)
            self.conn.commit()
            print(f"✅ 明细表批量插入成功，共{len(batch_data)}条")
            return True
        except Error as e:
            print(f"❌ 明细表插入失败：{e}")
            self.conn.rollback()
            return False

    def add_operation_log(self, user_id, operation_type, operation_desc, related_id=None):
        """添加操作日志"""
        if not self.cursor:
            return False
        try:
            sql = """
                INSERT INTO operation_log 
                (user_id, operation_type, operation_desc, related_id)
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(sql, (user_id, operation_type, operation_desc, related_id))
            self.conn.commit()
            return True
        except Error as e:
            print(f"❌ 日志插入失败：{e}")
            self.conn.rollback()
            return False

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("🔌 数据库连接已关闭")


# 全局单例
_db_manager = None

def get_db_manager():
    """获取数据库管理器单例"""
    global _db_manager
    if _db_manager is None or _db_manager.conn is None:
        _db_manager = DatabaseManager()
    return _db_manager
