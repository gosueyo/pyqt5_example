import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PyQt5.QtCore import QTimer, QTime, QDate, Qt
from PyQt5.QtGui import QFont

class ModernTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('타이머')
        self.setGeometry(100, 100, 360, 600) # 스마트폰과 유사한 비율로 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.time = QTime(0, 0, 0)
        self.is_running = False

        self.initUI()

    def initUI(self):
        # 전체 레이아웃
        main_vbox = QVBoxLayout()
        main_vbox.setContentsMargins(20, 20, 20, 20)

        # 상단 공간
        main_vbox.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 날짜 표시
        date_str = QDate.currentDate().toString('yyyy.MM.dd. ddd')
        date_label = QLabel(date_str)
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setFont(QFont('Arial', 14))
        date_label.setStyleSheet("color: #888;")
        main_vbox.addWidget(date_label)

        # 타이머 시간 표시
        self.time_label = QLabel(self.time.toString('HH:mm:ss'))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont('Arial', 60, QFont.Bold))
        main_vbox.addWidget(self.time_label)

        # 총 시간 표시 (UI 모방)
        total_label = QLabel('TOTAL\n00H 00M') # 예시 텍스트
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setFont(QFont('Arial', 12))
        total_label.setStyleSheet("color: #aaa;")
        main_vbox.addWidget(total_label)

        # 중앙 공간
        main_vbox.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 버튼 레이아웃
        btn_hbox = QHBoxLayout()
        self.start_pause_btn = QPushButton('시작')
        self.reset_btn = QPushButton('초기화')

        # 버튼 스타일링
        self.start_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 16px;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)


        self.start_pause_btn.clicked.connect(self.toggle_timer)
        self.reset_btn.clicked.connect(self.reset_timer)

        btn_hbox.addWidget(self.start_pause_btn)
        btn_hbox.addWidget(self.reset_btn)

        main_vbox.addLayout(btn_hbox)

        self.setLayout(main_vbox)
        self.setStyleSheet("background-color: #fff;")
        self.show()

    def toggle_timer(self):
        if not self.is_running:
            self.timer.start(1000) # 1초마다 갱신
            self.is_running = True
            self.start_pause_btn.setText('일시정지')
            self.start_pause_btn.setStyleSheet("background-color: #ff9800; color: white; font-size: 16px; border-radius: 5px; padding: 10px;") # 주황색
        else:
            self.timer.stop()
            self.is_running = False
            self.start_pause_btn.setText('계속')
            self.start_pause_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; border-radius: 5px; padding: 10px;") # 녹색

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.time.setHMS(0,0,0)
        self.time_label.setText(self.time.toString('HH:mm:ss'))
        self.start_pause_btn.setText('시작')
        self.start_pause_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; border-radius: 5px; padding: 10px;") # 녹색

    def update_time(self):
        self.time = self.time.addSecs(1)
        self.time_label.setText(self.time.toString('HH:mm:ss'))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ModernTimer()
    sys.exit(app.exec_())