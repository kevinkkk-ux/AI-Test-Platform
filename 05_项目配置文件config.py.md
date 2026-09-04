## Ch05 项目配置文件config.py

### 一、本章概述

#### 1.1 学习目标

- 理解项目配置文件在企业级AI应用中的重要性
- 掌握Python环境变量配置的最佳实践
- 能够独立设计和维护大型项目的配置体系
- 理解配置参数对项目运行的影响

#### 1.2 配置文件的作用

配置文件是项目的“神经中枢”，集中管理所有可变参数，使得：

- **环境隔离**：开发、测试、生产环境使用不同配置
- **安全防护**：敏感信息（API密钥、密码等）不硬编码在代码中
- **维护便捷**：修改参数无需修改源码，降低风险
- **团队协作**：统一配置规范，减少沟通成本

### 二、环境变量加载机制

#### 2.1 环境变量的重要性

```python
# config.py
import os
from dotenv import load_dotenv
load_dotenv()
```

**代码解析：**

- **os 模块**：Python标准库，提供与操作系统交互的功能，包括读取环境变量
- **python-dotenv 库**：第三方库，用于从 `.env` 文件加载环境变量到系统环境
- **load_dotenv() 函数**：自动加载项目根目录下的 `.env` 文件，将其中的键值对注入到 `os.environ` 中

**配置优先级：**

```
系统环境变量 > .env文件 > 默认值
```

#### 2.2 `.env` 文件示例

```python
# .env 文件（不提交到版本控制）
DB_HOST=192.168.1.100
DB_PORT=3307
DB_USER=admin
DB_PASSWORD=my_secure_password
DEEPSEEK_API_KEY=sk-your-api-key-here
```

**安全最佳实践：**

- `.env` 文件必须添加到 `.gitignore` 中
- 仓库中提供 `.env.example` 模板文件
- 生产环境使用系统的环境变量配置工具

### 三、数据库配置模块

#### 3.1 配置定义

```python
# config.py
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "123456"),
    "database": os.getenv("DB_DATABASE", "softtest_db"),
    "charset": os.getenv("DB_CHARSET", "utf8mb4")
}
```

#### 3.2 参数详解

| 参数       | 默认值        | 说明                                    |
| ---------- | ------------- | --------------------------------------- |
| `host`     | `127.0.0.1`   | 数据库服务器地址，本地开发使用localhost |
| `port`     | `3306`        | MySQL默认端口，需转为整数类型           |
| `user`     | `root`        | 数据库登录用户名                        |
| `password` | `123456`      | 数据库密码，生产环境必须修改            |
| `database` | `softtest_db` | 项目使用的数据库名称                    |
| `charset`  | `utf8mb4`     | 字符集，支持emoji表情等四字节字符       |

#### 3.3 在项目中的使用

```python
# database.py
class DatabaseManager:
    def __init__(self):
        self.config = DB_CONFIG  # 导入配置
        
    def connect(self) -> bool:
        try:
            self.connection = mysql.connector.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config["database"],
                charset=self.config["charset"]
            )
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
```

**设计要点：**

- 配置字典化，便于传递和管理
- 类型转换：`int()` 确保端口为整数
- 默认值选择：优先使用127.0.0.1和3306等通用设置

### 四、LLM配置模块

#### 4.1 DeepSeek大模型配置

```python
# config.py
DEEPSEEK_CONFIG = {
    "api_key": os.getenv("DEEPSEEK_API_KEY", "enter_your_api_key"),
    "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "temperature": float(os.getenv("DEEPSEEK_TEMP", 0.1)),
    "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    "max_tokens": int(os.getenv("DEEPSEEK_MAX_TOKEN", 2000))
}
```

#### 4.2 参数详解

| 参数          | 默认值                     | 说明                                 |
| ------------- | -------------------------- | ------------------------------------ |
| `api_key`     | `sk-...`                   | DeepSeek API密钥，注意默认值仅为示例 |
| `base_url`    | `https://api.deepseek.com` | API请求基础地址                      |
| `temperature` | `0.1`                      | 生成温度，越低越稳定，越高越有创造性 |
| `model`       | `deepseek-chat`            | 使用的模型名称                       |
| `max_tokens`  | `2000`                     | 最大生成Token数                      |

#### 4.3 在项目中使用

```python
# llm_init.py
from config import DEEPSEEK_CONFIG

def init_llm():
    llm = ChatOpenAI(
        model=DEEPSEEK_CONFIG["model"],
        temperature=DEEPSEEK_CONFIG["temperature"],
        max_tokens=DEEPSEEK_CONFIG["max_tokens"],
        api_key=DEEPSEEK_CONFIG["api_key"],
        base_url=DEEPSEEK_CONFIG["base_url"]
    )
    return llm
```

**温度参数说明：**

- `0.0-0.2`：确定性输出，适合测试用例生成等精确任务
- `0.3-0.7`：平衡模式，适合一般对话
- `0.8-1.0`：创造性输出，适合创意写作

### 五、平台基础配置

#### 5.1 配置定义

```python
# config.py 第24-29行
PLATFORM_CONFIG = {
    "theme": "soft",
    "title": "企业AI软件测试一体化管理平台",
    "desc": "测试用例生成|RAG需求解析|Selenium自动化测试|数据分析智能体|数据可视化",
    "server_port": int(os.getenv("PLATFORM_PORT", 7860))
}
```

#### 5.2 参数详解

| 参数          | 默认值              | 说明                                                  |
| ------------- | ------------------- | ----------------------------------------------------- |
| `theme`       | `soft`              | Gradio界面主题，可选"soft", "default", "monochrome"等 |
| `title`       | `企业AI软件测试...` | 浏览器标签页标题                                      |
| `desc`        | `测试用例生成|...`  | 平台功能描述，用竖线分隔                              |
| `server_port` | `7860`              | Gradio服务端口，可被环境变量覆盖                      |

#### 5.3 在Gradio界面中的应用

```python
# main.py
with gr.Blocks(title=PLATFORM_CONFIG["title"]) as main_blocks:
    gr.Markdown(f"# {PLATFORM_CONFIG['title']}\n### {PLATFORM_CONFIG['desc']}")
```

### 六、路径配置模块

#### 6.1 配置定义

```python
# config.py
PATH_CONFIG = {
    "chroma_db_root": "./chroma_db",
    "faiss_vector_store": "files/vector_store",
    "embed_model_path": os.getenv("EMBED_MODEL_PATH", "D:\\PycharmProjects\\model\\models--BAAI--bge-large-zh-v1.5\\snapshots\\79e7739b6ab944e86d6171e44d24c997fc1e0116"),
    "case_xlsx": "files/testcases.xlsx",
    "visual_output_dir": "files/visualizations",
    "file_root": "files",
    "script_dir": "files/scripts"
}
```

#### 6.2 路径架构设计

```
project_root/
├── chroma_db/              # Chroma向量数据库存储
├── files/
│   ├── vector_store/       # FAISS向量库
│   ├── testcases.xlsx      # 测试用例Excel文件
│   ├── visualizations/     # 可视化图表输出
│   └── scripts/            # 生成的Selenium脚本
└── config.py
```

#### 6.3 路径配置最佳实践

```python
# 使用路径配置
def save_visualization(chart_html, filename):
    output_dir = PATH_CONFIG["visual_output_dir"]
    os.makedirs(output_dir, exist_ok=True)  # 确保目录存在
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(chart_html)
    return filepath
```

**设计要点：**

- 使用相对路径，便于项目迁移
- 使用 `os.makedirs(exist_ok=True)` 自动创建目录
- 嵌入模型路径使用绝对路径，需根据实际环境调整

### 七、Selenium测试目标配置

#### 7.1 配置定义

```python
# config.py
SELENIUM_TARGET = {
    "login_url": "http://127.0.0.1:8848/adminLogin/index.html",
    "register_url": "http://127.0.0.1:8848/denglu/jiemian/index.html"
}
```

#### 7.2 在自动化测试中的使用

```python
# auto_test.py
def execute_login_cases(url, uid_input_id, pwd_input_id):
    target_url = url or SELENIUM_TARGET["login_url"]  # 使用默认配置
    # ... 启动Selenium执行测试 ...
```

**设计目的：**

- 集中管理测试目标URL
- 便于切换不同测试环境
- 支持用户自定义覆盖默认配置

### 八、状态常量与枚举定义

#### 8.1 状态常量

```python
# config.py
STATUS = {
    "PENDING": 0,    # 待处理
    "RUNNING": 1,    # 执行中
    "SUCCESS": 2,    # 成功
    "FAILED": 3      # 失败
}
```

#### 8.2 类型枚举

```python
# config.py
FILE_TYPE = {"DEMAND": 1, "API_DOC": 2, "SCRIPT": 3, "REPORT": 4, "OTHER": 99}
KNOWLEDGE_FILE_TYPE = {"DEMAND": "demand", "SCRIPT": "script", "API_DOC": "api_doc"}
CASE_GENERATE_TYPE = {"AI": 1, "RAG": 2}
AUTO_TASK_TYPE = {"LOGIN": "login_auto", "REGISTER": "register_auto", "CUSTOM": "custom_auto"}
```

#### 8.3 在项目中的应用

```python
# 状态管理
def update_task_status(task_id, new_status):
    db.execute_query(
        "UPDATE analysis_task SET task_status = %s WHERE id = %s",
        (STATUS["SUCCESS"], task_id)  # 使用常量，避免魔法数字
    )

# 类型判断
def save_file(file_type_str):
    if file_type_str == KNOWLEDGE_FILE_TYPE["DEMAND"]:
        # 保存为需求文档
        pass
```

**设计优势：**

- **可读性**：`STATUS["SUCCESS"]` 比 `2` 更易于理解
- **可维护性**：修改状态值只需修改一处
- **类型安全**：避免拼写错误导致的bug

### 九、配置管理最佳实践总结

#### 9.1 配置设计原则

| 原则           | 说明                    | 示例                                |
| -------------- | ----------------------- | ----------------------------------- |
| **环境分离**   | 不同环境使用不同配置    | 开发用127.0.0.1，生产用真实IP       |
| **默认值合理** | 提供最常用的默认值      | 端口默认7860，模型默认deepseek-chat |
| **类型明确**   | 显式进行类型转换        | `int()`, `float()`, `str()`         |
| **集中管理**   | 所有配置集中到config.py | 避免散落在各个文件中                |
| **安全第一**   | 敏感信息不硬编码        | API密钥使用环境变量                 |

#### 9.2 常见问题与解决方案

**Q1：配置修改后不生效？**

- 检查是否重新加载了 `.env` 文件
- 确认环境变量优先级是否覆盖了 `.env`

**Q2：生产环境如何配置？**

- 使用云服务商的环境变量管理工具
- 或使用配置中心（如Spring Cloud Config、Consul）

**Q3：配置类型错误怎么办？**

- 运行时检查：`assert isinstance(port, int)`
- 使用Pydantic等配置验证库

### 十、本章小结

通过本章学习，我们掌握了：

1. 环境变量加载机制及 `.env` 文件的使用

2. 数据库配置、LLM配置、平台配置的设计方法

3. 路径配置的最佳实践

4. 状态常量和枚举类型的使用

5. 配置管理在企业级项目中的重要性