from ultralytics import YOLO
import cv2

# 1. 비디오 경로 설정
cap = cv2.VideoCapture("http://210.99.70.120:1935/live/cctv009.stream/playlist.m3u8")

# 2. 모델 로드
model = YOLO("yolo11n.pt")

# 3. 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("프레임 확인")
        break
    # 성공했을때 처리
    # 3-1. 객체 추적
    results = model.track(frame, persist=True, conf=0.4)
    # persist = 이전 프레임 정보 유지
    
    # 3-2. 추적 결과 시각화
    annotated_frame = results[0].plot()
    
    # 3-3. 윈도우 창 생성
    window_name = "CCTV_YOLO_TRACK"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL) # 창 크기 조절
    cv2.imshow(window_name, annotated_frame)

    # 3-4. q키를 눌러서 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("q키를 눌러서 종료합니다.")
        break
    
# 4. 자원 해제
cap.release()
cv2.destroyAllWindows()