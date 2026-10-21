# [Transformers pipeline 과제]
# 1. 1 ~ 4번 파일 복사 후 _en_ => _kr_ 로 파일명만 변경
# 2. _kr_ 파일 안에 코드를 한국어 문장을 입력한 실습으로 수정
# 3. 모델 변경 또는 파이프라인 변경 등으로 접근하여 진행

# [유사도]
# model = SentenceTransformer("jhgan/ko-sroberta-multitask")

# [감정 분석]
# classifier = pipeline("sentiment-analysis", model="tabularisai/multilingual-sentiment-analysis")
# # 대체 모델 : model="matthewburke/korean_sentiment" (한국어 전용, 라벨 LABEL_0=부정 / LABEL_1=긍정)

# [문장 생성]
# generator = pipeline("text-generation", model="skt/kogpt2-base-v2")   # 최초 1회 모델 다운로드 필요

# [문장 요약]
# summarizer = pipeline("summarization", model="eenzeenee/t5-base-korean-summarization")

# - 13:10분 까지 진행