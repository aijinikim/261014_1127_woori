import streamlit as st
from ultralytics import YOLO
import cv2
import pandas as pd             # 엑셀 같은 데이터 타입으로 만드는 도구
import time                     # 시간 측정
import plotly.express as px     # 그래프 그리는 도구

# 1. 화면 구성
# 좌/우 2개 컬럼 생성
col1, col2 = st.columns(2)  # 같은 너비 두 칸 생성

with col1:
    frame_placeholder = st.empty()  # 왼쪽 컬럼 YOLO 프레임 표시용

with col2:
    chart_placeholder = st.empty()  # 오른쪽 컬럼 객체 수 차트 표시용
    
# 2. 비디오 경로 설정
cap = cv2.VideoCapture("http://210.99.70.120:1935/live/cctv066.stream/playlist.m3u8")

# 3. 모델 로드
@st.cache_resource
def load_model():
    return YOLO("yolo11n.pt")

model = load_model()

# 4. 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("프레임 확인")
        st.warning("프레임 확인")
        break
    # 4-1. 모델 추론
    result = model(frame)
    
    # 4-2. 탐지 결과 시각화 가져오기
    annotated_frame = result[0].plot()
    
    # 4-3. 탐지된 객체 클래스 이름 추출
    labels = []
    for c in result[0].boxes.cls:
        labels.append(model.names[int(c)])
    
    # 4-4. 차트 그리기
    if labels:  # 뭔가 탐지했다면
        # labels 리스트를 DataFrame으로 변환 후 객체별 개수 집계
        df_count = pd.DataFrame({"Object" : labels})
        df_count = df_count.value_counts().reset_index(name="Count")
        # 종류별 개수 세기

        # 4-5. px 막대 그래프
        fig = px.bar(
            df_count,
            x="Object",             # 가로축 : 객체 이름
            y="Count",              # 세로축 : 개수
            title="탐지 객체 수",     # 그래프 이름
            color="Object",         # 객체마다 색상 설정
            text="Count",            # 막대 위에 "Count" 숫자로 표시
        )
    else:   # 탐지 안 되었을때
        df_count = pd.DataFrame({"Object" : []})    # 빈 표 만들기
        fig = px.bar(
            df_count,
            x="Object",
            y="Count", 
            title="탐지 객체 수",
        )
        
    # 4-6. st에 결과 표시
    frame_placeholder.image(annotated_frame, channels="BGR")
    chart_placeholder.plotly_chart(fig, use_container_width=True, key=f"chart_{time.time()}")
        
# 5. 자원 해제
cap.release()
cv2.destroyAllWindows()