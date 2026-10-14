from ultralytics import YOLO

# 1. 모델 로드
model = YOLO("yolo11n.pt")
# print(model.names)
# 2. 모델 추론(파라미터 튜닝)
model(
    "261014_2_yolo_basic/input_want.jpg",
    save=True,
    classes=[55]
    # conf=0.2,           # 신뢰도 20% 이상만 탐지
    # max_det=1,        # 최대 탐지 개수 설정
    # save_crop=True,     # 탐지 영역 이미지 저장
    # save_txt=True       # 좌표 텍스트 저장
)

# cake만 탐지될 수 있도록 설정