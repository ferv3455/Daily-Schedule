import pickle
import datetime
import sys
from day import Day

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QButtonGroup, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QRadioButton, QSizePolicy, QSpacerItem, QSpinBox, QTextEdit, QVBoxLayout, QWidget

# from tkinter import Toplevel, Frame, Button, Label, LEFT, RIGHT, IntVar, \
#         StringVar, Text, Radiobutton, Entry, font, W, X, END
# from tkinter.messagebox import showwarning

class Calendar:
    def __init__(self):
        self.marked_days = dict()

    def add_day(self, dateobj):
        key = self.create_key(dateobj.year, dateobj.month, dateobj.day)
        self.marked_days[key] = Day(dateobj)

    def get_day(self, dateobj):
        key = self.create_key(dateobj.year, dateobj.month, dateobj.day)
        if key in self.marked_days:
            return self.marked_days[key]
        else:
            return None

    def del_day(self, dateidx):
        del self.marked_days[dateidx]

    def create_key(self, y, m, d):
        return y * 1000 + m * 100 + d

    def __iter__(self):
        return iter(self.marked_days)


class CalendarEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        mainFont = QtGui.QFont("Microsoft YaHei", 10, QtGui.QFont.Weight.Normal)
        titleFont = QtGui.QFont("Consolas", 18, QtGui.QFont.Weight.Bold)
        subtitleFont = QtGui.QFont("Calibri", 14, QtGui.QFont.Weight.Bold)

        # Initialize window
        self.setWindowTitle("Calendar Editor")
        self.setWindowIcon(QtGui.QIcon("images/cms.png"))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowState(QtCore.Qt.WindowState.WindowMaximized)

        # Load data
        with open("calendar.dat", "rb") as fin:
            self.calendar = pickle.load(fin)

        self.current_date = datetime.date.today()
        self.day_delta = datetime.timedelta(1)

        # Window Layout
        mainLayout = QVBoxLayout(self)
        self.setLayout(mainLayout)

        ## Title
        titleFrame = QFrame(self)
        mainLayout.addWidget(titleFrame)
        titleLayout = QHBoxLayout(titleFrame)
        titleFrame.setLayout(titleLayout)

        icon = QtGui.QIcon("images/left-arrows.png")
        bt_previous = QPushButton(icon, " &Previous ", titleFrame)
        bt_previous.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        icon = QtGui.QIcon("images/right-arrows.png")
        bt_forward = QPushButton(icon, " &Next ", titleFrame)
        bt_forward.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        bt_forward.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        bt_previous.setFont(subtitleFont)
        bt_forward.setFont(subtitleFont)
        lb_title = QLabel("Calendar", titleFrame)
        lb_title.setFont(titleFont)

        titleLayout.addWidget(bt_previous)
        titleLayout.addItem(QSpacerItem(20, 20, 
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred))
        titleLayout.addWidget(lb_title)
        titleLayout.addItem(QSpacerItem(20, 20, 
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred))
        titleLayout.addWidget(bt_forward)

        bt_previous.clicked.connect(self.backward)
        bt_forward.clicked.connect(self.forward)


        ## Calendar Area
        calendarFrame = QFrame(self)
        mainLayout.addWidget(calendarFrame)
        calendarLayout = QGridLayout(calendarFrame)
        calendarLayout.setSpacing(0)
        calendarFrame.setLayout(calendarLayout)
        calendarFrame.setStyleSheet('''QRadioButton::indicator::unchecked {
            image: url(./images/up-arrow.png);
        }
        QRadioButton::indicator::unchecked:hover {
            image: url(./images/up-arrow (1).png);
        }
        QRadioButton::indicator::unchecked:pressed {
            image: url(./images/up-arrow (3).png);
        }
        QRadioButton::indicator::checked {
            image: url(./images/up-arrow (2).png);
        }
        ''')

        self.day_labels = list()
        self.day_alarms = list()
        self.day_remarks = list()
        self.select_buttons = QButtonGroup(calendarFrame)
        self.select_buttons.setExclusive(True)

        for i in range(8):
            # Date Label
            label = QLabel(calendarFrame)
            label.setFont(mainFont)
            self.day_labels.append(label)
            calendarLayout.addWidget(label, 0, i)
            calendarLayout.setAlignment(label, QtCore.Qt.AlignmentFlag.AlignCenter)

            # Alarm text edit
            alarmEdit = QTextEdit(calendarFrame)
            alarmEdit.setFont(mainFont)
            alarmEdit.setReadOnly(True)
            self.day_alarms.append(alarmEdit)
            calendarLayout.addWidget(alarmEdit, 1, i)

            # Remarks text edit
            remarksEdit = QTextEdit(calendarFrame)
            remarksEdit.setFont(mainFont)
            remarksEdit.setReadOnly(True)
            self.day_remarks.append(remarksEdit)
            calendarLayout.addWidget(remarksEdit, 2, i)

            # Select button
            button = QRadioButton(calendarFrame)
            button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self.select_buttons.addButton(button, i - 1)
            calendarLayout.addWidget(button, 3, i)
            calendarLayout.setAlignment(button, QtCore.Qt.AlignmentFlag.AlignCenter)

        calendarLayout.setRowStretch(1, 1)
        calendarLayout.setRowStretch(2, 2)

        self.select_buttons.idClicked.connect(self.reset_date_input)
        self.select_buttons.button(0).setChecked(True)

        ## Editting area
        editFrame = QFrame(self)
        editFrame.setFont(mainFont)
        mainLayout.addWidget(editFrame)
        editLayout = QGridLayout(editFrame)
        editFrame.setLayout(editLayout)

        ### Edit alarms
        alarmBox = QGroupBox("Edit Alarms", editFrame)
        alarmLayout = QGridLayout(alarmBox)
        alarmBox.setLayout(alarmLayout)
        editLayout.addWidget(alarmBox, 0, 0)

        self.addAlarmBoxes = list()
        for i in range(3):
            self.addAlarmBoxes.append(QSpinBox(alarmBox))
            alarmLayout.addWidget(self.addAlarmBoxes[-1], 0, i)
        self.addAlarmBoxes[0].setRange(0, 23)
        self.addAlarmBoxes[1].setRange(0, 59)
        self.addAlarmBoxes[2].setRange(0, 59)

        icon = QtGui.QIcon("images/plus.png")
        addAlarmButton = QPushButton(icon, "Add", alarmBox)
        addAlarmButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        addAlarmButton.clicked.connect(self.add_alarm)
        alarmLayout.addWidget(addAlarmButton, 0, 3)

        self.removeAlarmBox = QSpinBox(alarmBox)
        alarmLayout.addWidget(self.removeAlarmBox, 1, 1)

        icon = QtGui.QIcon("images/negative.png")
        removeAlarmButton = QPushButton(icon, "Del", alarmBox)
        removeAlarmButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        removeAlarmButton.clicked.connect(self.del_alarm)
        alarmLayout.addWidget(removeAlarmButton, 1, 3)

        ### Edit remarks
        remarkBox = QGroupBox("Edit Remarks", editFrame)
        remarkBox.setFixedWidth(400)
        remarkLayout = QGridLayout(remarkBox)
        remarkBox.setLayout(remarkLayout)
        editLayout.addWidget(remarkBox, 0, 1)

        self.newRemarkEdit = QLineEdit(remarkBox)
        remarkLayout.addWidget(self.newRemarkEdit, 0, 0, 1, 5)

        icon = QtGui.QIcon("images/plus.png")
        addRemarkButton = QPushButton(icon, "Add", remarkBox)
        addRemarkButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        addRemarkButton.clicked.connect(self.add_remark)
        remarkLayout.addWidget(addRemarkButton, 0, 5)

        icon = QtGui.QIcon("images/down.png")
        moveDownButton = QPushButton(icon, "&Down", remarkBox)
        moveDownButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        moveDownButton.clicked.connect(self.down_remark)
        remarkLayout.addWidget(moveDownButton, 1, 0)

        remarkLayout.addItem(QSpacerItem(20, 20, 
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred), 1, 1)

        self.removeRemarkBox = QSpinBox(remarkBox)
        remarkLayout.addWidget(self.removeRemarkBox, 1, 2)

        icon = QtGui.QIcon("images/negative.png")
        removeRemarkButton = QPushButton(icon, "Del", remarkBox)
        removeRemarkButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        removeRemarkButton.clicked.connect(self.del_remark)
        remarkLayout.addWidget(removeRemarkButton, 1, 3)

        remarkLayout.addItem(QSpacerItem(20, 20, 
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred), 1, 4)

        icon = QtGui.QIcon("images/up.png")
        addRemarkButton = QPushButton(icon, "&Up", remarkBox)
        addRemarkButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        addRemarkButton.clicked.connect(self.up_remark)
        remarkLayout.addWidget(addRemarkButton, 1, 5)

        ### Clear records
        clearBox = QGroupBox("Clear Records", editFrame)
        clearLayout = QGridLayout(clearBox)
        clearBox.setLayout(clearLayout)
        editLayout.addWidget(clearBox, 1, 0, 1, 2)

        clearLayout.addItem(QSpacerItem(20, 20, 
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred), 0, 0)

        self.clearRecordBoxes = list()
        for i in range(2):
            for j in range(3):
                self.clearRecordBoxes.append(QSpinBox(clearBox))
                clearLayout.addWidget(self.clearRecordBoxes[-1], i, 2 * j + 1)
        
        self.clearRecordBoxes[0].setRange(0, 3000)
        self.clearRecordBoxes[1].setRange(1, 12)
        self.clearRecordBoxes[2].setRange(1, 31)
        self.clearRecordBoxes[3].setRange(0, 3000)
        self.clearRecordBoxes[4].setRange(1, 12)
        self.clearRecordBoxes[5].setRange(1, 31)

        for i in range(2):
            for j in range(2):
                clearLayout.addWidget(QLabel("/", clearBox), i, 2 * j + 2)

        icon = QtGui.QIcon("images/delete.png")
        clearButton = QPushButton(icon, "Keep these days\n&Clear the rest", alarmBox)
        clearButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        clearButton.clicked.connect(self.clear_days)
        clearLayout.addWidget(clearButton, 0, 7, 2, 1)

        clearLayout.addItem(QSpacerItem(20, 20, 
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred), 0, 8)

        ### Edit memo
        memoBox = QGroupBox("Edit Memo", editFrame)
        memoLayout = QGridLayout(memoBox)
        memoBox.setLayout(memoLayout)
        editLayout.addWidget(memoBox, 0, 2, 2, 1)

        self.memoEdit = QTextEdit(memoBox)
        self.memoEdit.setFont(mainFont)
        memoLayout.addWidget(self.memoEdit)

        # Load memo
        with open("remarks.dat", "r") as fin:
            content = fin.read()
            self.memoEdit.insertPlainText(content)

        # Initialize input boxes
        self.reset_clear_date_entry()
        self.reset_date_input()
        self.update_screen()

    def backward(self):
        self.current_date -= self.day_delta
        self.update_screen()

    def forward(self):
        self.current_date += self.day_delta
        self.update_screen()

    def add_alarm(self, event=None):
        date = self.current_date + self.select_buttons.checkedId() * self.day_delta
        date_obj = self.calendar.get_day(date)
        if not date_obj:
            self.calendar.add_day(date)
            date_obj = self.calendar.get_day(date)

        date_obj.add_alarm(self.addAlarmBoxes[0].value(), 
                           self.addAlarmBoxes[1].value(), 
                           self.addAlarmBoxes[2].value())
        date_obj.sort_alarm()
        self.update_column(self.select_buttons.checkedId() + 1, 1)
        
        for i in range(3):
            self.addAlarmBoxes[i].setValue(0)
        self.reset_date_input()

    def del_alarm(self, event=None):
        date = self.current_date + self.select_buttons.checkedId() * self.day_delta
        date_obj = self.calendar.get_day(date)
        try:
            date_obj.remove_alarm(self.removeAlarmBox.value())
        except:
            self.warning("Warning", "Index out of range!")
        self.update_column(self.select_buttons.checkedId() + 1, 1)
        self.reset_date_input()

    # def func_decide(self, event):
    #     if event.keysym == "Return":
    #         self.del_remark()
    #     elif event.keycode == 38:
    #         self.up_remark()
    #     elif event.keycode == 40:
    #         self.down_remark()

    def add_remark(self, event=None):
        date = self.current_date + self.select_buttons.checkedId() * self.day_delta
        date_obj = self.calendar.get_day(date)
        if not date_obj:
            self.calendar.add_day(date)
            date_obj = self.calendar.get_day(date)

        date_obj.add_remark(self.newRemarkEdit.text())
        self.update_column(self.select_buttons.checkedId() + 1, 2)
        self.newRemarkEdit.setText("")
        self.reset_date_input()

    def del_remark(self, event=None):
        date = self.current_date + self.select_buttons.checkedId() * self.day_delta
        date_obj = self.calendar.get_day(date)
        try:
            date_obj.remove_remark(self.removeRemarkBox.value())
        except:
            self.warning("Warning", "Index out of range!")
        self.update_column(self.select_buttons.checkedId() + 1, 2)
        self.reset_date_input()

    def up_remark(self, event=None):
        date = self.current_date + self.select_buttons.checkedId() * self.day_delta
        date_obj = self.calendar.get_day(date)
        try:
            date_obj.switch_remark(self.removeRemarkBox.value(), self.removeRemarkBox.value() - 1)
            self.update_column(self.select_buttons.checkedId() + 1, 2)
            self.removeRemarkBox.setValue(self.removeRemarkBox.value() - 1)
        except:
            self.warning("Warning", "Index out of range!")
        

    def down_remark(self, event=None):
        date = self.current_date + self.select_buttons.checkedId() * self.day_delta
        date_obj = self.calendar.get_day(date)
        try:
            date_obj.switch_remark(self.removeRemarkBox.value(), self.removeRemarkBox.value() + 1)
            self.update_column(self.select_buttons.checkedId() + 1, 2)
            self.removeRemarkBox.setValue(self.removeRemarkBox.value() + 1)
        except:
            self.warning("Warning", "Index out of range!")
        
    def clear_days(self, event=None):
        self.clearRecordBoxes[0].value()
        begin_date = 1000 * self.clearRecordBoxes[0].value() + \
                100 * self.clearRecordBoxes[1].value() + \
                self.clearRecordBoxes[2].value()
        end_date = 1000 * self.clearRecordBoxes[3].value() + \
                100 * self.clearRecordBoxes[4].value() + \
                self.clearRecordBoxes[5].value()
        del_list = list()
        for day in self.calendar:
            if day < begin_date or day > end_date:
                del_list.append(day)
                
        for day in del_list:
            self.calendar.del_day(day)
        self.update_screen()

    def update_screen(self):
        for i in range(8):
            self.day_alarms[i].clear()
            self.day_remarks[i].clear()
            self.day_labels[i].setStyleSheet("background-color: transparent;")
            self.day_alarms[i].setStyleSheet("background-color: white;")
            self.day_remarks[i].setStyleSheet("background-color: white;")

        for i in range(8):
            date = self.current_date + (i - 1) * self.day_delta
            if date.weekday() > 4:
                self.day_labels[i].setStyleSheet("background-color: orchid;")
                self.day_alarms[i].setStyleSheet("background-color: lavender;")
                self.day_remarks[i].setStyleSheet("background-color: lavender;")
            if date == datetime.date.today():
                self.day_alarms[i].setStyleSheet("background-color: beige;")
                self.day_remarks[i].setStyleSheet("background-color: beige;")
            
            self.day_labels[i].setText(date.strftime("%m/%d(%a)"))
            date_obj = self.calendar.get_day(date)
            if date_obj:
                cursor_alarms = self.day_alarms[i].textCursor()
                for index, alarm in enumerate(date_obj.alarms, 1):
                    alarm_time = alarm.isoformat()
                    cursor_alarms.insertText("{:2d}  ".format(index) + alarm_time + "\n")

                cursor_remarks = self.day_remarks[i].textCursor()
                for index, remark in enumerate(date_obj.remarks, 1):
                    cursor_remarks.insertText("{:2d}  ".format(index) + remark + "\n")

        self.reset_date_input()

    def reset_clear_date_entry(self):
        date = datetime.datetime.today() - datetime.timedelta(days=1)
        self.clearRecordBoxes[0].setValue(date.year)
        self.clearRecordBoxes[1].setValue(date.month)
        self.clearRecordBoxes[2].setValue(date.day)
        self.clearRecordBoxes[3].setValue(2049)
        self.clearRecordBoxes[4].setValue(12)
        self.clearRecordBoxes[5].setValue(31)

    def reset_date_input(self):
        date = self.current_date + self.select_buttons.checkedId() * self.day_delta
        date_obj = self.calendar.get_day(date)
        if date_obj:
            self.removeAlarmBox.setRange(1, len(date_obj.alarms))
            self.removeRemarkBox.setRange(1, len(date_obj.remarks))
    
    def update_column(self, idx, row):
        if row == 1:
            self.day_alarms[idx].clear()
            date = self.current_date + (idx - 1) * self.day_delta
            date_obj = self.calendar.get_day(date)
            if date_obj:
                cursor = self.day_alarms[idx].textCursor()
                for index, alarm in enumerate(date_obj.alarms, 1):
                    alarm_time = alarm.isoformat()
                    cursor.insertText("{:2d}  ".format(index) + alarm_time + "\n")

        else:
            self.day_remarks[idx].clear()
            date = self.current_date + (idx - 1) * self.day_delta
            date_obj = self.calendar.get_day(date)
            if date_obj:
                cursor = self.day_remarks[idx].textCursor()
                for index, remark in enumerate(date_obj.remarks, 1):
                    cursor.insertText("{:2d}  ".format(index) + remark + "\n")

    def warning(self, str1, str2):
        self.message = QMessageBox(QMessageBox.Warning, str1, str2)
        self.message.setWindowIcon(QtGui.QIcon("cms.png"))
        self.message.setModal(False)
        self.message.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint)
        self.message.show()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        with open("calendar.dat", "wb") as fout:
            pickle.dump(self.calendar, fout)
            
        content = self.memoEdit.toPlainText().strip()
        with open("remarks.dat", "w") as fout:
            fout.write(content)

        self.warning("Warning", "Please reload data \nif the calendar has been edited! ")
        return super().closeEvent(a0)


if __name__ == "__main__":
    # c = Calendar()
    # c.add_day(datetime.date.today())
    # d = c.get_day(datetime.date.today())
    # d.add_alarm(15, 40, 00)
    # d.add_alarm(16, 00, 00)
    # d.add_remark("Hello!")
    # d.add_remark("哈哈")
    # with open("calendar.dat", "wb") as fout:
    #     pickle.dump(c, fout)

    app = QApplication(sys.argv)
    d = CalendarEditor(None)
    d.show()
    sys.exit(app.exec_())

