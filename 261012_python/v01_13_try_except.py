user_input = input("피트로 환산할 미터 값을 입력해주세요 : ")

try:
    meters = float(user_input)
    feet = meters * 3.28084
    print(f"{meters}m는 {feet}ft 입니다.")
except ValueError:
    print("숫자를 입력해주세요!")
    
# 실행했을때 발생하는 오류 해결 => 해결 후 간략히 채팅방에 방법 공유 ~ 10:30분까지
# 1. 구글링, 2. 클로드, 3. 챗봇, 4. Copilot