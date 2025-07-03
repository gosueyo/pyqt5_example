
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QSpacerItem, QSizePolicy, QGraphicsOpacityEffect)
from PyQt5.QtCore import QTimer, QTime, Qt, QPropertyAnimation
from PyQt5.QtGui import QFont, QPainter, QColor

class RotatableLabel(QLabel):
    """회전 애니메이션을 위한 커스텀 QLabel"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rotation_angle = 0

    def setRotation(self, angle):
        self.rotation_angle = angle
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 중앙을 기준으로 회전
        transform = painter.transform()
        transform.translate(self.width() / 2, self.height() / 2)
        transform.rotate(self.rotation_angle)
        transform.translate(-self.width() / 2, -self.height() / 2)
        painter.setTransform(transform)
        
        # 부모 클래스의 paintEvent 호출 대신 직접 텍스트 그리기
        painter.setFont(self.font())
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.drawText(self.rect(), self.alignment(), self.text())

class FinalTimerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Final Timer')
        self.setGeometry(100, 100, 380, 640)

        # 상태 변수
        self.countdown_time = QTime(0, 0, 0)
        self.is_running = False
        
        # 타이머
        self.main_timer = QTimer(self)
        self.main_timer.timeout.connect(self.update_countdown)
        
        self.alarm_animation_timer = QTimer(self)
        self.alarm_animation_timer.timeout.connect(self.animate_alarm)
        self.alarm_angle_direction = 1
        self.alarm_brightness_direction = 1

        self.initUI()
        self.setup_initial_state()

    def initUI(self):
        # --- 레이아웃 ---
        self.main_vbox = QVBoxLayout()
        self.setLayout(self.main_vbox)

        # --- 위젯 ---
        # 1. 시간 표시 레이블
        self.time_label = RotatableLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont('Arial', 60, QFont.Bold))

        # 2. 시간 프리셋 버튼
        self.presets_hbox = QHBoxLayout()
        for t in [5, 10, 20]:
            btn = QPushButton(f'{t}분')
            btn.clicked.connect(lambda _, m=t: self.set_preset_time(m))
            self.presets_hbox.addWidget(btn)

        # 3. 제어 버튼
        self.controls_hbox = QHBoxLayout()
        self.start_btn = QPushButton('시작')
        self.pause_continue_btn = QPushButton('일시정지')
        self.delete_btn = QPushButton('삭제')
        
        self.controls_hbox.addWidget(self.start_btn)
        self.controls_hbox.addWidget(self.pause_continue_btn)
        self.controls_hbox.addWidget(self.delete_btn)

        # 4. 알람 확인 버튼
        self.alarm_ok_btn = QPushButton('확인')

        # 5. 밝기 애니메이션을 위한 오버레이
        self.brightness_overlay = QWidget(self)
        self.brightness_overlay.setStyleSheet(f"background-color: rgba(255, 255, 255, 0);")
        self.brightness_overlay.hide()

        # --- 위젯 배치 ---
        time_label_hbox = QHBoxLayout()
        time_label_hbox.addStretch()
        time_label_hbox.addWidget(self.time_label)
        time_label_hbox.addStretch()

        self.main_vbox.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.main_vbox.addLayout(time_label_hbox) # 수정된 부분
        self.main_vbox.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.main_vbox.addLayout(self.presets_hbox)
        self.main_vbox.addLayout(self.controls_hbox)
        self.main_vbox.addWidget(self.alarm_ok_btn)
        
        # --- 시그널 연결 ---
        self.start_btn.clicked.connect(self.start_timer)
        self.pause_continue_btn.clicked.connect(self.toggle_pause)
        self.delete_btn.clicked.connect(self.reset_timer)
        self.alarm_ok_btn.clicked.connect(self.dismiss_alarm)

    def resizeEvent(self, event):
        """창 크기가 변경될 때 오버레이 크기도 조절"""
        self.brightness_overlay.resize(self.size())
        super().resizeEvent(event)

    # --- 상태 관리 ---
    def setup_initial_state(self):
        self.time_label.setText("00:00:00")
        self.countdown_time = QTime(0, 0, 0)
        
        for i in range(self.presets_hbox.count()):
            self.presets_hbox.itemAt(i).widget().show()
        
        self.start_btn.show()
        self.pause_continue_btn.hide()
        self.delete_btn.hide()
        self.alarm_ok_btn.hide()

    def setup_running_state(self):
        for i in range(self.presets_hbox.count()):
            self.presets_hbox.itemAt(i).widget().hide()
            
        self.start_btn.hide()
        self.pause_continue_btn.show()
        self.pause_continue_btn.setText('일시정지')
        self.delete_btn.show()
        self.alarm_ok_btn.hide()

    def setup_alarm_state(self):
        for i in range(self.controls_hbox.count()):
            self.controls_hbox.itemAt(i).widget().hide()
        self.alarm_ok_btn.show()

    # --- 슬롯 함수 ---
    def set_preset_time(self, minutes):
        if not self.is_running:
            self.countdown_time = QTime(0, minutes, 0)
            self.time_label.setText(self.countdown_time.toString("mm:ss"))

    def start_timer(self):
        if self.countdown_time > QTime(0, 0, 0):
            self.is_running = True
            self.main_timer.start(1000)
            self.setup_running_state()

    def toggle_pause(self):
        if self.is_running:
            self.main_timer.stop()
            self.is_running = False
            self.pause_continue_btn.setText('계속')
        else:
            self.main_timer.start(1000)
            self.is_running = True
            self.pause_continue_btn.setText('일시정지')

    def reset_timer(self):
        self.main_timer.stop()
        self.is_running = False
        self.setup_initial_state()

    def update_countdown(self):
        self.countdown_time = self.countdown_time.addSecs(-1)
        self.time_label.setText(self.countdown_time.toString("mm:ss"))
        if self.countdown_time == QTime(0, 0, 0):
            self.trigger_alarm()

    def trigger_alarm(self):
        self.main_timer.stop()
        self.is_running = False
        self.setup_alarm_state()
        QApplication.beep()
        self.brightness_overlay.show()
        self.alarm_animation_timer.start(50) # 50ms 간격으로 애니메이션

    def animate_alarm(self):
        # 1. 밝기 애니메이션
        current_alpha = self.brightness_overlay.styleSheet().split(',')[3].replace(');','').strip()
        alpha = int(current_alpha)

        if alpha >= 80: self.alarm_brightness_direction = -1
        if alpha <= 0: self.alarm_brightness_direction = 1

        # 속도를 약 3배 증가시킵니다. (10 -> 30)
        alpha += 30 * self.alarm_brightness_direction
        self.brightness_overlay.setStyleSheet(f"background-color: rgba(255, 255, 255, {alpha});")

        # 2. 회전 애니메이션
        angle = self.time_label.rotation_angle
        if angle > 15: self.alarm_angle_direction = -1
        if angle < -15: self.alarm_angle_direction = 1

        # 속도를 3배 증가시킵니다. (3 -> 9)
        angle += 9 * self.alarm_angle_direction
        self.time_label.setRotation(angle)

        # 3. 비프음 반복 (중앙 근처에서 울리도록 조건 변경)
        if abs(angle) < 9:
            QApplication.beep()

    def dismiss_alarm(self):
        self.alarm_animation_timer.stop()
        self.brightness_overlay.hide()
        self.time_label.setRotation(0)
        self.reset_timer()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FinalTimerApp()
    ex.show()
    sys.exit(app.exec_())
