from full_screen import FullScreenDemo
from calendar import CalendarEditor, Calendar
from schedule import Planner
from settings import Settings
import datetime
import os
import pickle
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMenu, QMessageBox, QWidget
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
        self.setWindowIcon(QtGui.QIcon("images/cms.png"))

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

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

        # Layout
        layout = QHBoxLayout(self)
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        self.setLayout(layout)

        # Window Settings
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        setWindow(self, WINDOW_WIDTH, RIGHT_INTERVAL)

        # Background
        p = QtGui.QPalette()
        p.setColor(QtGui.QPalette.Background, QtGui.QColor(255, 255, 255, 0))
        self.setPalette(p)

        # Initialize data
        self.initCalendar()
        self.initAlarms()
        self.initSchedule()
        self.initSettings()
        self.initColor()
        self.update()

        # Right Click Menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
        self.contextMenu = None

        # Update Timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def warning(self, str1, str2):
        self.message = QMessageBox(QMessageBox.Warning, str1, str2)
        self.message.setWindowIcon(QtGui.QIcon("images/cms.png"))
        self.message.setModal(False)
        self.message.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint)
        self.message.show()

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
        self.state = True  # True????????????
        self.end_time = datetime.time(0, 0, 0)

    def initSettings(self):
        self.settings = Settings()
        self.settings.loadFile("settings.dat")

    def initColor(self):
        self.colorSet = COLORSETS[self.settings.darkmode]
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

        # TODO: what is this for? check 24:00
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
                self.label2.setText((datetime.datetime.now() +
                                     datetime.timedelta(minutes=5)).strftime("%H:%M"))
                self.label1.setText("Over")
                self.label1.setStyleSheet("color:%s" % self.colorSet[1])
                t = self.warning("Task Ends",
                                 "Today's work is over.\nHave a rest.")

                if self.settings.shutdown:
                    os.system("shutdown /s /t 300")

        # print(now.strftime("%H:%M:%S"))

    def showMenu(self):
        if (not self.contextMenu):
            self.contextMenu = QMenu()

        self.contextMenu.clear()
        menuActions = list()
        menuActions.append(self.contextMenu.addAction("Edit the schedule"))
        menuActions.append(self.contextMenu.addAction("View the calendar"))
        self.contextMenu.addSeparator()
        menuActions.append(self.contextMenu.addAction("Fullscreen"))
        menuActions.append(self.contextMenu.addAction(
            "Shutdown ON" if self.settings.shutdown else "Shutdown OFF"))
        self.contextMenu.addSeparator()
        menuActions.append(self.contextMenu.addAction("Version 4.0"))
        self.contextMenu.addSeparator()
        menuActions.append(self.contextMenu.addAction("Load Data"))
        menuActions.append(self.contextMenu.addAction(
            "Dark Mode" if self.settings.darkmode else "Bright Mode"))
        menuActions.append(self.contextMenu.addAction("Exit"))
        self.contextMenu.popup(QtGui.QCursor.pos())

        menuActions[0].triggered.connect(self.edit_schedule)
        menuActions[1].triggered.connect(self.view_calendar)
        # menuActions[2].triggered.connect(self.full_screen)
        menuActions[2].setEnabled(False)
        menuActions[3].triggered.connect(self.change_shutdown)
        menuActions[4].setEnabled(False)
        menuActions[5].triggered.connect(self.load)
        menuActions[6].triggered.connect(self.change_color)
        menuActions[7].triggered.connect(self.close)

        try:
            # self.contextMenu.show()
            self.contextMenu.exec(QtGui.QCursor.pos())
        except Exception as e:
            print(e)

    def edit_schedule(self):
        self.planner = Planner()
        self.planner.closingSignal.connect(self.load)
        self.planner.show()

    def view_calendar(self):
        self.editor = CalendarEditor()
        self.editor.closingSignal.connect(self.load)
        self.editor.show()

    def full_screen(self):
        if not self.state:
            result = QMessageBox.warning(self, "During a break", "Are you sure about fullscreen during a break?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if result == QMessageBox.StandardButton.No:
                return
        FullScreenDemo(self, self.end_time)

    def change_shutdown(self):
        self.settings.shutdown = 1 - self.settings.shutdown
        self.update()
        self.settings.dumpFile("settings.dat")

    def load(self):
        self.initCalendar()
        self.initAlarms()
        self.initSchedule()
        self.initSettings()
        self.update()

    def change_color(self):
        self.settings.darkmode = 1 - self.settings.darkmode
        self.initColor()
        self.update()
        self.settings.dumpFile("settings.dat")

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.settings.dumpFile("settings.dat")
        resetWindow(self, RIGHT_INTERVAL)
        return super().closeEvent(a0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    d = DisplayWindow()
    d.show()
    sys.exit(app.exec_())
