# 📝 AI软件测试一体化管理平台

> 基于大模型的智能测试用例生成、自动化脚本生成、自动化测试执行与数据分析智能体系统

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-green.svg)](https://python.langchain.com/)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-blue.svg)](https://www.mysql.com/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)](https://www.selenium.dev/)

---

## 📋 目录

- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [技术栈](#技术栈)
- [项目架构](#项目架构)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [数据库设计](#数据库设计)
- [核心模块说明](#核心模块说明)
- [演示截图](#演示截图)
- [开发日志](#开发日志)
- [未来规划](#未来规划)
- [许可证](#许可证)

---

## 🌟 项目简介

本项目是一个**基于大模型的AI软件测试一体化管理平台**，将大语言模型（LLM）与软件测试全流程深度结合，实现从测试用例智能生成、自动化脚本生成、自动化测试执行到测试数据分析的全链路智能化。

项目同时包含一个**基于LangGraph的数据分析智能体**，支持通过自然语言查询电商数据库，自动生成SQL、执行查询、统计分析、可视化图表和完整分析报告。

### ✨ 项目亮点

- 🤖 **大模型驱动**：基于DeepSeek大模型，通过Prompt Engineering实现结构化输出
- 🧠 **智能体工作流**：基于LangGraph构建7节点工作流，支持条件路由与自动重试
- 🔒 **安全验证机制**：SQL生成后自动安全校验，防止危险操作
- 📊 **数据可视化**：自动选择图表类型（饼图/柱状图/折线图/散点图）
- 💾 **数据库持久化**：测试用例主表+明细表+操作日志，完整记录
- 🌐 **网页交互界面**：基于Gradio，多选项卡设计，操作友好

---

## 🎯 核心功能

### 模块一：测试用例AI辅助生成

- 支持**登录模块**、**注册模块**、**修改个人信息模块**三大业务模块
- 基于**等价类划分法** + **健壮边界值法**生成测试用例
- 包含有效等价类、无效等价类、合法边界、非法边界四种类型
- 输出Excel格式测试用例，支持预览和下载
- 测试用例自动存入MySQL数据库

### 模块二：Selenium自动化脚本生成

- 支持上传接口文档（txt/docx/pdf/md）
- AI智能解析页面元素配置（URL、元素定位、功能描述）
- 结合测试用例Excel，自动生成完整的Selenium自动化测试脚本
- 脚本基于pytest框架，包含异常处理和日志输出
- 支持Edge浏览器驱动自动管理

### 模块三：自动化测试执行

- 配置目标页面URL和测试用例Excel
- 一键执行自动化测试，支持无头模式
- 自动填充表单、点击提交、处理Alert弹窗
- 验证测试结果，统计通过率
- 执行结果自动写回Excel

### 模块四：数据分析智能体（LangGraph）

- **自然语言查询**：用中文提问，自动生成SQL
- **7节点工作流**：SQL生成→安全验证→执行→分析→可视化→报告→错误处理
- **自动重试机制**：SQL生成或执行失败，自动重试最多3次
- **智能选图**：根据数据特征自动选择饼图/柱状图/折线图/散点图
- **完整报告**：包含数据摘要、统计分析、AI洞察、可视化图表、业务建议

---

## 🛠️ 技术栈

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **编程语言** | Python | 3.9+ | 主开发语言 |
| **大模型框架** | LangChain | 0.1+ | 大模型应用开发框架 |
| **智能体框架** | LangGraph | 0.1+ | 智能体工作流编排 |
| **大模型API** | DeepSeek | v4-flash | 大语言模型 |
| **网页框架** | Gradio | 4.0+ | 网页交互界面 |
| **数据库** | MySQL | 8.0+ | 数据持久化 |
| **数据库驱动** | pymysql / mysql-connector | - | MySQL连接 |
| **自动化测试** | Selenium | 4.0+ | 浏览器自动化 |
| **驱动管理** | webdriver-manager | 4.0+ | 浏览器驱动自动管理 |
| **数据处理** | pandas | 2.0+ | 数据分析与处理 |
| **数据可视化** | matplotlib | 3.7+ | 图表生成 |
| **Excel处理** | openpyxl | 3.1+ | Excel文件读写 |
| **配置管理** | python-dotenv | 1.0+ | 环境变量管理 |
| **版本控制** | Git | - | 代码版本管理 |

---

## 🏗️ 项目架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        Gradio 网页界面                            │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │  测试用例生成  │ 自动化脚本生成│ 自动化测试执行│  数据分析智能体 │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  测试用例生成模块  │     │  自动化测试模块   │     │  数据分析智能体   │
│  data_generator  │     │  api_doc_parser  │     │    agent.py     │
│                  │     │  selenium_gen    │     │  (LangGraph)    │
│  等价类+边界值法  │     │  auto_test       │     │                 │
│  Excel输出        │     │  Selenium执行    │     │  7节点工作流     │
│  MySQL持久化      │     │  通过率统计      │     │  条件路由+重试   │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────┐
                    │   DeepSeek 大模型    │
                    │  (SQL生成/文本生成)   │
                    └─────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────┐
                    │     MySQL 数据库     │
                    │  soft_test_db       │
                    │  analysis_db        │
                    └─────────────────────┘
```

### 数据分析智能体工作流（LangGraph）

```
用户输入自然语言
        │
        ▼
┌───────────────┐
│  节点1         │
│  generate_sql │──────┐
│  生成SQL       │      │
└───────┬───────┘      │
        │              │
        ▼              │
┌───────────────┐      │
│  节点2         │      │
│ validate_sql  │      │
│  安全验证      │      │
└───────┬───────┘      │
        │              │
   ┌────┴────┐         │
   │         │         │
   ▼         ▼         │
  通过      失败        │
   │         │         │
   ▼         ▼         │
┌───────┐  重试<3次?──┘
│ 节点3  │    │
│execute│    否
│ 执行  │    │
└───┬───┘    ▼
    │      ┌───────┐
    │      │ 节点7  │
    │      │ handle│
    │      │ error │
    │      └───┬───┘
    ▼          │
┌───────┐      │
│ 节点4  │      │
│analyze│      │
│ 分析  │      │
└───┬───┘      │
    ▼          │
┌───────┐      │
│ 节点5  │      │
│visual │      │
│ 可视化 │      │
└───┬───┘      │
    ▼          │
┌───────┐      │
│ 节点6  │      │
│report │      │
│ 报告  │      │
└───┬───┘      │
    ▼          ▼
   结束       结束
```

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- MySQL 8.0+
- Edge浏览器（自动化测试用）

### 1. 克隆项目

```bash
git clone https://github.com/kevinkkk-ux/AI-Test-Platform.git
cd AI-Test-Platform
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# DeepSeek API配置
DEEPSEEK_API_KEY=sk-你的DeepSeek_API_Key

# MySQL数据库配置
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_DATABASE=soft_test_db
```

### 4. 初始化数据库

在Navicat或MySQL命令行中执行 `init_db.sql`：

```bash
mysql -u root -p < init_db.sql
```

### 5. 运行测试用例生成系统

```bash
python web_ui.py
```

浏览器访问 `http://127.0.0.1:7860`

### 6. 运行数据分析智能体

```bash
cd ai_data_analyzer
python main.py
```

浏览器访问 `http://127.0.0.1:7861`

---

## 📁 项目结构

```
AI-Test-Platform/
├── 📄 README.md                    # 项目说明文档
├── 📄 requirements.txt             # 依赖清单
├── 📄 .env                         # 环境变量（不提交到Git）
├── 📄 .gitignore                   # Git忽略配置
├── 📄 init_db.sql                  # 数据库初始化脚本
│
├── 📁 config.py                    # 项目配置文件
├── 📁 database.py                  # 数据库操作封装
├── 📁 data_generator.py            # 测试用例生成核心
├── 📁 web_ui.py                    # Gradio网页界面（测试用例系统）
│
├── 📁 api_doc_parser.py            # 接口文档智能解析
├── 📁 selenium_generator.py        # Selenium脚本生成
├── 📁 auto_test.py                 # 自动化测试执行引擎
│
├── 📁 ai_data_analyzer/            # 数据分析智能体（独立模块）
│   ├── 📄 main.py                  # 入口文件（Gradio界面）
│   ├── 📄 config.py                # 配置文件
│   ├── 📄 database.py              # 数据库连接
│   ├── 📄 sql_generator.py         # SQL生成+安全验证
│   ├── 📄 agent.py                 # LangGraph智能体（核心）
│   ├── 📄 data_analyzer.py         # 数据分析+AI洞察
│   ├── 📄 visualizer.py            # 可视化图表生成
│   └── 📄 report_generator.py      # 分析报告生成
│
├── 📁 files/                       # 文件目录
│   ├── 📄 login_testcases.xlsx     # 登录测试用例
│   ├── 📄 register_testcases.xlsx  # 注册测试用例
│   ├── 📄 modify_profile_testcases.xlsx  # 修改信息测试用例
│   ├── 📁 scripts/                 # 生成的Selenium脚本
│   └── 📁 rag_docs/                # RAG文档目录
│
├── 📄 login.html                   # 本地测试登录页面
└── 📁 docs/                        # 课程设计文档
```

---

## 🗄️ 数据库设计

### 测试用例数据库（soft_test_db）

#### test_case_main（用例主表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| case_type | VARCHAR | 用例类型（登录/注册/修改信息） |
| group_num | INT | 用例数量 |
| case_title | VARCHAR | 用例组标题 |
| case_content | TEXT | 字段规则配置 |
| generate_type | INT | 生成类型（0=等价类,1=边界值,2=AI） |
| create_time | TIMESTAMP | 创建时间 |

#### test_case_detail（用例明细表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| main_id | INT | 关联主表ID |
| case_no | VARCHAR | 用例编号 |
| field_values | JSON | 字段值（JSON格式） |
| scene_desc | TEXT | 场景描述 |
| case_type | VARCHAR | 用例类型 |
| expected_result | TEXT | 预期结果 |
| create_time | TIMESTAMP | 创建时间 |

#### operation_log（操作日志表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| user_id | INT | 用户ID |
| operation_type | VARCHAR | 操作类型 |
| operation_desc | TEXT | 操作描述 |
| related_id | INT | 关联ID |
| create_time | TIMESTAMP | 操作时间 |

### 电商数据库（analysis_db）

| 表名 | 说明 | 主要字段 |
|------|------|---------|
| users | 用户表 | id, username, membership_level, account_balance, city, province |
| product_categories | 产品分类表 | id, category_name, parent_id |
| products | 产品表 | id, category_id, product_name, unit_price, stock_quantity, sales_volume |
| orders | 订单表 | id, order_number, user_id, total_amount, actual_amount, order_status |
| order_details | 订单明细表 | id, order_id, product_id, quantity, unit_price, subtotal |
| reviews | 商品评价表 | id, user_id, product_id, rating, content |
| points_records | 积分记录表 | id, user_id, points, record_type, source |
| visit_logs | 访问日志表 | id, user_id, page_url, visit_time, device_type |

---

## 📖 核心模块说明

### 1. 测试用例生成（data_generator.py）

**核心原理**：通过Prompt Engineering控制大模型输出结构化Markdown表格，解析后转为Excel。

**Prompt设计要点**：
- 明确指定测试方法（等价类+边界值）
- 明确字段规则和约束
- 明确输出格式（Markdown表格，指定表头）
- 要求包含四种用例类型
- 限制只输出表格，不输出多余文字

**输出解析**：
- 解析Markdown表格为CSV
- 验证列数一致性
- 转为pandas DataFrame
- 保存为Excel并写入数据库

### 2. SQL生成与安全验证（sql_generator.py）

**Schema Prompt构建**：
- 动态获取数据库表结构
- 包含表名、字段名、字段类型、字段注释、主键信息
- 作为System Prompt传给大模型

**安全验证机制**：
- 禁止关键字检查：INSERT、UPDATE、DELETE、DROP、CREATE、ALTER、TRUNCATE
- 危险操作模式检查：INTO OUTFILE、LOAD_FILE、BENCHMARK、SLEEP
- 确保只允许SELECT查询

### 3. LangGraph智能体（agent.py）

**7个节点**：
1. `generate_sql`：调用大模型生成SQL
2. `validate_sql`：验证SQL安全性
3. `execute_sql`：执行SQL查询
4. `analyze_data`：统计分析+AI洞察
5. `visualize`：生成可视化图表
6. `generate_report`：生成完整分析报告
7. `handle_error`：错误处理

**条件路由**：
- 验证通过 → 执行SQL
- 验证失败且重试<3次 → 重新生成
- 验证失败且重试≥3次 → 错误处理
- 执行成功 → 数据分析
- 执行失败且重试<3次 → 重新生成
- 执行失败且重试≥3次 → 错误处理

### 4. 可视化（visualizer.py）

**自动选图逻辑**：
- 1个分类列 + 1个数值列 + 分类≤6 → 饼图
- 1个分类列 + 1个数值列 + 分类>6 → 柱状图
- 2个数值列 → 散点图
- 其他 → 柱状图

**中文字体处理**：
- Windows下自动使用微软雅黑
- 解决负号显示问题

---

## 📸 演示截图

### 测试用例生成系统

| 功能 | 截图 |
|------|------|
| 测试用例生成界面 | （待补充） |
| 自动化脚本生成 | （待补充） |
| 自动化测试执行 | （待补充） |

### 数据分析智能体

| 功能 | 截图 |
|------|------|
| 主界面 | （待补充） |
| 分析报告 | （待补充） |
| SQL与查询结果 | （待补充） |

---

## 📝 开发日志

### 2026.09.01 - 2026.09.03
- ✅ 完成测试用例AI生成模块（登录/注册/修改信息）
- ✅ 完成Gradio网页界面
- ✅ 完成MySQL数据库设计与持久化
- ✅ 解决大模型输出格式不稳定问题（多层解析+容错）

### 2026.09.04
- ✅ 完成Selenium自动化脚本生成模块
- ✅ 完成接口文档智能解析（支持txt/docx/pdf/md）
- ✅ 完成自动化测试执行引擎
- ✅ 实现Alert弹窗处理与通过率统计

### 2026.09.05 - 2026.09.06
- ✅ 完成简单版数据分析功能（直接调用大模型）
- ✅ 完成饼图/柱状图/折线图可视化
- ✅ 项目提交到GitHub

### 2026.09.07
- ✅ 完成基于LangGraph的数据分析智能体（独立模块）
- ✅ 实现7节点工作流编排
- ✅ 实现条件路由与自动重试机制
- ✅ 实现SQL安全验证机制
- ✅ 完成电商数据库设计（8张表+示例数据）
- ✅ 完成完整分析报告生成（含AI洞察+可视化+业务建议）

---

## 🔮 未来规划

- [ ] **RAG增强**：完善RAG模块，支持上传需求文档生成测试用例
- [ ] **更多测试方法**：增加因果图法、场景法、错误推测法等
- [ ] **测试报告生成**：自动生成HTML格式测试报告
- [ ] **用户管理系统**：增加用户注册登录、权限管理
- [ ] **历史记录查询**：支持查询历史生成记录和测试结果
- [ ] **云服务部署**：部署到云服务器，支持公网访问
- [ ] **移动端适配**：优化手机端界面体验
- [ ] **单元测试**：为核心模块编写单元测试

---

## 📄 许可证

本项目仅供学习和研究使用。

---

## 🙏 致谢

感谢所有开源项目的贡献者，特别是：
- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Gradio](https://github.com/gradio-app/gradio)
- [Selenium](https://github.com/SeleniumHQ/selenium)
- [DeepSeek](https://www.deepseek.com/)

---

<div align="center">

**如果这个项目对你有帮助，欢迎给个 ⭐ Star！**

</div>
