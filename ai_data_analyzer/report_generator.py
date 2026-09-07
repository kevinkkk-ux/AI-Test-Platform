# report_generator.py
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器：整合所有信息，生成完整的分析报告"""

    def __init__(self):
        pass

    def _format_query_result(self, query_result: List[Dict], max_rows: int = 20) -> str:
        """格式化查询结果为Markdown表格"""
        if not query_result:
            return "无数据"

        # 限制显示行数
        display_data = query_result[:max_rows]
        if len(query_result) > max_rows:
            display_data.append({k: "..." for k in query_result[0].keys()})

        # 获取列名
        columns = list(query_result[0].keys())

        # 生成Markdown表格
        md_lines = []
        md_lines.append("| " + " | ".join(columns) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(columns)) + " |")

        for row in display_data:
            values = [str(row.get(col, "")) for col in columns]
            md_lines.append("| " + " | ".join(values) + " |")

        if len(query_result) > max_rows:
            md_lines.append(f"\n*共 {len(query_result)} 条数据，仅显示前 {max_rows} 条*")

        return "\n".join(md_lines)

    def generate(
        self,
        query: str,
        sql: Optional[str] = None,
        query_result: Optional[List[Dict]] = None,
        analysis: Optional[str] = None,
        visualization: Optional[str] = None
    ) -> str:
        """
        生成完整的分析报告（Markdown格式）
        :param query: 用户自然语言查询
        :param sql: 生成的SQL语句
        :param query_result: SQL查询结果
        :param analysis: 数据分析结果
        :param visualization: 可视化图表（base64编码）
        :return: Markdown格式的完整报告
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report_parts = []

        # 1. 标题
        report_parts.append(f"# 📊 数据分析报告")
        report_parts.append(f"\n> 生成时间：{now}")
        report_parts.append(f"\n---\n")

        # 2. 查询信息
        report_parts.append(f"## 🔍 查询信息")
        report_parts.append(f"\n**用户查询**：{query}")
        if sql:
            report_parts.append(f"\n**生成的SQL**：")
            report_parts.append(f"```sql\n{sql}\n```")
        report_parts.append(f"\n---\n")

        # 3. 数据摘要
        report_parts.append(f"## 📋 数据摘要")
        if query_result:
            report_parts.append(f"\n查询到 **{len(query_result)}** 条数据")
            report_parts.append(f"\n### 数据明细")
            report_parts.append(f"\n{self._format_query_result(query_result)}")
        else:
            report_parts.append(f"\n无查询结果")
        report_parts.append(f"\n---\n")

        # 4. 可视化图表
        if visualization:
            report_parts.append(f"## 📈 可视化图表")
            report_parts.append(f"\n![可视化图表](data:image/png;base64,{visualization})")
            report_parts.append(f"\n---\n")

        # 5. 数据分析与洞察
        if analysis:
            report_parts.append(f"## 🧠 数据分析与洞察")
            report_parts.append(f"\n{analysis}")
            report_parts.append(f"\n---\n")

        # 6. 报告结尾
        report_parts.append(f"## 📝 报告说明")
        report_parts.append(f"""\n- 本报告由AI数据分析智能体自动生成
- 数据来源：电商系统后台数据库（analysis_db）
- 分析方法：统计分析 + AI大模型洞察
- 仅供参考，具体业务决策请结合实际情况""")

        report = "\n".join(report_parts)
        logger.info("分析报告生成完成")
        return report

    def generate_html(
        self,
        query: str,
        sql: Optional[str] = None,
        query_result: Optional[List[Dict]] = None,
        analysis: Optional[str] = None,
        visualization: Optional[str] = None
    ) -> str:
        """
        生成HTML格式的报告（用于Gradio界面展示）
        """
        markdown_report = self.generate(query, sql, query_result, analysis, visualization)

        # 简单的Markdown转HTML（基础转换，够用）
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据分析报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #2980b9; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 10px; }}
        h3 {{ color: #16a085; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; background: white; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        code {{ background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
                pre {{
            background-color: #f6f8fa;
            color: #24292f;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid #d0d7de;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
        }}
        pre code {{
            background: none;
            color: #24292f;
            padding: 0;
            font-family: inherit;
        }}
        code {{
            background-color: #f6f8fa;
            color: #d6336c;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }}

        img {{ max-width: 100%; height: auto; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        blockquote {{ border-left: 4px solid #95a5a6; padding-left: 15px; color: #7f8c8d; margin: 15px 0; }}
        .highlight {{ background-color: #fff3cd; padding: 2px 4px; }}
    </style>
</head>
<body>
{self._markdown_to_html(markdown_report)}
</body>
</html>"""
        return html

    def _markdown_to_html(self, md: str) -> str:
        """简单的Markdown转HTML（基础功能）"""
        import re

        lines = md.split('\n')
        html_lines = []
        in_code_block = False
        in_table = False
        table_rows = []

        for line in lines:
            # 代码块
            if line.strip().startswith('```'):
                if in_code_block:
                    html_lines.append('</code></pre>')
                    in_code_block = False
                else:
                    html_lines.append('<pre><code>')
                    in_code_block = True
                continue

            if in_code_block:
                html_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))
                continue

            # 表格
            if '|' in line and line.strip().startswith('|'):
                if not in_table:
                    in_table = True
                    table_rows = []
                # 跳过分隔行
                if re.match(r'^\|[\s\-|]+\|$', line.strip()):
                    continue
                table_rows.append(line)
                continue
            else:
                if in_table:
                    # 生成表格HTML
                    if table_rows:
                        html_lines.append('<table>')
                        for i, row in enumerate(table_rows):
                            cells = [c.strip() for c in row.strip('|').split('|')]
                            tag = 'th' if i == 0 else 'td'
                            html_lines.append('<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>')
                        html_lines.append('</table>')
                    in_table = False
                    table_rows = []

            # 标题
            if line.startswith('# '):
                html_lines.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('## '):
                html_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('### '):
                html_lines.append(f'<h3>{line[4:]}</h3>')
            # 分隔线
            elif line.strip() == '---':
                html_lines.append('<hr>')
            # 引用
            elif line.startswith('> '):
                html_lines.append(f'<blockquote>{line[2:]}</blockquote>')
            # 图片
            elif '![' in line:
                match = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', line)
                if match:
                    alt, src = match.groups()
                    html_lines.append(f'<img src="{src}" alt="{alt}">')
            # 粗体
            elif '**' in line:
                line = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', line)
                html_lines.append(f'<p>{line}</p>')
            # 空行
            elif line.strip() == '':
                html_lines.append('')
            # 普通段落
            else:
                html_lines.append(f'<p>{line}</p>')

        # 处理最后一个表格
        if in_table and table_rows:
            html_lines.append('<table>')
            for i, row in enumerate(table_rows):
                cells = [c.strip() for c in row.strip('|').split('|')]
                tag = 'th' if i == 0 else 'td'
                html_lines.append('<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>')
            html_lines.append('</table>')

        return '\n'.join(html_lines)


# 全局实例
_report_generator = None


def get_report_generator() -> Optional[ReportGenerator]:
    return _report_generator


def init_report_generator():
    global _report_generator
    _report_generator = ReportGenerator()
