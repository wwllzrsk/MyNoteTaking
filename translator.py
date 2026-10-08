"""translator.py —— 调用 OpenRouter 上的 DeepSeek 做翻译（课件 P24–P26）"""
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 从项目根目录的 .env 读取 OPENROUTER_API_KEY

TARGET_LANGUAGE = "中文"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

SYSTEM_PROMPT = (
    "You are a professional translator. "
    f"Translate the user's input into {TARGET_LANGUAGE}. "
    "Only return the translated text, without any explanation."
)


def llm_generate(user_prompt: str) -> str:
    """把 user_prompt 交给 LLM，返回翻译后的文本。"""
    response = client.chat.completions.create(
        model="nvidia/nemotron-3-super-120b-a12b:free",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "How are you?"
    print(llm_generate(text))
