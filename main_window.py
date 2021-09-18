from tkinter import Tk, Frame, Label, StringVar, IntVar, Menu, CENTER, font
from tkinter.messagebox import showinfo, askokcancel
import datetime
import time
import pickle
from threading import Thread
from schedule import Planner
from calendar import Calendar, CalendarEditor
from settings import Settings
from full_screen import FullScreenDemo
import ctypes
import os

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)

flag_continue = True

def warning(str1, str2):
    showinfo(str1, str2)


class TimingSystem:
    def __init__(self):
        self.root = Tk()
        self.root.title("Timing System")
        self.root.geometry("250x120+130+875")
        self.root.wm_attributes('-topmost', 1)
        self.root.wm_attributes('-alpha', 0.6)
        self.root.overrideredirect(True)
        self.root.bind("<Button-3>", self.menu_popup)

        self.root.protocol("WM_DELETE_WINDOW", self.root_exit);

        with open("calendar.dat", "rb") as fin:
            self.calendar = pickle.load(fin)
        
        today_obj = self.calendar.get_day(datetime.date.today())
        if today_obj:
            self.alarms = today_obj.get_alarms()
        else:
            self.alarms = list()

        self.current_alarm = 0
        self.init_alarms()

        with open("schedule.dat", "rb") as fin:
            self.schedule = pickle.load(fin)

        self.task_num = 0

        self.state = True       #True为任务中
        self.end_time = datetime.time(0, 0, 0)

        with open("settings.dat", "rb") as fin:
            self.settings = pickle.load(fin)

        self.shutdown = IntVar()
        self.shutdown.set(self.settings.shutdown)

        # Arranging widgets
        self.frame = Frame(self.root)
        self.frame.pack()

        ft = font.Font(family='Consolas', size=15)

        self.v1 = StringVar()      #标记状态
        self.v1.set("Task")
        self.label1 = Label(self.frame, width=15, font=ft, 
                            justify=CENTER, textvariable=self.v1)
        self.label1.pack()

        self.v2 = StringVar()       #标记状态结束的时间
        self.label2 = Label(self.frame, width=15, font=ft,
                            justify=CENTER, textvariable=self.v2, fg="blue")
        self.label2.pack()

        self.v3 = StringVar()       #标记当前时间
        self.label3 = Label(self.frame, width=15, font=ft,
                            justify=CENTER, textvariable=self.v3)
        self.label3.pack()

        self.menu = Menu(self.root, tearoff=0)
        self.menu.add_command(label="Edit the schedule", command=self.edit_schedule)
        self.menu.add_command(label="View the calendar", command=self.view_calendar)
        self.menu.add_separator()
        self.menu.add_command(label="Fullscreen", command=self.full_screen)
        self.menu.add_checkbutton(label="Scheduled Shutdown", variable=self.shutdown, command=self.restart)
        self.menu.add_separator()
        self.menu.add_command(label="Version 3.0", command=None)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.root_exit)

        self.update()
        self.root.tk.call('tk', 'scaling', ScaleFactor / 75)
        self.root.mainloop()

    def edit_schedule(self):
        Planner(self)

    def view_calendar(self):
        CalendarEditor(self)

    def root_exit(self):
        self.settings.shutdown = self.shutdown.get()
        with open("settings.dat", "wb") as fout:
            pickle.dump(self.settings, fout)

        global flag_continue
        flag_continue = False
        self.root.destroy()

    def menu_popup(self, event):
        self.menu.post(event.x_root, event.y_root)

    def init_alarms(self):
        if not self.alarms:
            self.current_alarm = -1
        else:
            now = datetime.datetime.now().time()
            while now > self.alarms[self.current_alarm]:
                self.current_alarm += 1
                if self.current_alarm >= len(self.alarms):
                    self.current_alarm = -1
                    break

    def update(self):
        now = datetime.datetime.now().time()
        if self.current_alarm >= 0 and now > self.alarms[self.current_alarm]:
            t = Thread(target=warning, args=("Alarm", \
                    "Alarm Reminder: " + self.alarms[self.current_alarm].isoformat()))
            t.start()
            self.current_alarm += 1
            if self.current_alarm >= len(self.alarms):
                self.current_alarm = -1
        
        if (now.hour, now.minute) == (0, 0) and now.second < 3:
            self.end_time = datetime.time(0, 0, 0)

        if now > self.end_time:
            flag = True
            while now > self.schedule[self.task_num][1]:
                self.task_num += 1
                if self.task_num == len(self.schedule):
                    flag = False
                    break
            if flag:
                self.state = now >= self.schedule[self.task_num][0]
                if self.state:
                    self.end_time = self.schedule[self.task_num][1]
                    self.v1.set("Task")
                    self.label2["fg"] = "blue"
                    t = Thread(target=warning, args=("Task Begins", "Rest is over.\nReturn to work."))
                    t.start()
                else:
                    self.end_time = self.schedule[self.task_num][0]
                    self.v1.set("Rest")
                    self.label2["fg"] = "red"
                    t = Thread(target=warning, args=("Task Ends", "This period is over.\nHave a rest."))
                    t.start()
                self.v2.set(self.end_time.strftime("%H:%M:%S"))

            else:
                self.end_time = datetime.time(23, 59, 59)
                self.v2.set((datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%H:%M:%S"))
                self.v1.set("All tasks over")
                self.label2["fg"] = "red"
                t = Thread(target=warning, args=("Task Ends", "Today's work is over.\nHave a rest."))
                t.start()

                if self.shutdown.get():
                    os.system("shutdown /s /t 300")
                    # os.system("shutdown /a")
                

        self.v3.set(now.strftime("%H:%M:%S"))
        self.root.after(1000, self.update)

    def full_screen(self):
        if not self.state:
            isOK = askokcancel("During a break", "Are you sure about fullscreen during a break?")
            if not isOK:
                return
        FullScreenDemo(self, self.end_time)

    def restart(self):
        self.settings.shutdown = self.shutdown.get()
        with open("settings.dat", "wb") as fout:
            pickle.dump(self.settings, fout)
        
        self.root.destroy()


if __name__ == "__main__":
    while flag_continue:
        TimingSystem()



