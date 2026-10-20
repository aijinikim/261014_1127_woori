from ultralytics import solutions
import cv2

# 1. 비디오 경로 설정
cap = cv2.VideoCapture(0)

# 2. 모델 로드
distance = solutions.DistanceCalculation(
    model="yolo11n.pt",
    conf=0.3,
    show=False
)

# 3. 프레임 처리
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("프레임 읽기 실패")
        break
    
    # 3-1. 모델 추론
    # distance(frame)
    results = distance.process(frame)
    
    # # 윈도우 창 띄움
    cv2.imshow("distance", results.plot_im)
    
    # 3-2. 거리 추출
    pixel_distance = results.pixels_distance
        
    # 3-4. q 키로 종료
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     print("q키를 눌러서 종료")
    #     break    
        
    # 3-3. 거리에 따른 정의
    if pixel_distance is None or pixel_distance == 0:
        print("[거리] ----px [상태] 입력 안됨")
        continue
    
    if pixel_distance >= 150:
        status = "Safe"
    elif pixel_distance >= 100:
        status = "Warning"
    else:
        status = "Danger"
        
    print(f"[거리] : {pixel_distance}, [상태] :  {status}")
    
    # 3-4. q 키로 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("q키를 눌러서 종료")
        break
    
# 4. 자원 해제
cap.release()
cv2.destroyAllWindows()

## 픽셀 거리 단위에 따른 상태 정의