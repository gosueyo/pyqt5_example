## Ex 3-1. 창 띄우기.

import sys
from PyQt5.QtWidgets import QApplication, QWidget

# QWidget이 부모 클래스
# 부모 클래스를 상속 받아서 My App이라는 클래스를 생성
class MyApp(QWidget):

    def __init__(self):
        # super는 부모 클래스를 가리킨다.
        super().__init__()
        self.initUI()

    def initUI(self):
        # 창의 이름을 설정
        self.setWindowTitle('My APP')
        # 창의 위치를 설정
        self.move(1000, 300)
        # 창의 사이즈를 설정
        self.resize(600, 400)
        self.show()


if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())
