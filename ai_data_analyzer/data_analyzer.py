# data_analyzer.py
from typing import Dict, Any, List, Optional
import pandas as pd
from openai import OpenAI
import logging
import json

logger = logging.getLogger(__name__)


class DataAnalyzer:
    """数据分析师：统计分析 + AI洞察"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"]
        )

    def _basic_stats(self, df: pd.DataFrame) -> str:
        """生成基础统计描述"""
        stats_parts = []
        stats_parts.append(f"数据总行数：{len(df)}")
        stats_parts.append(f"数据列数：{len(df.columns)}")
        stats_parts.append(f"列名：{', '.join(df.columns.tolist())}")

        # 数值列统计
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            stats_parts.append("\n数值列统计：")
            for col in numeric_cols:
                stats_parts.append(f"  - {col}: 均值={df[col].mean():.2f}, 最大={df[col].max()}, 最小={df[col].min()}, 总和={df[col].sum()}")

        # 分类列统计
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            stats_parts.append("\n分类列统计：")
            for col in categorical_cols:
                unique_count = df[col].nunique()
                stats_parts.append(f"  - {col}: {unique_count}个不同值")
                if unique_count <= 10:
                    value_counts = df[col].value_counts().to_dict()
                    for v, c in value_counts.items():
                        stats_parts.append(f"      {v}: {c}条")

        return "\n".join(stats_parts)

    def _ai_insight(self, query: str, df: pd.DataFrame, basic_stats: str) -> str:
        """调用大模型生成AI洞察"""
        # 限制数据量，避免token过多
        sample_data = df.head(20).to_dict('records')
        sample_json = json.dumps(sample_data, ensure_ascii=False, default=str)

        system_prompt = f"""你是一个专业的数据分析师，请根据用户的查询和查询结果，生成专业的数据分析洞察。

要求：
1. 分析数据的趋势、分布、异常点
2. 给出有价值的业务洞察和建议
3. 语言简洁专业，分点论述
4. 不要重复基础统计数据，重点在洞察和建议
5. 输出格式：Markdown，包含"核心发现"、"关键洞察"、"业务建议"三个部分"""

        user_prompt = f"""用户查询：{query}

基础统计：
{basic_stats}

数据样本（前20条）：
{sample_json}

请生成数据分析洞察。"""

        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.get("temperature", 0.3),
                max_tokens=self.config.get("max_tokens", 2000)
            )
            insight = response.choices[0].message.content.strip()
            logger.info("AI洞察生成完成")
            return insight
        except Exception as e:
            logger.error(f"AI洞察生成失败: {str(e)}")
            return f"AI洞察生成失败: {str(e)}"

    def analyze(self, query: str, query_result: List[Dict[str, Any]]) -> str:
        """
        主分析方法：基础统计 + AI洞察
        :param query: 用户自然语言查询
        :param query_result: SQL查询结果（字典列表）
        :return: 分析结果（Markdown格式）
        """
        if not query_result:
            return "查询结果为空，无数据可分析"

        # 转换为DataFrame
        df = pd.DataFrame(query_result)

        # 1. 基础统计
        basic_stats = self._basic_stats(df)

        # 2. AI洞察
        ai_insight = self._ai_insight(query, df, basic_stats)

        # 3. 整合结果
        result = f"""## 数据统计
{basic_stats}

---

{ai_insight}
"""

        return result


# 全局实例
_data_analyzer = None


def get_data_analyzer() -> Optional[DataAnalyzer]:
    return _data_analyzer


def init_data_analyzer(config: Dict[str, Any]):
    global _data_analyzer
    _data_analyzer = DataAnalyzer(config)
