# visualizer.py
from typing import Dict, Any, List, Optional
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 不显示窗口，只生成图片
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

# 设置中文字体（Windows下用微软雅黑）
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class Visualizer:
    """可视化生成器：根据数据自动选择图表类型"""

    def __init__(self):
        pass

    def _fig_to_base64(self, fig) -> str:
        """将matplotlib图表转换为base64编码字符串"""
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_base64

    def _auto_select_chart_type(self, df: pd.DataFrame) -> str:
        """根据数据自动选择图表类型"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        # 只有1个分类列 + 1个数值列 → 饼图或柱状图
        if len(categorical_cols) == 1 and len(numeric_cols) == 1:
            unique_count = df[categorical_cols[0]].nunique()
            if unique_count <= 6:
                return 'pie'  # 分类少用饼图
            else:
                return 'bar'  # 分类多用柱状图

        # 有2个数值列 → 散点图
        if len(numeric_cols) >= 2:
            return 'scatter'

        # 有1个分类列 + 多个数值列 → 柱状图
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            return 'bar'

        # 默认柱状图
        return 'bar'

    def _pie_chart(self, df: pd.DataFrame) -> str:
        """生成饼图"""
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not categorical_cols or not numeric_cols:
            return self._bar_chart(df)

        labels = df[categorical_cols[0]].tolist()
        values = df[numeric_cols[0]].tolist()

        fig, ax = plt.subplots(figsize=(8, 6))
        colors = plt.cm.Set3(range(len(labels)))
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct='%1.1f%%',
            colors=colors, startangle=90
        )
        ax.set_title(f'{categorical_cols[0]} 占比分布', fontsize=14, fontweight='bold')
        plt.setp(autotexts, size=10, weight='bold')

        return self._fig_to_base64(fig)

    def _bar_chart(self, df: pd.DataFrame) -> str:
        """生成柱状图"""
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not categorical_cols or not numeric_cols:
            # 没有分类列，直接画数值列
            fig, ax = plt.subplots(figsize=(10, 6))
            for col in numeric_cols:
                ax.bar(range(len(df)), df[col], label=col, alpha=0.7)
            ax.set_xlabel('序号')
            ax.set_ylabel('数值')
            ax.set_title('数据柱状图', fontsize=14, fontweight='bold')
            ax.legend()
            return self._fig_to_base64(fig)

        x_col = categorical_cols[0]
        y_col = numeric_cols[0]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(range(len(df)), df[y_col], color='steelblue', alpha=0.8)
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df[x_col].tolist(), rotation=45, ha='right')
        ax.set_xlabel(x_col, fontsize=12)
        ax.set_ylabel(y_col, fontsize=12)
        ax.set_title(f'{x_col} vs {y_col}', fontsize=14, fontweight='bold')

        # 在柱子上显示数值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}' if height == int(height) else f'{height:.1f}',
                    ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def _line_chart(self, df: pd.DataFrame) -> str:
        """生成折线图"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        fig, ax = plt.subplots(figsize=(10, 6))

        if categorical_cols:
            x_labels = df[categorical_cols[0]].tolist()
            x = range(len(df))
            ax.set_xticks(x)
            ax.set_xticklabels(x_labels, rotation=45, ha='right')
            ax.set_xlabel(categorical_cols[0], fontsize=12)
        else:
            x = range(len(df))
            ax.set_xlabel('序号', fontsize=12)

        for col in numeric_cols:
            ax.plot(x, df[col], marker='o', linewidth=2, markersize=6, label=col)

        ax.set_ylabel('数值', fontsize=12)
        ax.set_title('数据趋势折线图', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return self._fig_to_base64(fig)

    def _scatter_chart(self, df: pd.DataFrame) -> str:
        """生成散点图"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if len(numeric_cols) < 2:
            return self._bar_chart(df)

        x_col = numeric_cols[0]
        y_col = numeric_cols[1]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(df[x_col], df[y_col], s=80, c='steelblue', alpha=0.7, edgecolors='white')
        ax.set_xlabel(x_col, fontsize=12)
        ax.set_ylabel(y_col, fontsize=12)
        ax.set_title(f'{x_col} vs {y_col} 散点图', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return self._fig_to_base64(fig)

    def generate_chart(self, query_result: List[Dict[str, Any]], chart_type: str = 'auto') -> Optional[str]:
        """
        生成可视化图表
        :param query_result: SQL查询结果
        :param chart_type: 图表类型，auto/pie/bar/line/scatter
        :return: base64编码的图片
        """
        if not query_result:
            logger.warning("查询结果为空，无法生成图表")
            return None

        df = pd.DataFrame(query_result)

        if len(df) == 0:
            logger.warning("DataFrame为空，无法生成图表")
            return None

        try:
            # 自动选择图表类型
            if chart_type == 'auto':
                chart_type = self._auto_select_chart_type(df)

            logger.info(f"生成图表类型: {chart_type}")

            if chart_type == 'pie':
                return self._pie_chart(df)
            elif chart_type == 'bar':
                return self._bar_chart(df)
            elif chart_type == 'line':
                return self._line_chart(df)
            elif chart_type == 'scatter':
                return self._scatter_chart(df)
            else:
                logger.warning(f"未知图表类型: {chart_type}，使用柱状图")
                return self._bar_chart(df)

        except Exception as e:
            logger.error(f"图表生成失败: {str(e)}")
            return None


# 全局实例
_visualizer = None


def get_visualizer() -> Optional[Visualizer]:
    return _visualizer


def init_visualizer():
    global _visualizer
    _visualizer = Visualizer()
