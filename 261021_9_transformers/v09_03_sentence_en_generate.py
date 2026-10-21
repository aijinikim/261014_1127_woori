from transformers import pipeline

# 1. 텍스트 생성 파이프라인 생성
generator = pipeline("text-generation", model="gpt2")   # 최초 1회 모델 다운로드 필요

# 2. 시드 문장 입력 (이어 쓸 첫 부분)
q = input("이어서 쓸 첫 문장을 입력해주세요 : ")

# 3. 텍스트 생성 실행
results = generator(
    q,
    max_new_tokens=50,      # 추가 생성할 토큰 수 (길수록 추론 시간도 길어짐)
    num_return_sequences=1,  # 반환 문장 1개로 설정
)

# 4. 결과 출력
print(results[0]["generated_text"])
"""
이어서 쓸 첫 문장을 입력해주세요 : to build muscle...
to build muscle... and now you're getting bigger.
It's like a new workout machine."
This workout machine is so well-fitted with the new 6-foot-3-inch, 220-pound frame that it would be easy to see why there is
근육을 키우는 데 도움이 되죠... 그리고 이제 몸이 점점 커지고 있어요. 마치 새로운 운동 기구 같아요."
이 운동 기구는 190cm, 100kg의 새로운 체격에 너무나 잘 맞아떨어져서, 왜 인기가 있는지 쉽게 알 수 있을 겁니다.
"""

"""
이어서 쓸 첫 문장을 입력해주세요 : When you're extremely sleepy
When you're extremely sleepy, you usually hear a soft whisper.
It may be a bit of a longtime, but you may hear a soft, soft moan.
Don't tell anyone! I'm making you nervous, dont'tell anyone!
이어질 첫 문장을 입력해 주세요: 아주 졸릴 때
아주 졸릴 때면, 보통 나직한 속삭임이 들려오곤 합니다. 꽤 오랜 시간이 흐른 뒤일지도 모르지만, 아주 가냘픈 신음 소리가 들릴 수도 있어요.
누구에게도 말하지 마세요! 제가 당신을 불안하게 만들고 있나요? 절대 아무에게도 말하지 마세요!
"""
