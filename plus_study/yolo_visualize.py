from pathlib import Path
from ultralytics import YOLO

# 1. img path
input_img = "tti_result.jpg"

# 2. model
model = YOLO("yolo11n.pt")

# 3. inference
result = model(
    input_img,
    visualize=True,     # 레이어별 특징 맵 저장
    save=True,          # 박스 그린 이미지 저장
    imgsz=1280,         # 특징 맵 해상도 키움 (작은 물체 반응 확인)
    conf=0.1,           # 확신도 낮은 박스까지 표시
    save_txt=True,      # 박스 좌표를 txt 로 저장
    save_conf=True,     # txt 에 확신도 포함
    line_width=1,       # 박스 선 얇게
    project="vis",      # 결과 폴더: vis/exp1, vis/exp12, ...
    name="exp1",
)

# 4. 검출 결과 확인
r = result[0]
print("저장 폴더:", r.save_dir)
for c, p in zip(r.boxes.cls, r.boxes.conf):
    print(r.names[int(c)], round(float(p), 2))

# 5. 꼭 볼 특징 맵 — 16: 작은 물체 / 19: 중간 / 22: 큰 물체
vis_dir = Path(r.save_dir) / Path(input_img).stem
for s in (16, 19, 22):
    for f in vis_dir.glob(f"stage{s}_*.png"):
        print(f)