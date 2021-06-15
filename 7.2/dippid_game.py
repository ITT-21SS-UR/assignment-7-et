from DIPPID import SensorUDP
import sys
import random
from enum import Enum
from PyQt5 import QtWidgets, QtCore, Qt, QtGui
from PyQt5.QtCore import QTimer


# Authors: ev, tg
# equal workload distribution

# Enum class with game states
class ApplicationState(Enum):
    EXPLANATION = 1
    GAME = 2
    FINISHED = 3


class FirstGame(QtWidgets.QWidget):
    # constants
    PORT = int(sys.argv[1])
    SCREEN_START = 0
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    SPACESHIP_DIM = 40
    SPACESHIP_Y = (int(SCREEN_HEIGHT) - int(SPACESHIP_DIM))
    TARGET_DIM = 60
    TARGET_MIN_HEIGHT = 600
    TARGETS_NUM = 7
    BULLET_DIM = 10

    # variables
    spaceship_x = (SCREEN_WIDTH / 2)
    sensor = ()
    targets_x = []
    targets_y = []
    bullets_x = []
    bullets_y = []
    target_counter = TARGETS_NUM
    bullet_counter = 0
    targets_printed = False

    def __init__(self):
        super().__init__()
        self.application_state = ApplicationState.EXPLANATION
        self.sensor = SensorUDP(self.PORT)
        self.sensor.register_callback('button_1', self.handle_button_press1)
        self.sensor.register_callback('button_2', self.handle_button_press2)
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.handle_elements)
        self.timer.start(10)
        self.show()

    # handles button press 1 according to the application state
    def handle_button_press1(self, data):
        if int(data) == 0:
            return

        else:
            if self.application_state == ApplicationState.EXPLANATION:
                self.application_state = ApplicationState.GAME

            if self.application_state == ApplicationState.FINISHED:
                self.application_state = ApplicationState.EXPLANATION

        self.update()

    # handles button press 2 aka shooting bullets
    def handle_button_press2(self, data):
        if int(data) == 0:
            return

        else:
            if self.application_state == ApplicationState.GAME:
                self.bullets_x.append(self.spaceship_x + (self.SPACESHIP_DIM / 2))
                self.bullets_y.append(self.SPACESHIP_Y)
                self.bullet_counter = self.bullet_counter + 1

        self.update()

    def init_ui(self):
        self.setGeometry(self.SCREEN_START, self.SCREEN_START, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.setWindowTitle('DIPPID Game')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    # draw elements according to application state
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtCore.Qt.black)
        painter.setFont(Qt.QFont('Decorative', 30))

        if self.application_state == ApplicationState.EXPLANATION:
            painter.drawText(event.rect(), QtCore.Qt.AlignCenter,
                             "Get ready to play!\n\n By tilting your phone sideways \n you "
                             "can control the spaceship, \n by pressing button 2 you can shoot!\n\n"
                             "Press button 1 when you are ready to start!")
            self.bullet_counter = 0
            return

        if self.application_state == ApplicationState.FINISHED:
            painter.drawText(event.rect(), QtCore.Qt.AlignCenter,
                             "THE END\n\n"
                             "You needed " + str(self.bullet_counter) + " shots\n"
                                                                        "To start again press button 1")
            return

        self.draw_spaceship(painter)
        self.draw_targets(painter)
        self.draw_bullets(painter)
        self.draw_status(painter)

    # draw the targets with random location
    def draw_targets(self, painter):
        if not self.targets_printed:
            for i in range(self.TARGETS_NUM):
                self.targets_x.append(random.randint(0, int(self.SCREEN_WIDTH) - int(self.TARGET_DIM)))
                self.targets_y.append(random.randint(100, int(self.TARGET_MIN_HEIGHT)))
                self.targets_printed = True

        painter.setPen(Qt.QPen(QtCore.Qt.darkRed, 0, QtCore.Qt.SolidLine))
        painter.setBrush(Qt.QBrush(QtCore.Qt.red))
        for i in range(self.target_counter):
            painter.drawRect(int(self.targets_x[i]), int(self.targets_y[i]), int(self.TARGET_DIM), int(self.TARGET_DIM))

    # draw the spaceship at the bottom of the window
    def draw_spaceship(self, painter):
        painter.setPen(Qt.QPen(QtCore.Qt.darkBlue, 2, QtCore.Qt.SolidLine))
        painter.setBrush(Qt.QBrush(QtCore.Qt.blue))
        painter.drawRect(int(self.spaceship_x), int(self.SPACESHIP_Y), int(self.SPACESHIP_DIM), int(self.SPACESHIP_DIM))

    # draw bullets with the actual spaceship position as start position
    def draw_bullets(self, painter):
        painter.setPen(Qt.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine))
        painter.setBrush(Qt.QBrush(QtCore.Qt.black))
        for i in range(len(self.bullets_x)):
            painter.drawEllipse(int(self.bullets_x[i]), int(self.bullets_y[i]), int(self.BULLET_DIM),
                                int(self.BULLET_DIM))

    # draw status text
    def draw_status(self, painter):
        painter.setPen(QtCore.Qt.black)
        painter.setFont(Qt.QFont('Decorative', 24))
        textbox = QtCore.QRect(5, 5, self.SCREEN_WIDTH, 100)
        painter.drawText(textbox, QtCore.Qt.AlignLeft,
                         "Targets left: " + str(self.target_counter) + "\nBullets fired: " + str(self.bullet_counter))

    def handle_elements(self):
        self.move_spaceship()
        self.move_bullets()
        self.check_collision()

    # move spaceship with tilting of the phone
    def move_spaceship(self):
        if self.sensor.has_capability('gravity'):
            sensor_value = self.sensor.get_value('gravity')['x']
            new_x_pos = self.spaceship_x - int(sensor_value)
            if (new_x_pos > 0) and (new_x_pos < (self.SCREEN_WIDTH - self.SPACESHIP_DIM)):
                self.spaceship_x = new_x_pos

        self.update()

    # move bullets with constant speed
    def move_bullets(self):
        for i in range(len(self.bullets_y)):
            self.bullets_y[i] = self.bullets_y[i] - 1

        self.update()

    # checks for collision between bullets and targets and eventually delete targets
    def check_collision(self):
        delete_targets_x = []
        delete_targets_y = []
        for i in range(len(self.bullets_y)):
            for j in range(len(self.targets_y)):
                if self.bullets_y[i] < (self.targets_y[j] + self.TARGET_DIM) and \
                        (self.targets_x[j] + self.TARGET_DIM) > self.bullets_x[i] > self.targets_x[j]:
                    self.target_counter = self.target_counter - 1
                    delete_targets_x.append(self.targets_x[j])
                    delete_targets_y.append(self.targets_y[j])

        for k in range(len(delete_targets_x)):
            self.targets_x.remove(delete_targets_x[k])

        for n in range(len(delete_targets_y)):
            self.targets_y.remove(delete_targets_y[n])

        if self.target_counter == 0:
            self.reset_game()

        self.update()

    # reset game and empty variables
    def reset_game(self):
        self.application_state = ApplicationState.FINISHED
        self.spaceship_x = (self.SCREEN_WIDTH / 2)
        self.targets_x = []
        self.targets_y = []
        self.bullets_x = []
        self.bullets_y = []
        self.target_counter = self.TARGETS_NUM
        self.targets_printed = False


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
