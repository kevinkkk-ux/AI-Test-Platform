# rag_store.py
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions
import logging
import uuid
from config import PATH_CONFIG

logger = logging.getLogger(__name__)


class TestCaseRAG:
    def __init__(self):
        # 初始化嵌入函数（将文本转为向量）
        self.embed_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=PATH_CONFIG["embed_model_path"]
        )
        # 初始化ChromaDB客户端（持久化存储）
        self.client = chromadb.PersistentClient(path=PATH_CONFIG["chroma_db_root"])
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="test_case_knowledge",
            embedding_function=self.embed_func
        )

    def add_test_case_batch(self, case_list: List[Dict]) -> int:
        """
        批量添加测试用例到向量库
        :param case_list: 测试用例字典列表
        :return: 添加的用例数量
        """
        docs, metas, ids = [], [], []
        gen_type_map = {'1': 'AI生成', '2': 'RAG生成', '3': '手动录入', '4': '接口导入'}
        for case in case_list:
            cid = case.get("case_id") or f"null_{uuid.uuid4().hex[:8]}"
            # 构建文档文本
            text = f"用例ID: {case.get('case_id', '无')}\n" \
                   f"标题: {case.get('case_title', '无')}\n" \
                   f"描述: {case.get('case_content', '无')}\n" \
                   f"生成类型: {gen_type_map.get(str(case.get('case_generate_type', '')), '未知')}\n" \
                   f"用例类型: {case.get('case_type', '未分类')}"
            docs.append(text)
            metas.append({
                "case_id": str(case.get("case_id")),
                "title": case.get("case_title"),
                "case_type": case.get("case_type")
            })
            ids.append(f"case_{cid}")
        if docs:
            self.collection.add(documents=docs, metadatas=metas, ids=ids)
        return len(docs)

    def retrieve(self, query: str, top_k: int = 3) -> str:
        """
        根据查询文本检索最相似的测试用例
        :param query: 查询文本
        :param top_k: 返回结果数量
        :return: 检索到的文档文本
        """
        res = self.collection.query(query_texts=[query], n_results=top_k)
        docs = res.get("documents", [[]])
        if not docs:
            return "未找到相关历史用例"
        return "\n".join([f"【参考用例 {i + 1}】\n{d}" for i, d in enumerate(docs)])

    def count(self) -> int:
        """返回向量库中的用例总数"""
        return self.collection.count()


# 全局单例
rag_case_store = TestCaseRAG()
# main.py 第54-60行（init_system函数）
def init_system():
    global analysis_agent
    db = get_db_manager()
    if not db.connect():
        raise Exception("MySQL连接失败")
    sql_gen = SQLGenerator()
    analyzer = DataAnalyzer()
    analysis_agent = DataAnalysisAgent(sql_gen, db, analyzer, visualizer, report_generator)
    # 同步历史用例到向量库
    ok, cases = db.execute_query(
        "SELECT t.*, COALESCE(u.nickname, u.username) as user_name FROM test_case t "
        "LEFT JOIN sys_user u ON t.user_id = u.user_id WHERE t.case_is_deleted=0"
    )
    if ok and cases:
        cnt = rag_case_store.add_test_case_batch(cases)
        logger.info(f"同步{cnt}条历史用例至向量库")