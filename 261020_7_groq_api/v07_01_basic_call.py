# pip install groq
# pip install python-dotenv
from groq import Groq
from dotenv import load_dotenv  # .env 읽는 도구
import os

# 1. .env의 GROQ_API_KEY 키를 환경변수로 불러옴
load_dotenv()

# 2. 키로 Groq 클라이언트 만들기 (키를 통해서 요청)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 3. 질문 보내기
res = client.chat.completions.create(
    model="openai/gpt-oss-20b", # 무료, 빠름
    messages=[
        {
            "role": "user", # 질문이나 요청할때
            "content": "groq라는 회사에 대해서 한국말로 알려줘"  # 질문 
        }
    ]
)

# 4. 답변 받기
result = res.choices[0].message.content
print(f"AI의 답변 : {result} \n =======================")