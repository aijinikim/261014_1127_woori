# import pytesseract      # OCR 사용
# from PIL import Image   # 이미지 처리 도구
# import os

# # 1. Tesseract 실행 파일 경로 지정
# pytesseract.pytesseract.tesseract_cmd = "c:/Program Files/Tesseract-OCR/tesseract.exe"

# # 2. 이미지 불러오기
# # image = Image.open("261021_10_ocr/input.jpg")
# # image = Image.open("261021_10_ocr/input_car.jpg")
# image = Image.open("261021_10_ocr/input_naver.PNG")

# # 3. OCR 수행
# results = pytesseract.image_to_string(
#     image,
#     lang="kor+eng"
# )

# # 4. 결과 출력
# print(f"OCR 실행 결과 : {results}")
"""
OCR 실행 결과 :
This is a lot of 12 point text to test theocr code and see if it works on all types
of file format.

The quick brown dog jumped over the
lazy fox. The quick brown dog jumped
over the lazy fox. The quick brown dog
jumped over the lazy fox. The quick
brown dog jumped over the lazy fox.
"""

"""
OCR 실행 결과 :
Ｌㄴ스트스때스56<0내

이수진

팀장 / 제품개발팀

+123-456-7890
16110@「6811/8「626516.000
123 40616 56, 407 다, 51 12345
"""

"""
OCR 실행 결과 :
LARANASKIN

이수진

팀장 / 제 품 개발팀

+123-456-7890
hello@reallygreatsite.com
123 Anywhere St., Any City, ST 12345
"""

## 영수증
"""
OCR 실행 결과 : 춤플러스 ens?
이 10118 0000000000애야26
18)031 - 960.

교왕시 BIA! AL

교환/환불/결제변경은 구매 점포에서
한달(신선7일)이내 가능, 임대매장 예외
(미개봉)상품,영수증/결제카드 지참

0
18
ox
oe:

DY 44 41 E{ 2 4006     3,4

02 몽블랑제 빵골라담기 3,850 1 3,850

09 클래시코토마토갈릭 2,490 1  2,.490

과세 물        8, 937

가               893

구매금이                         9, 830

4자체발급80마스터골드 5387-20-*\-5784 50
카드결제 :                  9, 830

할부개월 : 일시불     승인번호 : 62810585

한화다이렉트 자동차보험

ite 기정의 달 0번트>
wine aed 460
1008 1000 34, 5/1631 $18
Be Saal anise ae
"""


## 1. 번호판 이미지 인식
"""
OCR 실행 결과 : 
"""

## 2. 다른 OCR과 비교
import easyocr

reader = easyocr.Reader(["ko", "en"])

result = reader.readtext("261021_10_ocr/input_car.jpg", detail=0)
print(f"OCR 실행 결과 : {result}")
# OCR 실행 결과 : ['헌', '154러7070', 'Sheer Driving Pleasure', 'BMW Korea', 'mae']