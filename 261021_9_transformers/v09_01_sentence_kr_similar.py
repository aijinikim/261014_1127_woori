from sentence_transformers import SentenceTransformer, util

# 1. 모델 로드
model = SentenceTransformer("jhgan/ko-sroberta-multitask")
# 모델 설명 :
    # 한국어 문장을 의미 공간에 맵핑 (한국어 SBERT)
    # all-MiniLM-L6-v2 는 영어 전용 -> 한국어는 한국어 학습 모델 사용

# 2. 비교할 두 문장 정의
# 2-1. 의미상 완전히 다른 두 문장 예시 -> 낮은 유사도 기대
# sen1 = "고양이가 소파 위에서 자고 있다"
# sen2 = "내일 학교에서 수학 시험이 있다"
# 2-2. 의미상 비슷한 두 문장 예시 -> 높은 유사도 기대
sen1 = "그는 도서관에서 책을 읽고 있다"
sen2 = "그는 책을 읽으러 도서관에 와 있다"
# 2-3. 비슷한 단어
# sen1 = "강아지"
# sen2 = "개"

# 3. 문장 -> 숫자 좌표로 바꾸기(인코딩)
emb1 = model.encode(sen1, convert_to_tensor=True)
emb2 = model.encode(sen2, convert_to_tensor=True)

# 4. 두 문장 유사도 측정 (코사인 유사도)
cos_sim = util.pytorch_cos_sim(emb1, emb2)

# 5. 결과 출력
print(f"두 문장의 유사도 : {cos_sim.item():.4f}")

# 2-1. 다른 의미 : 두 문장의 유사도 : -0.0390
# 2-2. 비슷한 의미 : 두 문장의 유사도 : 0.8935
# 2-3. 비슷한 단어 : 두 문장의 유사도 : 0.7976
