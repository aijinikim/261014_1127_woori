from ultralytics import YOLO

# 1. 모델 로드
model = YOLO("yolo11l.pt")

# 2. 모델 내보내기
# model.export(format="onnx", )
# model.export(format="openvino")
model.export(format="onnx", quantize=16, device=0)