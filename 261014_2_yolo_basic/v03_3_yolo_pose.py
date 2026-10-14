from ultralytics import YOLO

# 1. 모델 로드
model = YOLO("yolo11n-pose.pt")

# 2. 모델 추론
model("261014_2_yolo_basic/input_pose.mp4", save=True)