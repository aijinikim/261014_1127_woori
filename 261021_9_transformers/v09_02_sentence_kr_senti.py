from transformers import pipeline

# 1. 감정 분석 파이프라인 생성
# 기본 모델(distilbert-sst2)은 영어 전용 -> 한국어 포함 다국어 감정 모델 지정
classifier = pipeline("sentiment-analysis", model="tabularisai/multilingual-sentiment-analysis")
# 대체 모델 : model="matthewburke/korean_sentiment" (한국어 전용, 라벨 LABEL_0=부정 / LABEL_1=긍정)

# 2. 분석할 문장 입력
# 2-1. 긍정 문장
# text = "오늘 기분이 정말 좋아요"
# 2-2. 부정 문장
text = "그녀는 오늘 정말 행복하지 않다"
# 2-3. 부정 단어
# text = "화가 난다"

# 3. 문장 분석
results = classifier(text)

# 4. 결과 확인
# Very Negative, Negative, Neutral, Positive, Very Positive (5단계)
print(f"문장 분석 결과 : {results[0]['label']}")
# 1에 가까울수록 모델 확신도 높음
print(f"문장 분석 점수 : {results[0]['score']:.4f}")

# text = "오늘 기분이 정말 좋아요"
# 문장 분석 결과 : Positive
# 문장 분석 점수 : 0.7780

# text = "그녀는 오늘 행복하지 않다"
# 문장 분석 결과 : Negative
# 문장 분석 점수 : 0.6532

# text = "화가 난다"
# 문장 분석 결과 : Negative
# 문장 분석 점수 : 0.3632
