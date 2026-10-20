from ultralytics import solutions
import cv2

# 1. 비디오 경로 설정
cap = cv2.VideoCapture("http://210.99.70.120:1935/live/cctv066.stream/playlist.m3u8")

# 2. 영역 좌표 설정 (dict 형식 - 키로 영역 구분)
region_points = {
    "region1" : [(229, 273), (188, 307), (444, 307), (430, 279)],
    "region2" : [(170, 304), (51, 308), (3, 331), (4, 473), (633, 475), (631, 378), (574, 327), (461, 309)]
}
# 클릭된 좌표는 (229, 273) 입니다.
# 클릭된 좌표는 (188, 307) 입니다.
# 클릭된 좌표는 (444, 307) 입니다.
# 클릭된 좌표는 (430, 279) 입니다.

# 클릭된 좌표는 (170, 304) 입니다.
# 클릭된 좌표는 (51, 308) 입니다.
# 클릭된 좌표는 (3, 331) 입니다.
# 클릭된 좌표는 (4, 473) 입니다.
# 클릭된 좌표는 (633, 475) 입니다.
# 클릭된 좌표는 (631, 378) 입니다.
# 클릭된 좌표는 (574, 327) 입니다.
# 클릭된 좌표는 (461, 309) 입니다.

# 3. 모델 로드
yolo_region = solutions.RegionCounter(
    model="yolo11n.pt",
    show=False,
    region=region_points
)

# 4. 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("프레임 확인해라")
        break
    # 4-1. 프레임 크기 조정(좌표계 통일)
    re_frame = cv2.resize(frame, (640, 480))
    
    # 4-2. 구역 내 객체 수 계산
    results = yolo_region(re_frame)
    
    # 4-3. 처리된 프레임 표시 (show=False => 우리가 직접 창을 띄움)
    cv2.imshow("REGION", results.plot_im)
    
    # 4-4. q 키를 눌러서 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("q키를 눌러서 종료합니다.")
        break

# 5. 자원 해제
cap.release()
cv2.destroyAllWindows()