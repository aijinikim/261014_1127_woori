from ultralytics import SAM
import time
import cv2

# 1. 모델 로드
model = SAM("sam_b.pt")
# sam_b(빠름), l(정확)

# 2. 이미지 경로 설정
image_path = "261016_5_yolo_advan/input_sam.jpg"

# 2-1. 이미지 읽기
intput_image = cv2.imread(image_path)

# 2-2. 이미지 리사이즈
re_intput_image = cv2.resize(intput_image, (197, 236))

# 3. 추론 시간 측정 시작
start_time = time.time()

# 4. 모델 추론
# model(re_intput_image, save=True)
results = model(re_intput_image)

# 5. 추론 시간 측정 종료
end_time = time.time()

# 라벨 제거
no_label_output = results[0].plot(labels=False, boxes=False)

# 결과 이미지 저장
cv2.imwrite("./output_sam.jpg", no_label_output)

# 6. 결과 로그 출력
if_time = end_time - start_time
print(f"총 추론 시간 : {if_time:.2f}")
print("추론 완료")