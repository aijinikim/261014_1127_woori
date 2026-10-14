import pyfiglet
from termcolor import colored

# 구현 : pyfiglet + colored를 적용한 sentence 출력
# 코드 완성하신 분들은 웹 사이트 10번 노드 비밀번호 해제 후 코드 확인
sentence = "GOOD"
py_sentence = pyfiglet.figlet_format(sentence)
# print(py_sentence)
color_py_sentence = colored(py_sentence, "yellow")
print(color_py_sentence)