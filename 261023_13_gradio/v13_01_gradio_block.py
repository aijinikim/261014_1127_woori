import gradio as gr
from ultralytics import YOLO
from deep_translator import MyMemoryTranslator

model = YOLO("yolo11n.pt")

# 1. 지금까지 만든 함수 3개 정의
def say_hello(name):
    return "Hello,", name

def trans_ko_to_en(text):
    en_text = MyMemoryTranslator(source="ko-KR", target="en-US").translate(text)
    return en_text

def det_image(image):
    results = model(image)
    annotated_image = results[0].plot()
    return annotated_image

with gr.Blocks() as gr_web:
    gr.Markdown("# 내가 만든 웹 서비스 모음") # 제목
    
    with gr.Tab("인사"):
        name_box = gr.Textbox(label="이름")
        hello_box = gr.Textbox(label="인사말")
        # click(실행할 함수, 읽어올 칸, 결과 쓸 칸)
        gr.Button("인사하기").click(say_hello, name_box, hello_box)
        
    with gr.Tab("번역"):
        ko_box = gr.Textbox(label="한국어")
        en_box = gr.Textbox(label="영어")
        gr.Button("번역하기").click(trans_ko_to_en, ko_box, en_box)
        
    with gr.Tab("YOLO탐지"):
        in_image = gr.Image(type="numpy", label="사진 업로드")
        out_image = gr.Image(label="탐지 결과")
        gr.Button("탐지하기").click(det_image, in_image, out_image)
        
gr_web.launch(share=True) 