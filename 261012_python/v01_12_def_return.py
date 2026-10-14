import pyfiglet
from termcolor import colored

def make_highlight(text:str):
    """
    입력된 문자열을 pyfigle, termcolor를 이용해서 꾸며준다.
    
        매개변수 : text(str)
    """
    py_text = pyfiglet.figlet_format(text)
    color_py_text = colored(py_text, "red")
    return color_py_text

# highlight_text = make_highlight("Hello")
# print(highlight_text)
print(make_highlight("Hello"))
