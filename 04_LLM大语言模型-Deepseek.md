## Ch04 LLM大语言模型-Deepseek

### 一、大语言模型（LLM）基础概念

#### 1.1 什么是大语言模型

大语言模型（Large Language Model，简称LLM）是一种基于海量文本数据训练的深度学习模型，它能够理解和生成自然语言文本，完成复杂对话、文本创作等任务。我们可以将其理解为数字世界的“通才”，因为它的“大脑”（参数）足够大。

**核心原理**：大模型本质上就是在不断预测“下一个词是什么”。你输入一段话的开头，它就能根据统计概率预测下一个词，然后一个词一个词地往下接，直到完成整个文本生成过程。

#### 1.2 大模型的“大”体现在哪里

**训练数据大**：以GPT-3为例，其训练数据总量约3000亿个Token，相当于300万本10万字的书籍。这些数据来源于网络爬虫、论坛帖子、电子书、维基百科等多种渠道。

**参数量大**：参数是大模型的“大脑神经元”，参数越多，模型越“聪明”。常见模型规模包括：

- 7B模型：70亿参数
- 13B模型：130亿参数
- 70B模型：700亿参数
- 175B模型：1750亿参数

#### 1.3 核心架构：Transformer

Transformer是一种广泛应用于自然语言处理任务的神经网络架构，因其自注意力机制而能够高效处理序列数据中的长距离依赖关系。我们可以把它认为是一位“超级翻译官”，能够同时处理输入序列中的所有单词，并根据上下文关系进行理解和生成。

#### 1.4 Token：文本的基本单位

Token是大模型处理文本的基本单位，可以理解为“文本碎片”。它不是“字”，也不是“词”，而是模型自己定义的一种切分方式。例如：

- 英文：“Hello, how are you?” → ["Hello", ",", " how", " are", " you", "?"]
- 中文：“今天天气真好” → ["今天", "天气", "真", "好"] 或 ["今", "天", "天", "气", "真", "好"]

### 二、DeepSeek API接入

#### 2.1 DeepSeek平台注册与API密钥获取

DeepSeek作为国产领先的大语言模型，具有强大的中文理解能力和OpenAI API全兼容设计，为开发者提供了便捷的接入体验。学员需要访问DeepSeek官网注册开发者账号，完成实名认证后进入控制台启用API服务。

**关键步骤：**

- 访问DeepSeek开放平台API key栏目（https://platform.deepseek.com/api_keys）
- 点击创建API Key并妥善保存（密钥仅在生成时显示一次）
- 完成企业或个人实名认证（需准备身份证或营业执照）

#### 2.2 API密钥安全管理最佳实践

 **绝对禁止**在代码中硬编码API密钥，这是行业安全红线。推荐使用环境变量管理：

```python
import os
from dotenv import load_dotenv

#方法一：使用dotenv加载.env文件
load_dotenv()  # 加载环境变量
API_KEY = os.getenv('DEEPSEEK_API_KEY')

#方法二：交互式安全输入
import getpass
if not os.environ.get("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter API key for DeepSeek: ")
```

#### 2.3 OpenAI兼容接口配置

 DeepSeek完美兼容OpenAI API格式，迁移成本极低。配置示例如下：

```python
import os
from openai import OpenAI

#设置环境变量
os.environ["DEEPSEEK_API_KEY"] = "your_api_key"

#创建OpenAI客户端（兼容DeepSeek）
client = OpenAI(
    base_url="https://api.deepseek.com",  #DeepSeek API端点
    api_key=os.getenv("DEEPSEEK_API_KEY")
)
```

**技术要点：**

- `base_url`参数指定为DeepSeek的API地址（https://api.deepseek.com）
- 原有基于OpenAI的代码几乎无需修改即可迁移
- DeepSeek-V3支持128K超长上下文，远超行业标准

#### 2.4 调用对话 API

在创建 API key 之后，你可以使用以下样例脚本的来访问 DeepSeek API。样例为非流式输出，您可以将 stream 设置为 true 来使用流式输出。

**.env文件**（用于存储你的api_key）

```
DEEPSEEK_API_KEY=your_api_key
```

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  #加载环境变量
API_KEY = os.getenv('DEEPSEEK_API_KEY')

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个优秀的AI智能助手"},
        {"role": "user", "content": "请介绍一下你自己"},
    ],
    stream=False
)

print(response.choices[0].message.content)
```

