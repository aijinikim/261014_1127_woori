from ultralytics import YOLO
import time
import cv2

# 1. 비디오 경로 설정
cap = cv2.VideoCapture("http://210.99.70.120:1935/live/cctv066.stream/playlist.m3u8")

# 2. 모델 선택
# model = YOLO("yolo11l.pt")
model = YOLO("yolo11l_openvino_model/")

# 3. 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("프레임 확인해주세요.")
        break
    # 3-1. 추론 시작 시간 측정
    start_time = time.perf_counter()    # 추론 시작 시간
    
    # 3-2. 모델 추론
    results = model(frame, verbose=False, device="intel:cpu")
    
    # 3-3. 추론 종료 시간 측정
    end_time = time.perf_counter()      # 추론 종료 시간
    
    # 3-4. FPS 계산
    if_time = end_time - start_time
    fps = 1 / if_time   # 1초 / 1장 걸린 시간
    
    # 3-5. 결과 시각화
    annotated_frame = results[0].plot()
    
    # 3-6. FPS 표시
    cv2.putText(
        annotated_frame,
        f"{fps:.1f} FPS",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )
    
    # 3-7. 윈도우 창 띄우기
    cv2.imshow("YOLO_FPS", annotated_frame)
    
    # 3-8. q 키를 눌러서 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("q키를 눌러서 종료")
        break
        
# 4. 자원 해제
cap.release()
cv2.destroyAllWindows()