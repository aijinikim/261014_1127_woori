import gradio as gr
from ultralytics import YOLO

# 1. 모델 로드
model = YOLO("yolo11n.pt")

# 2. 이미지 탐지 함수
def det_image(image):
    results = model(image)
    annotated_frame = results[0].plot()
    return annotated_frame
    
# 3. gradio 웹 인터페이스 정의 및 실행
gr.Interface(
    fn=det_image,
    inputs=gr.Image(type="numpy"),
    outputs=gr.Image(),
    title="YOLO 이미지 객체 탐지",
    description="이미지를 업로드하면 YOLO가 객체를 탐지합니다."
).launch(share=True)