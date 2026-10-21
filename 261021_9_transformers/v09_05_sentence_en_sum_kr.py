# from deep_translator import GoogleTranslator    # 구글 번역
from deep_translator import MyMemoryTranslator
from transformers import pipeline
# pip install transformers==5.20.2
# 다운그레이드
# pip install transformers==4.46.3

def trans_en_to_ko(sum_en_text:str)-> str:
    """
    주어진 영어 문장을 한국어로 번역하는 함수
    """
    sum_ko_text = MyMemoryTranslator(source="en-US", target="ko-KR").translate(sum_en_text)
    return sum_ko_text

# 1. 요약 파이프라인
summarizer = pipeline("summarization", model="t5-small")

# 2. 요약할 원문 (영어 단락)
text = """
A special 25th anniversary edition of the extraordinary international bestseller, including a new Foreword by Paulo Coelho.
Combining magic, mysticism, wisdom and wonder into an inspiring tale of self-discovery, The Alchemist has become a modern classic, selling millions of copies around the world and transforming the lives of countless readers across generations.
Paulo Coelho's masterpiece tells the mystical story of Santiago, an Andalusian shepherd boy who yearns to travel in search of a worldly treasure.
His quest will lead him to riches far different-and far more satisfying-than he ever imagined.
Santiago's journey teaches us about the essential wisdom of listening to our hearts, of recognizing opportunity and learning to read the omens strewn along life's path, and, most importantly, to follow our dreams.
"""

# 3. 요약 실행
summary = summarizer(
    text,
    min_length=20,  # 최소 토큰 수
    max_length=100, # 최대 토큰 수
    do_sample=False # 매번 동일 결과 출력
)

# 4. 결과 확인
sum_en_text = summary[0]["summary_text"]
# print(f"요약된 문장 : {sum_en_text}")
"""
요약된 문장 : a special 25th anniversary edition of the extraordinary international bestseller.
includes a new Foreword by Paulo Coelho . teaches us about the essential wisdom of listening to our hearts .
요약 문장: 놀라운 국제적 베스트셀러의 특별한 25주년 기념판.
파울로 코엘료가 새로 쓴 서문이 수록되어 있으며, 우리 마음의 소리에 귀를 기울이는 것의 본질적인 지혜를 일깨워 준다.
"""

sum_ko_text = trans_en_to_ko(sum_en_text)
print(f"### 한국어로 번역 후 요약된 문장 : {sum_ko_text} ###")
"""
한국어로 번역 후 요약된 문장 : 특별한 국제 베스트셀러 25 주년 기념 특별판.
Paulo Coelho의 새로운 서문이 포함되어 있습니다.
우리의 마음을 듣는 데 필수적인 지혜에 대해 가르쳐줍니다.
"""

## 과제
# 결과 확인 => 영어 => 번역 => 한국어
# 11:40분 까지