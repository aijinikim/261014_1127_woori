import urllib.request   # 인터넷 주소로 자료 요청하는 도구
import json             # 글자로 된 자료를 사전(dict) 모양으로 바꾸는 도구
import pandas as pd     # 자료를 엑셀 같은 표로 다루는 도구
from ultralytics import YOLO
import cv2
from v06_03_openapi_yolo import its_cctv

# 03번 함수 import해서 가져오기
input_url = its_cctv()

# 9. 프레임 설정
cap = cv2.VideoCapture(input_url)

# 10. 모델 로드
model = YOLO("yolo11n.pt")

# 11. 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("프레임 확인해주세요.")
        break
    results = model(frame)
    annotated_frame = results[0].plot()
    
    # 11-1. 윈도우 창 설정 및 띄우기
    cv2.namedWindow("OPENAPI", cv2.WINDOW_NORMAL)   # 창 크기 조절
    cv2.imshow("OPENAPI", annotated_frame)
    
    # 11-2. q키를 눌러서 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("q키를 눌러서 종료합니다.")
        break

# 12. 자원 해제
cap.release()
cv2.destroyAllWindows()

# 주석 1 ~ 8번 부분을 함수로 만들어주세요.
    # 매개변수 : cctv_index
    # return : cctv_url