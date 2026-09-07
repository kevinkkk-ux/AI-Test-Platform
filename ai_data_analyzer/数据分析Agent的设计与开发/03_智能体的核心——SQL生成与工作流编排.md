## Ch03 智能体的核心——SQL生成与工作流编排

上一章我们学习了项目的基础架构，包括配置文件（`config.py`）和数据库连接模块（`database.py`）。接下来，我们将进入整个系统的核心部分，探索两个至关重要的模块：**SQL生成器（sql_generator.py）** 和 **LangGraph智能体（agent.py）**。

如果把整个系统比作一个智能的数据分析师，那么：

- **sql_generator.py** 就是这位分析师的“翻译官”，它负责将用户的自然语言**“翻译”**成数据库能够理解的 SQL 查询语句。
- **agent.py** 就是这位分析师的“大脑”，它负责编排整个工作流程，指挥各个模块（包括翻译官）协同工作，最终完成数据分析任务。

让我们先来认识这位“翻译官”。

### 1. SQL生成器 (sql_generator.py)

这个模块的核心职能是：**根据用户输入的自然语言查询，结合数据库的结构信息，调用大语言模型（DeepSeek）生成对应的 SQL 语句**。

```python
from typing import Dict, Any, List, Optional
import json
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
    # ... (后续方法)
```

**关键要点：**

1. **类的初始化：`__init__ `方法**

   - SQLGenerator在初始化时接收两个参数：config（来自 DEEPSEEK_CONFIG）和 table_info（来自 DatabaseManager.get_table_info() 的返回结果）。
   - `self.client = OpenAI(...)`：这里创建了一个 `OpenAI` 客户端实例。注意，虽然类名是 `OpenAI`，但通过设置 `base_url` 为 `"https://api.deepseek.com/v1"`，我们实际上是在调用 DeepSeek 的 API。这体现了 `openai` 库的兼容性设计——它支持任何与 OpenAI API 格式兼容的服务。
   - self.table_info保存了数据库的表结构信息。这个信息将在后续的提示词构建中发挥关键作用。

2. **构建数据库Schema提示：build_schema_prompt() 方法**

   ```python
   def build_schema_prompt(self) -> str:
       """构建数据库Schema提示"""
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
   ```

   - 这个方法的作用是**将结构化的表信息，格式化为一段大模型易于理解的文本**。

   - 它遍历每一个表，对于每个表，先输出表名和表注释，然后遍历该表的每一列，输出列名、类型、注释和主键/索引信息。

   - 最终生成的字符串类似于： 

     ```
     表名: users (用户表)
       - id (INT) - 用户ID [KEY: PRI]
       - name (VARCHAR(100)) - 用户名
       - level (VARCHAR(20)) - 会员等级
     
     表名: orders (订单表)
       - order_id (INT) - 订单ID [KEY: PRI]
       - user_id (INT) - 用户ID
       - total_amount (DECIMAL(10,2)) - 订单金额
     ```

   - 这段文本将成为给大模型提示词的核心部分，帮助大模型“理解”数据库的结构。

3. **核心功能：生成SQL语句——generate_sql() 方法**

   ```python
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
   ```

   - **这是整个模块最核心的方法**。它接收用户的自然语言查询（`natural_query`）作为输入，并返回一个SQL语句（或 `None`）。
   - 提示词工程：system_prompt 是给大模型的“系统指令”，包含了数据库Schema信息和一系列注意事项。这些注意事项非常重要，它们限制了SQL的类型（只读）、语法（MySQL）、安全性（限制返回条数）等。这是典型的“提示词工程（Prompt Engineering）”实践。
   - 调用大模型：通过 self.client.chat.completions.create() 调用 DeepSeek API。messages 参数包含了两条消息：一条是系统指令（system），一条是用户请求（user）。
   - 后续处理：获取到大模型返回的文本后，代码通过正则表达式 re.sub(r'^sql\n?', '', sql) 清理掉可能存在的 Markdown 代码块标记（如sql），并验证生成的SQL是否以 SELECT 开头。

4. **安全验证：validate_sql() 方法**

   ```python
   def validate_sql(self, sql: str) -> bool:
       """验证SQL语句安全性"""
       forbidden_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE",
                             "ALTER", "TRUNCATE", "GRANT", "REVOKE"]
       sql_upper = sql.upper().strip()
       for keyword in forbidden_keywords:
           if sql_upper.startswith(keyword):
               return False
   
       dangerous_patterns = [
           r"INTO\s+OUTFILE",
           r"INTO\s+DUMPFILE",
           r"LOAD_FILE",
           r"BENCHMARK",
           r"SLEEP"
       ]
       for pattern in dangerous_patterns:
           if re.search(pattern, sql_upper):
               return False
       return True
   ```

   - 这是一个**安全阀门**。即使大模型不按指令行事，生成了危险的SQL语句（如 `DROP TABLE`），这个验证方法也能将其拦截。
   - 它检查SQL是否以禁止的关键字开头，并搜索危险的操作模式（如 INTO OUTFILE、LOAD_FILE 等）。只有通过验证的SQL才会被允许执行。
   - **为什么需要双重保障？** 因为大模型并非100%可靠，有时可能会出现“幻觉”或理解偏差。这个验证方法为系统增加了一层重要的安全防护。

**小结**：`sql_generator.py` 模块通过巧妙的提示词工程，将大模型的能力与数据库结构信息结合起来，实现了一个“自然语言到SQL”的翻译器。同时，它通过安全验证机制，确保了生成的SQL语句的安全性。

### 2. LangGraph智能体 (agent.py)

现在，我们来认识整个系统的“大脑”——`agent.py`。这个模块利用 LangGraph 框架，定义了一个**状态图（StateGraph）**，用以编排从“用户输入”到“最终报告”的完整工作流程。

```python
from typing import TypedDict, Annotated, Sequence, Dict, Any, List, Optional
from langgraph.graph import StateGraph
import json
import logging

logger = logging.getLogger(__name__)

# 定义状态类型
class AgentState(TypedDict):
    """智能体状态"""
    user_query: str
    sql: Optional[str]
    sql_valid: bool
    query_result: Optional[List[Dict[str, Any]]]
    analysis_result: Optional[Dict[str, Any]]
    chart_html: Optional[str]
    report: Optional[str]
    error: Optional[str]
    chart_type: str
    x_column: Optional[str]
    y_column: Optional[str]
    iterations: int
    max_iterations: int
```

**关键要点：**

1. **状态定义：AgentState**

   - 在 LangGraph 中，**状态（State）** 是贯穿整个工作流的核心数据。它记录了工作流在每一步执行后的结果。
   - AgentState继承自 TypedDict，相当于一个强类型的字典。它定义了所有可能在流程中产生或使用的数据字段，例如： 
     - `user_query`: 用户的原始输入。
     - `sql`: 生成的SQL语句。
     - `sql_valid`: SQL是否通过验证。
     - `query_result`: 数据库查询返回的结果。
     - `chart_html`: 生成的图表HTML代码。
     - `report`: 最终的分析报告。
     - `error`: 如果流程出错，记录错误信息。
     - `iterations` 和 `max_iterations`: 用于控制重试次数。

2. **智能体类：DataAnalysisAgent**

   ```python
   class DataAnalysisAgent:
       """数据分析智能体"""
       def __init__(self,
                    sql_generator: 'SQLGenerator',
                    db_manager: 'DatabaseManager',
                    analyzer: 'DataAnalyzer',
                    visualizer: 'DataVisualizer',
                    report_generator: 'ReportGenerator'):
           self.sql_generator = sql_generator
           self.db_manager = db_manager
           self.analyzer = analyzer
           self.visualizer = visualizer
           self.report_generator = report_generator
           # 构建图
           self.graph = self._build_graph()
   ```

   - DataAnalysisAgent 在初始化时，接收了其他所有模块的实例作为依赖。这体现了依赖注入的设计思想，使得智能体本身不负责创建这些模块，而是由外部创建好之后传入，提高了代码的灵活性和可测试性。
   - 在` __init__`的最后，它调用了 self._build_graph() 方法来构建工作流图。

3. **构建工作流图：_build_graph() 方法**

   ```python
       def _build_graph(self) -> StateGraph:
           """构建LangGraph图"""
   
           # 创建状态图
           workflow = StateGraph(AgentState)
   
           # 添加节点
           workflow.add_node("generate_sql", self._generate_sql_node)
           workflow.add_node("validate_sql", self._validate_sql_node)
           workflow.add_node("execute_sql", self._execute_sql_node)
           workflow.add_node("analyze_data", self._analyze_data_node)
           workflow.add_node("visualize_data", self._visualize_data_node)
           workflow.add_node("generate_report", self._generate_report_node)
           workflow.add_node("handle_error", self._handle_error_node)
   
           # 设置入口点
           workflow.set_entry_point("generate_sql")
   
           # 添加边
           workflow.add_edge("generate_sql", "validate_sql")
   
           # 条件边
           workflow.add_conditional_edges(
               "validate_sql",
               self._decide_next_step,
               {
                   "valid": "execute_sql",
                   "invalid": "handle_error",
                   "retry": "generate_sql"
               }
           )
   
           workflow.add_conditional_edges(
               "execute_sql",
               self._decide_execution_result,
               {
                   "success": "analyze_data",
                   "error": "handle_error"
               }
           )
   
           workflow.add_edge("analyze_data", "visualize_data")
           workflow.add_edge("visualize_data", "generate_report")
           workflow.add_edge("generate_report", "handle_error")  # 结束节点
   
           # 编译图
           app = workflow.compile()
           return app
   ```

   - **这是整个模块最核心的方法**。它使用 LangGraph 的 `StateGraph` 来构建一个**有向图**。
   - 节点（Node）：图中的每个圆形节点代表一个工作步骤，例如 generate_sql（生成SQL）、execute_sql（执行SQL）、analyze_data（分析数据）等。每个节点都绑定了一个处理函数（如self._generate_sql_node ）。
   - 边（Edge）：图中的箭头代表流程的走向。add_edge 添加的是无条件转移的边，例如“生成SQL”之后总是“验证SQL”。
   - 条件边（Conditional Edge）：add_conditional_edges 添加的是有条件的转移。例如，在“验证SQL”节点之后，流程不是固定的，而是根据 _decide_next_step 函数的返回值来决定下一步： 
     - 如果返回 "valid"（有效），则进入 execute_sql 节点。
     - 如果返回 `"invalid"`（无效），则进入 `handle_error` 节点。
     - 如果返回 `"retry"`（重试），则回到 `generate_sql` 节点，重新生成SQL。这为系统提供了**自我纠错**的能力。
   - **编译图**：`workflow.compile()` 将定义好的图结构编译成一个可执行的应用。

4. **节点(Node)函数**

   ```python
       def _generate_sql_node(self, state: AgentState) -> Dict[str, Any]:
           """生成SQL节点"""
           logger.info("生成SQL语句...")
           try:
               sql = self.sql_generator.generate_sql(state["user_query"])
               return {
                   "sql": sql,
                   "sql_valid": sql is not None,
                   "iterations": state.get("iterations", 0) + 1
               }
           except Exception as e:
               logger.error(f"SQL生成失败: {str(e)}")
               return {"error": str(e), "sql_valid": False}
   
       def _validate_sql_node(self, state: AgentState) -> Dict[str, Any]:
           """验证SQL节点"""
           logger.info("验证SQL语句...")
           if state.get("sql"):
               is_valid = self.sql_generator.validate_sql(state["sql"])
               return {"sql_valid": is_valid}
           return {"sql_valid": False}
   
       def _decide_next_step(self, state: AgentState) -> str:
           """决定下一步"""
           if state.get("sql_valid"):
               return "valid"
           elif state.get("iterations", 0) < state.get("max_iterations", 3):
               return "retry"
           else:
               return "invalid"
   
       def _execute_sql_node(self, state: AgentState) -> Dict[str, Any]:
           """执行SQL节点"""
           logger.info("执行SQL查询...")
           try:
               success, result = self.db_manager.execute_query(state["sql"])
               if success:
                   return {"query_result": result}
               else:
                   return {"error": str(result)}
           except Exception as e:
               logger.error(f"SQL执行失败: {str(e)}")
               return {"error": str(e)}
   
       def _decide_execution_result(self, state: AgentState) -> str:
           """决定执行结果"""
           if state.get("query_result") is not None:
               return "success"
           return "error"
   
       def _analyze_data_node(self, state: AgentState) -> Dict[str, Any]:
           """分析数据节点"""
           logger.info("分析数据...")
           try:
               analysis_result = self.analyzer.analyze_data(
                   state["query_result"],
                   state["user_query"],
                   state["sql"]
               )
               return {"analysis_result": analysis_result}
           except Exception as e:
               logger.error(f"数据分析失败: {str(e)}")
               return {"error": str(e)}
   
       def _visualize_data_node(self, state: AgentState) -> Dict[str, Any]:
           """可视化数据节点"""
           logger.info("生成可视化图表...")
           try:
               chart_html = self.visualizer.create_visualization(
                   state["query_result"],
                   state.get("chart_type", "柱状图"),
                   state.get("x_column"),
                   state.get("y_column")
               )
               return {"chart_html": chart_html}
           except Exception as e:
               logger.error(f"可视化失败: {str(e)}")
               return {"error": str(e)}
   
       def _generate_report_node(self, state: AgentState) -> Dict[str, Any]:
           """生成报告节点"""
           logger.info("生成分析报告...")
           try:
               report = self.report_generator.generate_report(
                   state["analysis_result"],
                   state["user_query"],
                   state["sql"],
                   state.get("chart_html")
               )
               return {"report": report}
           except Exception as e:
               logger.error(f"报告生成失败: {str(e)}")
               return {"error": str(e)}
   
       def _handle_error_node(self, state: AgentState) -> Dict[str, Any]:
           """错误处理节点"""
           logger.error(f"流程出错: {state.get('error', '未知错误')}")
           return state
   ```

   - _generate_sql_node：这个节点函数接收当前状态（AgentState），从中取出 user_query，调用 self.sql_generator.generate_sql() 生成SQL。然后，它返回一个字典，这个字典的内容会被合并（merge）到当前状态中，更新 sql、sql_valid 和 iterations 字段。
   - _decide_next_step：这个函数不是节点函数，而是路由函数。它接收当前状态，根据 sql_valid 和iterations  的值，决定下一步应该走向哪个节点。这实现了流程的分支和循环。

5. **运行智能体：run() 方法**

   ```python
       def run(self,
               user_query: str,
               chart_type: str = "柱状图",
               x_column: Optional[str] = None,
               y_column: Optional[str] = None) -> Dict[str, Any]:
           """运行智能体"""
   
           initial_state = AgentState(
               user_query=user_query,
               sql=None,
               sql_valid=False,
               query_result=None,
               analysis_result=None,
               chart_html=None,
               report=None,
               error=None,
               chart_type=chart_type,
               x_column=x_column,
               y_column=y_column,
               iterations=0,
               max_iterations=3
           )
   
           # 执行图
           result = self.graph.invoke(initial_state)
   
           return {
               "success": result.get("report") is not None,
               "report": result.get("report"),
               "chart_html": result.get("chart_html"),
               "sql": result.get("sql"),
               "error": result.get("error")
           }
   ```

   - run() 方法是智能体的入口。它接收用户的查询和一些可选参数（如图表类型），然后创建一个初始状态 initial_state。
   - 接着，它调用 self.graph.invoke(initial_state)，将初始状态注入到工作流图中，启动整个流程的执行。
   - 最后，它从最终状态中提取出 report、chart_html 等关键结果，并返回给调用者。

**小结**：`agent.py` 模块通过 LangGraph 框架，将复杂的多步骤数据分析流程，抽象成了一个清晰的状态图。它明确了每一步的职责（节点）、流程的走向（边和条件边），以及如何在各步骤之间传递数据（状态）。这种设计使得整个流程变得**可控、可观察、可重试**，极大地提高了系统的健壮性。

### 本章总结：

在这一章中，我们深入学习了两个核心模块：

- **sql_generator.py（翻译官）**：它利用大模型的能力，结合数据库结构信息，将自然语言“翻译”成安全的SQL语句。其核心在于**提示词工程**和**安全验证**。
- **agent.py（大脑）**：它利用 LangGraph 框架，构建了一个**状态图**来编排整个工作流程。其核心在于**状态管理**、**节点定义**和**条件路由**。

这两个模块共同构成了系统的“决策与执行”核心。下一章，我们将学习如何分析数据、生成图表，并最终将这些结果整合成一份完整的分析报告。