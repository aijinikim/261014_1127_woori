from sentence_transformers import SentenceTransformer, util

# 1. 모델 로드
model = SentenceTransformer("all-MiniLM-L6-v2")
# 모델 설명 :
    # 영어 문장을 의미 공간에 맵핑
    # 빠름

# 2. 비교할 두 문장 정의
# 2-1. 의미상 완전히 다른 두 문장 예시 -> 낮은 유사도 기대
# sen1 = "The cat is sleeping on the sofa"
# sen2 = "Tomorrow, I have a math exam at school"
# 2-2. 의미상 비슷한 두 문장 예시 -> 높은 유사도 기대
sen1 = "He is reading a book in the library"
sen2 = "He is at the library reading a book"
# 2-3. 비슷한 단어(0.8040)
# sen1 = "dog"
# sen2 = "puppy"

# 3. 문장 -> 숫자 좌표로 바꾸기(인코딩)
emb1 = model.encode(sen1, convert_to_tensor=True)
emb2 = model.encode(sen2, convert_to_tensor=True)

# 4. 두 문장 유사도 측정 (코사인 유사도)
cos_sim = util.pytorch_cos_sim(emb1, emb2)

# 5. 결과 출력
print(f"두 문장의 유사도 : {cos_sim.item():.4f}")