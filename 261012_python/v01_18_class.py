# 여러분들만의 클래스 정의
class Cafe:

# 속성 3개 이상
    def __init__(self, name, menu, price):
        self.name = name
        self.menu = menu
        self.price = price
        self.sold = 0 # 판매 잔 수 설정
        
# 메서드 2개 이상
    def order(self, count):
        self.sold += count
        print(f"{self.name}: {self.menu} {count}잔 주문 -> {self.price * count}원")
    
    def report(self):
        print(f"{self.name} 매출 : {self.sold}잔 {self.price * self.sold}원")
        
# 객체 2개 이상
cafe1 = Cafe("부천카페", "아메리카노", 3000)
cafe2 = Cafe("부평카페", "카페라떼", 6000)

# 메서드 2개 호출
# cafe1.order(2)
# cafe1.report()

cafe2.order(3)
cafe2.report()

# ~ 12:50분 까지 진행