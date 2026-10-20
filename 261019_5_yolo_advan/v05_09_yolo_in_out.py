from ultralytics import solutions
import cv2

# 1. 비디오 경로 설정
cap = cv2.VideoCapture("http://210.99.70.120:1935/live/cctv066.stream/playlist.m3u8")

# 2. 라인 설정
line_points = (178, 300), (453, 309)
# 클릭된 좌표는 (178, 300) 입니다.
# 클릭된 좌표는 (453, 309) 입니다.

# 3. 모델 로드
yolo_counter = solutions.ObjectCounter(
    model="yolo11n.pt",
    region=line_points
)

# 4. 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("프레임 확인해주세요.")
        break
    # 4-1. 프레임 리사이즈
    re_frame = cv2.resize(frame, (640, 480))
    
    # 4-2. 모델 추론
    results = yolo_counter(re_frame)
    
    # 4-3. 윈도우 창 띄우기
    cv2.imshow("IN/OUT", results.plot_im)
    
    # 4-4. q 키 눌러서 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("q키를 눌러서 종료")
        break
    
# 5. 자원 해제
cap.release()
cv2.destroyAllWindows()