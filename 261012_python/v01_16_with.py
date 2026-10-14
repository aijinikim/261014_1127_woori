# "x"	새 파일 만들기	이미 있으면 오류	기존 파일을 실수로 덮지 않게 저장
# "rb" "wb"	이미지 등 읽기·쓰기	"r" "w" 와 같음	이미지 복사·업로드·저장
# "r+"	읽기와 쓰기 둘 다	그대로 두고 수정	파일 일부만 고쳐 쓰기

# 위 3가지 모드에 대해서 코드 작성 후 결과 확인

# 1. x 모드
# with open("memo.txt", "x", encoding="utf-8") as f:
#     f.write("새로 추가를 하나요? 막나요?")
# Exception has occurred: FileExistsError
# [Errno 17] File exists: 'memo.txt'
#   File "C:\Users\Woori\Desktop\wori\261012_python\v01_16_with.py", line 8, in <module>
#     with open("memo.txt", "x", encoding="utf-8") as f:
#          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# FileExistsError: [Errno 17] File exists: 'memo.txt'

# 2. rb 모드(이미지 읽기)
# with open("temp.jpg", "rb") as img:
#     img_data = img.read()

# print(img_data)

# 3. wb 모드(이미지 쓰기)
# with open("wb_img.jpg", "wb") as m_img:
#     m_img.write(img_data)

# 4. r+ 모드(읽기와 쓰기 둘 다)
with open("memo.txt", "r+", encoding="utf-8") as f:
    text = f.read() # 먼저 읽기
    f.seek(0)       # 맨 앞부터 수정
    f.write("새롭게 시작할게")   # 새로 쓰기
    # f.write(text.replace("새로운", "낡은")) # 문자 변경
    f.truncate()    # 나머지 내용 제거
    
print("DONE")
