import gradio as gr
from deep_translator import MyMemoryTranslator

# 1. 번역 함수 정의
def trans_ko_to_en(text):
    en_text = MyMemoryTranslator(
                    source="ko-KR", target="en-US"
                ).translate(text)
    return en_text

# 2. Gradio 인터페이스 정의 및 웹 실행
gr.Interface(
    fn=trans_ko_to_en,
    inputs="text",
    outputs="text",
    title="한국말을 영어로 번역",
    description="한국말 입력하시면 영어로 번역 됩니다!"
).launch(share=True)