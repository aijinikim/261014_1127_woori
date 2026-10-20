from ultralytics import solutions
import cv2

# 1. 비디오 경로 설정
cap = cv2.VideoCapture("http://210.99.70.120:1935/live/cctv066.stream/playlist.m3u8")

# 2. 모델 로드
yolo_speed = solutions.SpeedEstimator(
    model="yolo11n.pt",
    max_speed=120,  # 최대 속도 상한
    classes=[2],    # car
    line_width=2,    # 선 두께
    meter_per_pixel=0.5
)

# 3. 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("프레임 확인해주세요.")
        break
    
    # 3-1. 모델 추론(속도 계산)
    results = yolo_speed(frame)
    
    # 3-2. 윈도우 창 띄우기(처리된 프레임 표시)
    cv2.imshow("SPEED", results.plot_im)
    
    # 3-3. q 키 입력 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("q 키를 눌러서 종료")
        break
    
# 4. 자원 해제
cap.release()
cv2.destroyAllWindows()