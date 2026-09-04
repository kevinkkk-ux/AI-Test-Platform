import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
api_key = os.getenv("API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {"role": "system", "content": "你是一个优秀的AI智能助手"},
        {"role": "user", "content": "请介绍一下你自己，你是什么大模型，我要具体的，你是pro还是flash"},
    ],
    stream=False
)

print(response.choices[0].message.content)
