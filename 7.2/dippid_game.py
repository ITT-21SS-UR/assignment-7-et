from DIPPID import SensorUDP
import sys
from enum import Enum
from PyQt5 import QtWidgets, QtCore, Qt, QtGui


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
    SPACESHIP_Y = (int(SCREEN_HEIGHT) - int(SPACESHIP_DIM))

    spaceship_x = (SCREEN_WIDTH / 2)
    sensor = ()

    def __init__(self):
        super().__init__()
        self.application_state = ApplicationState.EXPLANATION
        self.sensor = SensorUDP(self.PORT)
        self.initUI()
        self.show()

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

    def draw_spaceship(self, painter):
        painter.setPen(Qt.QPen(QtCore.Qt.darkBlue, 2, QtCore.Qt.SolidLine))
        painter.setBrush(Qt.QBrush(QtCore.Qt.blue))
        painter.drawRect(int(self.spaceship_x), int(self.SPACESHIP_Y), int(self.SPACESHIP_DIM), int(self.SPACESHIP_DIM))

    def moveSpaceship(self):
        if self.sensor.has_capability('accelerometer'):
            accelerometer = self.sensor.get_value('accelerometer')['x']
            self.spaceship_x = (self.spaceship_x - int(accelerometer)*10)


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
