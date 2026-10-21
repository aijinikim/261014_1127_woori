from transformers import pipeline

# 1. 감정 분석 파이프라인 생성
classifier = pipeline("sentiment-analysis")

# 2. 분석할 문장 입력
# 2-1. 긍정 문장
# text = "I'm feeling really great today."
# 2-2. 부정 문장
# text = "She is not happy today."
# 2-3. 부정 단어
text = "angry"

# 3. 문장 분석
results = classifier(text)

# 4. 결과 확인
# POSITIVE, NEGATIVE
print(f"문장 분석 결과 : {results[0]['label']}")
# 1에 가까울수록 모델 확신도 높음
print(f"문장 분석 점수 : {results[0]['score']:.4f}")

# text = "I'm feeling really great today."
# 문장 분석 결과 : POSITIVE
# 문장 분석 점수 : 0.9999

# text = "She is not happy today."
# 문장 분석 결과 : NEGATIVE
# 문장 분석 점수 : 0.9997

# text = "angry"
# 문장 분석 결과 : NEGATIVE
# 문장 분석 점수 : 0.9997