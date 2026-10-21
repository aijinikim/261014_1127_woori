import streamlit as st  # 웹앱 만드는 도구
from ultralytics import YOLO
import cv2

# 1. st 페이지 기본 설정
st.set_page_config(layout="wide")   # 화면을 가로로 넓게 사용
st.title("YOLO 실시간 CCTV 탐지")    # 페이지 맨 위에 제목 표시

# 2. 영상 출력 공간 설정
frame_placeholder = st.empty()

# 3. 비디오 경로 설정
cap = cv2.VideoCapture("http://210.99.70.120:1935/live/cctv066.stream/playlist.m3u8")

# 4. 모델 로드
model = YOLO("yolo11n.pt")

# 5. 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("프레임 확인해주세요...")
        st.warning("프레임 확인해주세요...")
        break
    # 5-1. 모델 추론
    results = model(frame)
    
    # 5-2. 탐지 결과를 이미지에 시각화
    annotated_frame = results[0].plot()
    
    # 5-3. st placeholder에 프레임 갱신
    frame_placeholder.image(annotated_frame, channels="BGR")
    
# 6. 자원 해제
cap.release()               # CCTV 연결 종료
cv2.destroyAllWindows()     # 열린 창 정리