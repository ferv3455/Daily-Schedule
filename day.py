import datetime

class Day:
    def __init__(self, dateobj, reserve=False):
        self.date = dateobj
        self.save_condition = reserve
        self.alarms = list()        # a list of timeobjs
        self.remarks = list()       # a list of strings

    def add_alarm(self, h, m, s):
        new_time = datetime.time(h, m, s)
        self.alarms.append(new_time)

    def remove_alarm(self, idx):    # idx start from 1
        if 0 < idx <= len(self.alarms):
            del self.alarms[idx - 1]
        else:
            raise IndexError()

    def sort_alarm(self):
        self.alarms.sort()

    def get_alarms(self):
        return self.alarms

    def add_remark(self, text):
        self.remarks.append(text)

    def remove_remark(self, idx):
        if 0 < idx <= len(self.remarks):
            del self.remarks[idx - 1]
        else:
            raise IndexError()

    def switch_remark(self, idx1, idx2):
        if 0 < idx1 <= len(self.remarks) and 0 < idx2 <= len(self.remarks):
            self.remarks[idx1 - 1], self.remarks[idx2 - 1] = \
                self.remarks[idx2 - 1], self.remarks[idx1 - 1]
        else:
            raise IndexError()

    def get_remarks(self):
        return self.remarks

    def setSaveCondition(self, newCond):
        self.save_condition = newCond

    def getSaveCondition(self):
        return self.save_condition


