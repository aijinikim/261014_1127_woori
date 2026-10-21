from transformers import pipeline

# 1. 텍스트 생성 파이프라인 생성
# gpt2 는 한국어 약함 -> SKT 한국어 GPT-2 사용
generator = pipeline("text-generation", model="skt/kogpt2-base-v2")   # 최초 1회 모델 다운로드 필요

# 2. 시드 문장 입력 (이어 쓸 첫 부분)
q = input("이어서 쓸 첫 문장을 입력해주세요 : ")

# 3. 텍스트 생성 실행
results = generator(
    q,
    max_new_tokens=50,       # 추가 생성할 토큰 수 (길수록 추론 시간도 길어짐)
    num_return_sequences=1,  # 반환 문장 1개로 설정
    repetition_penalty=1.5,  # 같은 말 반복 억제 (KoGPT2 는 반복이 잦음)
    do_sample=False          # 매번 동일 결과 출력
)

# 4. 결과 출력
print(results[0]["generated_text"])
"""
이어서 쓸 첫 문장을 입력해주세요 : 근육을 키우려면
근육을 키우려면 무엇보다 자신의 몸을 잘 관리해야 한다.
특히, 평소에는 운동을 통해 체력을 키우고 운동량을 늘려야 하는데, 이때도 무리한 운동은 피하고, 충분한 수면을 취하는 것이 좋다.
또한, 스트레스를 많이 받는다면 스트레칭이나 가벼운 걷기 등
"""

"""
이어서 쓸 첫 문장을 입력해주세요 : 아주 졸릴 때는
아주 졸릴 때는 괜찮지만 잠이 오지 않을 때엔 오히려 더 피곤할 수 있다.
잠을 잘 때도 마찬가지다.
아침에는 눈을 뜨고 일어나서 자야 한다.
눈은 항상 촉촉하고 맑아야 하는데 이럴 경우 눈물이 많이 나와 잠을
"""
