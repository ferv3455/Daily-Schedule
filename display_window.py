from calendar import CalendarEditor
from full_screen import FullScreenDemo
from schedule import Planner
from settings import Settings
import datetime
import os
import pickle
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QMenu, QMessageBox, QWidget
import win32gui
import sys

RIGHT_INTERVAL = 80
WINDOW_WIDTH = 80
WINDOW_WIDTH = 150
COLORSETS = [("#000000", "#CC0000", "#0033CC"),
             ("#f3f3f4", "#fc618d", "#0099FF")]


def setWindow(widget, width=150, right_intv=0):
    m_hTaskbar = win32gui.FindWindow("Shell_TrayWnd", None)
    m_hBar = win32gui.FindWindowEx(m_hTaskbar, 0, "ReBarWindow32", None)
    m_hMinBar = win32gui.FindWindowEx(m_hBar, 0, "MSTaskSwWClass", None)
    b = win32gui.GetWindowRect(m_hBar)
    win32gui.MoveWindow(
        m_hMinBar, 0, 0, b[2] - b[0] - width - right_intv, b[3] - b[1], True)
    widget.setGeometry(b[2] - b[0] - width - right_intv, 0, width, b[3] - b[1])
    win32gui.SetParent(int(widget.winId()), m_hBar)


def resetWindow(widget, right_intv=0):
    m_hTaskbar = win32gui.FindWindow("Shell_TrayWnd", None)
    m_hBar = win32gui.FindWindowEx(m_hTaskbar, 0, "ReBarWindow32", None)
    m_hMinBar = win32gui.FindWindowEx(m_hBar, 0, "MSTaskSwWClass", None)
    b = win32gui.GetWindowRect(m_hBar)
    win32gui.SetParent(int(widget.winId()), None)
    win32gui.MoveWindow(
        m_hMinBar, 0, 0, b[2] - b[0] - right_intv, b[3] - b[1], True)


class DisplayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello PyQt5")
        self.setWindowIcon(QtGui.QIcon("cms.png"))

        font = QtGui.QFont("Microsoft YaHei")
        font.setPointSize(12)

        # Label 1
        self.label1 = QLabel(self)
        self.label1.setText("Task")
        self.label1.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label1.setFont(font)

        # Label 2
        self.label2 = QLabel(self)
        self.label2.setText("11:00")
        self.label2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label2.setFont(font)

        # Window Settings
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        setWindow(self, WINDOW_WIDTH, RIGHT_INTERVAL)

        # self.label1.setGeometry(0, 0, WINDOW_WIDTH, int(self.height() / 2))
        # self.label2.setGeometry(0, int(self.height() / 2),
        #                         WINDOW_WIDTH, int(self.height() / 2))
        self.label1.setGeometry(0, 0, WINDOW_WIDTH // 2, self.height())
        self.label2.setGeometry(WINDOW_WIDTH // 2, 0,
                                WINDOW_WIDTH // 2, self.height())

        p = QtGui.QPalette()
        p.setColor(QtGui.QPalette.Background, QtGui.QColor(255, 255, 255, 0))
        self.setPalette(p)

        # Right Click Menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)

        self.initCalendar()
        self.initAlarms()
        self.initSchedule()
        self.initSettings()
        self.initColor()
        self.update()

        # Update Timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def warning(self, str1, str2):
        self.message = QMessageBox(QMessageBox.Warning, str1, str2)
        self.message.setWindowIcon(QtGui.QIcon("cms.png"))
        self.message.setModal(False)
        self.message.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint)
        self.message.show()

        # QMessageBox.warning(self, str1, str2)

    def initCalendar(self):
        with open("calendar.dat", "rb") as fin:
            self.calendar = pickle.load(fin)

        today_obj = self.calendar.get_day(datetime.date.today())
        if today_obj:
            self.alarms = today_obj.get_alarms()
        else:
            self.alarms = list()

    def initAlarms(self):
        self.current_alarm = 0
        if not self.alarms:
            self.current_alarm = -1
        else:
            now = datetime.datetime.now().time()
            while now > self.alarms[self.current_alarm]:
                self.current_alarm += 1
                if self.current_alarm >= len(self.alarms):
                    self.current_alarm = -1
                    break

    def initSchedule(self):
        with open("schedule.dat", "rb") as fin:
            self.schedule = pickle.load(fin)

        self.task_num = 0

        self.state = True  # True为任务中
        self.end_time = datetime.time(0, 0, 0)

    def initSettings(self):
        with open("settings.dat", "rb") as fin:
            self.settings = pickle.load(fin)

        self.shutdown = self.settings.shutdown
        self.darkmode = self.settings.darkmode

    def initColor(self):
        self.colorSet = COLORSETS[self.darkmode]
        self.label2.setStyleSheet("color:%s" % self.colorSet[0])
        if self.state:
            self.label1.setStyleSheet("color:%s" % self.colorSet[2])
        else:
            self.label1.setStyleSheet("color:%s" % self.colorSet[1])

    def update(self):
        now = datetime.datetime.now().time()

        # Alarm clock
        if self.current_alarm >= 0 and now > self.alarms[self.current_alarm]:
            t = self.warning("Alarm",
                             "Alarm Reminder: " + self.alarms[self.current_alarm].isoformat())

            self.current_alarm += 1
            if self.current_alarm >= len(self.alarms):
                self.current_alarm = -1

        # TODO: what is this for?
        if (now.hour, now.minute) == (0, 0) and now.second < 3:
            self.end_time = datetime.time(0, 0, 0)

        if now > self.end_time:
            flag = True         # False: day over
            while now > self.schedule[self.task_num][1]:
                self.task_num += 1
                if self.task_num == len(self.schedule):
                    flag = False
                    break
            if flag:            # mid-day
                self.state = now >= self.schedule[self.task_num][0]
                if self.state:      # during a task
                    self.end_time = self.schedule[self.task_num][1]
                    self.label1.setText("Task")
                    self.label1.setStyleSheet("color:%s" % self.colorSet[2])
                    t = self.warning("Task Begins",
                                     "Rest is over.\nReturn to work.")

                else:               # during a break
                    self.end_time = self.schedule[self.task_num][0]
                    self.label1.setText("Rest")
                    self.label1.setStyleSheet("color:%s" % self.colorSet[1])
                    t = self.warning("Task Ends",
                                     "This period is over.\nHave a rest.")

                self.label2.setText(self.end_time.strftime("%H:%M"))

            else:               # tasks over
                self.end_time = datetime.time(23, 59, 59)
                # self.v2.set((datetime.datetime.now() +
                #              datetime.timedelta(minutes=5)).strftime("%H:%M:%S"))
                self.label1.setText("All tasks over")
                self.label1.setStyleSheet("color:%s" % self.colorSet[1])
                t = self.warning("Task Ends",
                                 "Today's work is over.\nHave a rest.")

                if self.shutdown:
                    os.system("shutdown /s /t 300")

        # print(now.strftime("%H:%M:%S"))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        resetWindow(self, RIGHT_INTERVAL)
        return super().closeEvent(a0)

    # def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
    #     self.close()
    #     return super().mousePressEvent(a0)

    def showMenu(self):
        try:
            self.contextMenu = QMenu()
            self.actionA = self.contextMenu.addAction("Edit the schedule")
            self.actionB = self.contextMenu.addAction("View the calendar")
            self.contextMenu.addSeparator()
            self.actionC = self.contextMenu.addAction("Fullscreen")
            self.actionD = self.contextMenu.addAction("Scheduled Shutdown")
            self.contextMenu.addSeparator()
            self.actionE = self.contextMenu.addAction("Version 4.0")
            self.contextMenu.addSeparator()
            self.actionF = self.contextMenu.addAction("Load Data")
            self.actionG = self.contextMenu.addAction(
                "Bright Mode" if self.darkmode else "Dark Mode")
            self.actionH = self.contextMenu.addAction("Exit")
            self.contextMenu.popup(QtGui.QCursor.pos())

            self.actionA.triggered.connect(self.edit_schedule)
            self.actionB.triggered.connect(self.view_calendar)
            self.actionC.triggered.connect(self.full_screen)
            self.actionF.triggered.connect(self.load)
            self.actionG.triggered.connect(self.change_color)
            self.actionH.triggered.connect(self.close)
            self.contextMenu.show()

        except Exception as e:
            print(e)

    def edit_schedule(self):
        Planner(self)

    def view_calendar(self):
        CalendarEditor(self)

    def full_screen(self):
        if not self.state:
            result = QMessageBox.warning(self, "During a break", "Are you sure about fullscreen during a break?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if result == QMessageBox.StandardButton.No:
                return
        FullScreenDemo(self, self.end_time)

    def load(self):
        self.initCalendar()
        self.initAlarms()
        self.initSchedule()
        self.initSettings()
        self.update()

    def change_color(self):
        self.darkmode = 1 - self.darkmode
        self.initColor()
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    d = DisplayWindow()
    d.show()
    sys.exit(app.exec_())
