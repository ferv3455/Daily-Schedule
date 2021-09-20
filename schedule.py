import pickle
import datetime
import sys
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QGridLayout, QHBoxLayout, QLabel, QMessageBox, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QTextEdit, QWidget

class Planner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        with open("schedule.dat", "rb") as fin:
            self.schedule = pickle.load(fin)

        self.setWindowTitle("Planner")
        self.setWindowIcon(QtGui.QIcon("images/cms.png"))

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.setMinimumSize(500, 400)

        # Layout and widgets
        layout = QHBoxLayout(self)
        self.text = QTextEdit(self)
        self.text.setReadOnly(True)
        self.editWidget = QWidget(self)
        layout.addWidget(self.text, 3)
        layout.addWidget(self.editWidget, 1)
        self.setLayout(layout)

        editLayout = QGridLayout(self.editWidget)
        self.editWidget.setLayout(editLayout)

        labelIndex = QLabel("Delete Index: ", self)
        editLayout.addWidget(labelIndex, 0, 0, 1, 3)

        self.delBox = QSpinBox(self)
        self.delBox.setRange(1, len(self.schedule))
        editLayout.addWidget(self.delBox, 1, 0)
        delButton = QPushButton("&Delete", self)
        delButton.clicked.connect(self.delete)
        editLayout.addWidget(delButton, 1, 1, 1, 2)

        editLayout.addItem(QSpacerItem(20, 20, 
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding), 2, 0)

        self.addBoxes = list()
        for i in range(4, 7, 2):
            for j in range(3):
                self.addBoxes.append(QSpinBox(self))
                editLayout.addWidget(self.addBoxes[-1], i, j)

        self.addBoxes[0].setRange(0, 23)
        self.addBoxes[1].setRange(0, 59)
        self.addBoxes[2].setRange(0, 59)
        self.addBoxes[3].setRange(0, 23)
        self.addBoxes[4].setRange(0, 59)
        self.addBoxes[5].setRange(0, 59)

        beginLabel = QLabel("Add Begin: ", self)
        editLayout.addWidget(beginLabel, 3, 0, 1, 3)
        endLabel = QLabel("Add End: ", self)
        editLayout.addWidget(endLabel, 5, 0, 1, 3)

        addButton = QPushButton("&Add", self)
        addButton.clicked.connect(self.add)
        editLayout.addWidget(addButton, 7, 1, 1, 2)

        self.show_schedule()
        self.resetInputBoxes()

    def warning(self, str1, str2):
        self.message = QMessageBox(QMessageBox.Warning, str1, str2)
        self.message.setWindowIcon(QtGui.QIcon("cms.png"))
        self.message.setModal(False)
        self.message.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint)
        self.message.show()

    def show_schedule(self):
        self.text.clear()
        cursor = self.text.textCursor()
        for index, task in enumerate(self.schedule, 1):
            task_str = task[0].strftime(
                "%H:%M:%S") + " - " + task[1].strftime("%H:%M:%S")
            cursor.insertText("{:3d}  ".format(index) + task_str + "\n")

    def update_schedule(self):
        self.schedule.sort()
        with open("schedule.dat", "wb") as fout:
            pickle.dump(self.schedule, fout)

        self.delBox.setRange(1, len(self.schedule))

    def delete(self):
        if self.delBox.value() - 1 >= len(self.schedule) or self.delBox.value() - 1 < 0:
            self.warning("Warning", "Index out of range!")
            return
        del self.schedule[int(self.delBox.text()) - 1]
        self.update_schedule()
        self.show_schedule()
        self.resetInputBoxes()

    def add(self):
        d1 = datetime.time(self.addBoxes[0].value(), self.addBoxes[1].value(), self.addBoxes[2].value())
        d2 = datetime.time(self.addBoxes[3].value(), self.addBoxes[4].value(), self.addBoxes[5].value())
        if d1 >= d2:
            self.warning("Warning", "Task time not valid!")
            return
        if not self.valid_input(d1, d2):
            self.warning("Warning", "Overlapping existing tasks!")
            return
        self.schedule.append((d1, d2))
        self.update_schedule()
        self.show_schedule()
        self.resetInputBoxes()

    def valid_input(self, d1, d2):
        if not self.schedule:
            return True
        if d2 <= self.schedule[0][0] or d1 >= self.schedule[-1][1]:
            return True
        index = 0
        if len(self.schedule) >= 2:
            while index < len(self.schedule) - 1:
                if d1 >= self.schedule[index][1] and d2 <= self.schedule[index + 1][0]:
                    return True
                index += 1
        return False

    def resetInputBoxes(self):
        for box in self.addBoxes:
            box.setValue(0)
        
        self.delBox.setValue(0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.warning("Warning", "Please reload data \nif the schedule has been edited! ")
        return super().closeEvent(a0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    d = Planner(None)
    d.show()
    sys.exit(app.exec_())
