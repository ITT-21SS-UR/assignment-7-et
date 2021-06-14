from DIPPID import SensorUDP
import sys
import random
from enum import Enum
from PyQt5 import QtWidgets, QtCore, Qt, QtGui
from PyQt5.QtCore import QTimer


class ApplicationState(Enum):
    EXPLANATION = 1
    GAME = 2
    FINISHED = 3


class FirstGame(QtWidgets.QWidget):
    PORT = int(sys.argv[1])
    SCREEN_START = 0
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    SPACESHIP_DIM = 40
    TARGET_DIM = 60
    TARGET_MIN_HEIGHT = 600
    TARGETS_NUM = 3
    SPACESHIP_Y = (int(SCREEN_HEIGHT) - int(SPACESHIP_DIM))

    spaceship_x = (SCREEN_WIDTH / 2)
    sensor = ()
    targets_x = []
    targets_y = []
    application_state = ()
    targets_printed = ()

    def __init__(self):
        super().__init__()
        self.application_state = ApplicationState.EXPLANATION
        self.sensor = SensorUDP(self.PORT)
        self.sensor.register_callback('button_1', self.handle_button_press)
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_spaceship)
        self.timer.start(10)
        self.show()

    def handle_button_press(self, data):
        if int(data) == 0:
            print('button released')
            return
        else:
            print('button pressed')
            if self.application_state == ApplicationState.EXPLANATION:
                self.application_state = ApplicationState.GAME

            if self.application_state == ApplicationState.FINISHED:
                self.application_state = ApplicationState.GAME
        self.update()

    def initUI(self):
        self.setGeometry(self.SCREEN_START, self.SCREEN_START, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.setWindowTitle('DIPPID Game')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        if self.application_state == ApplicationState.EXPLANATION:
            painter.setPen(QtCore.Qt.black)
            painter.setFont(Qt.QFont('Decorative', 30))
            painter.drawText(event.rect(), QtCore.Qt.AlignCenter,
                             "Get ready to play!\n Tilt your phone to move the spaceship \n Press button 1 to shoot\n\n"
                             "Press button 1 when you are ready to start!")
            return

        if self.application_state == ApplicationState.FINISHED:
            painter.setPen(QtCore.Qt.black)
            painter.setFont(Qt.QFont('Decorative', 30))
            painter.drawText(event.rect(), QtCore.Qt.AlignCenter,
                             "THE END\n\n"
                             "To start again press button 1")
            return

        self.draw_spaceship(painter)
        self.draw_targets(painter)

    def draw_targets(self, painter):
        if not self.targets_printed:
            for i in range(self.TARGETS_NUM):
                self.targets_x.append(random.randint(0, int(self.SCREEN_WIDTH) - int(self.TARGET_DIM)))
                self.targets_y.append(random.randint(0, int(self.TARGET_MIN_HEIGHT)))
                self.targets_printed = True

        painter.setPen(Qt.QPen(QtCore.Qt.darkBlue, 2, QtCore.Qt.SolidLine))
        painter.setBrush(Qt.QBrush(QtCore.Qt.red))
        for i in range(self.TARGETS_NUM):
            painter.drawRect(int(self.targets_x[i]), int(self.targets_y[i]), int(self.TARGET_DIM), int(self.TARGET_DIM))

    def draw_spaceship(self, painter):
        painter.setPen(Qt.QPen(QtCore.Qt.darkBlue, 2, QtCore.Qt.SolidLine))
        painter.setBrush(Qt.QBrush(QtCore.Qt.blue))
        painter.drawRect(int(self.spaceship_x), int(self.SPACESHIP_Y), int(self.SPACESHIP_DIM), int(self.SPACESHIP_DIM))

    def move_spaceship(self):
        if self.sensor.has_capability('gravity'):
            sensor_value = self.sensor.get_value('gravity')['x']
            new_x_pos = self.spaceship_x - int(sensor_value)
            if (new_x_pos > 0) and (new_x_pos < (self.SCREEN_WIDTH - self.SPACESHIP_DIM)):
                self.spaceship_x = new_x_pos

        self.update()


def main():
    app = QtWidgets.QApplication(sys.argv)
    game = FirstGame()

    if len(sys.argv) < 2:
        sys.stdout.write("Need a port number. E.g. 5700")
        sys.exit(1)
    elif len(sys.argv) > 2:
        sys.stdout.write("Only one port number necessary")
        sys.exit(1)
    else:
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
