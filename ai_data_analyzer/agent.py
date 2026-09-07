from typing import TypedDict, Optional, Dict, Any, List
from langgraph.graph import StateGraph, END
import logging
from config import LANGGRAPH_CONFIG
from database import DatabaseManager
from sql_generator import SQLGenerator

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    query: str
    sql: Optional[str]
    sql_valid: bool
    retry_count: int
    query_result: Optional[List[Dict]]
    analysis_result: Optional[str]
    visualization: Optional[str]
    report: Optional[str]
    error: Optional[str]

class DataAnalysisAgent:
    def __init__(self, db_manager, sql_generator, data_analyzer=None, visualizer=None, report_generator=None):
        self.db = db_manager
        self.sql_gen = sql_generator
        self.data_analyzer = data_analyzer
        self.visualizer = visualizer
        self.report_gen = report_generator
        self.max_retries = LANGGRAPH_CONFIG.get("max_iterations", 3)
        self.graph = self._build_graph()

    def generate_sql_node(self, state):
        logger.info("【节点1】生成SQL")
        try:
            sql = self.sql_gen.generate_sql(state["query"])
            if sql:
                state["sql"] = sql
                state["error"] = None
            else:
                state["error"] = "SQL生成失败"
        except Exception as e:
            state["error"] = f"SQL生成异常: {str(e)}"
        return state

    def validate_sql_node(self, state):
        logger.info("【节点2】验证SQL")
        sql = state.get("sql")
        if not sql:
            state["sql_valid"] = False
            state["error"] = state.get("error", "SQL为空")
            return state
        state["sql_valid"] = self.sql_gen.validate_sql(sql)
        if not state["sql_valid"]:
            state["error"] = "SQL包含危险操作，已被拦截"
        return state

    def route_after_validate(self, state):
        if state.get("sql_valid"):
            return "execute"
        retry_count = state.get("retry_count", 0)
        if retry_count < self.max_retries:
            state["retry_count"] = retry_count + 1
            return "retry"
        return "error"

    def execute_sql_node(self, state):
        logger.info("【节点3】执行SQL")
        sql = state.get("sql")
        if not sql:
            state["error"] = "SQL为空"
            return state
        try:
            success, result = self.db.execute_query(sql)
            if success:
                state["query_result"] = result
                state["error"] = None
            else:
                state["error"] = f"SQL执行失败: {result}"
        except Exception as e:
            state["error"] = f"SQL执行异常: {str(e)}"
        return state

    def route_after_execute(self, state):
        if state.get("query_result") is not None and state.get("error") is None:
            return "analyze"
        retry_count = state.get("retry_count", 0)
        if retry_count < self.max_retries:
            state["retry_count"] = retry_count + 1
            return "retry"
        return "error"

    def analyze_data_node(self, state):
        logger.info("【节点4】分析数据")
        query_result = state.get("query_result")
        if not query_result:
            state["analysis_result"] = "查询结果为空"
            return state
        if self.data_analyzer:
            try:
                state["analysis_result"] = self.data_analyzer.analyze(state["query"], query_result)
            except Exception as e:
                state["analysis_result"] = f"分析异常: {str(e)}"
        else:
            state["analysis_result"] = f"查询到{len(query_result)}条数据"
        return state

    def visualize_node(self, state):
        logger.info("【节点5】可视化")
        query_result = state.get("query_result")
        if not query_result:
            state["visualization"] = None
            return state
        if self.visualizer:
            try:
                state["visualization"] = self.visualizer.generate_chart(query_result)
            except Exception as e:
                logger.error(f"可视化异常: {str(e)}")
                state["visualization"] = None
        else:
            state["visualization"] = None
        return state

    def generate_report_node(self, state):
        logger.info("【节点6】生成报告")
        if self.report_gen:
            try:
                state["report"] = self.report_gen.generate(
                    query=state["query"],
                    sql=state.get("sql"),
                    query_result=state.get("query_result"),
                    analysis=state.get("analysis_result"),
                    visualization=state.get("visualization")
                )
            except Exception as e:
                state["report"] = f"报告生成异常: {str(e)}"
        else:
            state["report"] = f"# 分析报告\n\n## 查询问题\n{state['query']}\n\n## SQL\n```sql\n{state.get('sql', '无')}\n```\n\n## 分析\n{state.get('analysis_result', '无')}"
        return state

    def handle_error_node(self, state):
        logger.info("【节点7】错误处理")
        error = state.get("error", "未知错误")
        retry_count = state.get("retry_count", 0)
        state["report"] = f"# ⚠️ 查询失败\n\n## 错误信息\n{error}\n\n## 重试次数\n已重试{retry_count}次，超过最大限制{self.max_retries}次。\n\n## 建议\n1. 检查查询问题是否清晰\n2. 换一种说法重新提问\n3. 确认数据库中有相关数据"
        return state

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("generate_sql", self.generate_sql_node)
        workflow.add_node("validate_sql", self.validate_sql_node)
        workflow.add_node("execute_sql", self.execute_sql_node)
        workflow.add_node("analyze_data", self.analyze_data_node)
        workflow.add_node("visualize", self.visualize_node)
        workflow.add_node("generate_report", self.generate_report_node)
        workflow.add_node("handle_error", self.handle_error_node)
        workflow.set_entry_point("generate_sql")
        workflow.add_edge("generate_sql", "validate_sql")
        workflow.add_conditional_edges("validate_sql", self.route_after_validate, {
            "execute": "execute_sql", "retry": "generate_sql", "error": "handle_error"
        })
        workflow.add_conditional_edges("execute_sql", self.route_after_execute, {
            "analyze": "analyze_data", "retry": "generate_sql", "error": "handle_error"
        })
        workflow.add_edge("analyze_data", "visualize")
        workflow.add_edge("visualize", "generate_report")
        workflow.add_edge("generate_report", END)
        workflow.add_edge("handle_error", END)
        return workflow.compile()

    def run(self, query: str) -> Dict[str, Any]:
        logger.info(f"开始处理查询: {query}")
        initial_state = {
            "query": query, "sql": None, "sql_valid": False,
            "retry_count": 0, "query_result": None, "analysis_result": None,
            "visualization": None, "report": None, "error": None
        }
        result = self.graph.invoke(initial_state)
        logger.info("查询处理完成")
        return {
            "query": result.get("query"), "sql": result.get("sql"),
            "query_result": result.get("query_result"), "analysis": result.get("analysis_result"),
            "visualization": result.get("visualization"), "report": result.get("report"),
            "error": result.get("error")
        }
