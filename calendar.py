import pickle
import datetime
from day import Day
from tkinter import Toplevel, Frame, Button, Label, LEFT, RIGHT, IntVar, \
        StringVar, Text, Radiobutton, Entry, font, W, X, END
from tkinter.messagebox import showwarning

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


class CalendarEditor:
    def __init__(self, parent):
        self.parent = parent
        self.ft = font.Font(family='Calibri', size=10)
        self.ft_main = font.Font(family='Consolas', size=18, weight=font.BOLD)
        self.ft_title = font.Font(family='Calibri', size=14, weight=font.BOLD)

        with open("calendar.dat", "rb") as fin:
            self.calendar = pickle.load(fin)

        root = Toplevel()
        root.title("Calendar Editor")
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.state("zoomed")
        self.originalBG = root.cget("bg")

        self.current_date = datetime.date.today()
        self.day_delta = datetime.timedelta(1)

        frame0 = Frame(root)
        frame0.pack(fill=X, padx=50, pady=20)
        bt_previous = Button(frame0, text="<<<<", command=self.backward, font=self.ft_title)
        bt_forward = Button(frame0, text=">>>>", command=self.forward, font=self.ft_title)
        bt_previous.pack(side=LEFT)
        bt_forward.pack(side=RIGHT)
        title_label = Label(frame0, text="Calendar", font=self.ft_main)
        title_label.pack()

        frame1 = Frame(root)
        frame1.pack(padx=20, pady=20)

        self.day_vals = list()
        self.day_labels = list()
        self.day_alarms = list()
        self.day_remarks = list()

        self.select_day = IntVar()
        self.select_day.set(0)

        for i in range(8):
            self.day_vals.append(StringVar())
            self.day_labels.append(Label(frame1, textvariable=self.day_vals[i], font=self.ft))
            self.day_labels[i].grid(row=0, column=i)
            self.day_alarms.append(Text(frame1, width=20, height=6, font=self.ft))
            self.day_alarms[i].grid(row=1, column=i)
            self.day_remarks.append(Text(frame1, width=20, height=15, font=self.ft))
            self.day_remarks[i].grid(row=2, column=i)
            rbutton = Radiobutton(frame1, value=i-1, variable=self.select_day, \
                    text="▲", width=5, indicatoron=False, font=self.ft)
            rbutton.grid(row=3, column=i)

        frame10 = Frame(root)
        frame10.pack()

        frame2 = Frame(frame10)
        frame2.pack(side=LEFT, padx=20)
        frame4 = Frame(frame10)
        frame4.pack(side=RIGHT, padx=20)
        frame3 = Frame(frame10)
        frame3.pack(side=LEFT, padx=20)

        self.h = IntVar()
        self.m = IntVar()
        self.s = IntVar()
        self.idx1 = IntVar()
        self.idx1.set(1)
        self.idx2 = IntVar()
        self.idx2.set(1)
        self.new_remark = StringVar()

        al_lb = Label(frame2, text="Edit the alarms:", font=self.ft_title)
        ent1_h = Entry(frame2, width=4, textvariable=self.h, font=self.ft)
        ent1_m = Entry(frame2, width=4, textvariable=self.m, font=self.ft)
        ent1_s = Entry(frame2, width=4, textvariable=self.s, font=self.ft)
        ent1_s.bind("<Return>", self.add_alarm)
        add_bt1 = Button(frame2, text="Add", command=self.add_alarm, font=self.ft)
        add_bt1.bind("<Return>", self.add_alarm)
        ent1_idx = Entry(frame2, width=4, textvariable=self.idx1, font=self.ft)
        ent1_idx.bind("<Return>", self.del_alarm)
        remove_bt1 = Button(frame2, text="Remove", command=self.del_alarm, font=self.ft)
        remove_bt1.bind("<Return>", self.del_alarm)

        al_lb.grid(row=0, column=0, columnspan=3, sticky=W)
        ent1_h.grid(row=1, column=0)
        ent1_m.grid(row=1, column=1)
        ent1_s.grid(row=1, column=2)
        add_bt1.grid(row=1, column=3)
        ent1_idx.grid(row=2, column=1)
        remove_bt1.grid(row=2, column=3)

        rm_lb = Label(frame3, text="Edit the remarks:", font=self.ft_title)
        ent2 = Entry(frame3, width=40, textvariable=self.new_remark, font=self.ft)
        ent2.bind("<Return>", self.add_remark)
        add_bt2 = Button(frame3, text="Add", command=self.add_remark, font=self.ft)
        add_bt2.bind("<Return>", self.add_remark)
        ent2_idx = Entry(frame3, width=4, textvariable=self.idx2, font=self.ft)
        ent2_idx.bind("<Key>", self.func_decide)
        remove_bt2 = Button(frame3, text="Remove", command=self.del_remark, font=self.ft)
        remove_bt2.bind("<Return>", self.del_remark)
        up_bt = Button(frame3, text='▲', command=self.up_remark, font=self.ft)
        up_bt.bind("<Return>", self.up_remark)
        down_bt = Button(frame3, text='▼', command=self.down_remark, font=self.ft)
        down_bt.bind("<Return>", self.down_remark)

        rm_lb.grid(row=0, column=0, columnspan=3, sticky=W)
        ent2.grid(row=1, column=0, columnspan=3)
        add_bt2.grid(row=1, column=3)
        down_bt.grid(row=2, column=0)
        ent2_idx.grid(row=2, column=1)
        remove_bt2.grid(row=2, column=2)
        up_bt.grid(row=2, column=3)

        overall_lb = Label(frame4, text="Memorandum", font=self.ft_title)
        overall_lb.pack()
        self.overall_text = Text(frame4, height=8, font=self.ft)
        self.overall_text.pack()

        frame5 = Frame(root)
        frame5.pack(pady = 20)
        self.y1 = IntVar()
        self.m1 = IntVar()
        self.d1 = IntVar()
        self.y2 = IntVar()
        self.m2 = IntVar()
        self.d2 = IntVar()
        self.reset_date_entry()
        ent_y1 = Entry(frame5, textvariable=self.y1, width=5)
        ent_m1 = Entry(frame5, textvariable=self.m1, width=3)
        ent_d1 = Entry(frame5, textvariable=self.d1, width=3)
        ent_y2 = Entry(frame5, textvariable=self.y2, width=5)
        ent_m2 = Entry(frame5, textvariable=self.m2, width=3)
        ent_d2 = Entry(frame5, textvariable=self.d2, width=3)
        clear_bt = Button(frame5, \
                text="Keep these days and clear the rest", command=self.clear_days)

        ent_y1.grid(row=1, column=1)
        ent_m1.grid(row=1, column=2)
        ent_d1.grid(row=1, column=3)
        ent_y2.grid(row=2, column=1)
        ent_m2.grid(row=2, column=2)
        ent_d2.grid(row=2, column=3)
        clear_bt.grid(row=1, column=4, rowspan=2)

        with open("remarks.dat", "r") as fin:
            content = fin.read()

        self.overall_text.insert(1.0, content)

        self.update_screen()

        root.mainloop()

    def backward(self):
        self.current_date -= self.day_delta
        self.update_screen()

    def forward(self):
        self.current_date += self.day_delta
        self.update_screen()

    def add_alarm(self, event=None):
        date = self.current_date + self.select_day.get() * self.day_delta
        date_obj = self.calendar.get_day(date)
        if not date_obj:
            self.calendar.add_day(date)
            date_obj = self.calendar.get_day(date)

        date_obj.add_alarm(self.h.get(), self.m.get(), self.s.get())
        date_obj.sort_alarm()
        self.update_column(self.select_day.get() + 1, 1)
        self.h.set(0)
        self.m.set(0)
        self.s.set(0)

    def del_alarm(self, event=None):
        date = self.current_date + self.select_day.get() * self.day_delta
        date_obj = self.calendar.get_day(date)
        try:
            date_obj.remove_alarm(self.idx1.get())
        except:
            showwarning("Warning", "Index out of range!")
        self.update_column(self.select_day.get() + 1, 1)

    def add_remark(self, event=None):
        date = self.current_date + self.select_day.get() * self.day_delta
        date_obj = self.calendar.get_day(date)
        if not date_obj:
            self.calendar.add_day(date)
            date_obj = self.calendar.get_day(date)

        date_obj.add_remark(self.new_remark.get())
        self.update_column(self.select_day.get() + 1, 2)
        self.new_remark.set("")

    def func_decide(self, event):
        if event.keysym == "Return":
            self.del_remark()
        elif event.keycode == 38:
            self.up_remark()
        elif event.keycode == 40:
            self.down_remark()

    def del_remark(self, event=None):
        date = self.current_date + self.select_day.get() * self.day_delta
        date_obj = self.calendar.get_day(date)
        try:
            date_obj.remove_remark(self.idx2.get())
        except:
            showwarning("Warning", "Index out of range!")
        self.update_column(self.select_day.get() + 1, 2)

    def up_remark(self, event=None):
        date = self.current_date + self.select_day.get() * self.day_delta
        date_obj = self.calendar.get_day(date)
        try:
            date_obj.switch_remark(self.idx2.get(), self.idx2.get() - 1)
            self.update_column(self.select_day.get() + 1, 2)
            self.idx2.set(self.idx2.get() - 1)
        except:
            showwarning("Warning", "Index out of range!")
        

    def down_remark(self, event=None):
        date = self.current_date + self.select_day.get() * self.day_delta
        date_obj = self.calendar.get_day(date)
        try:
            date_obj.switch_remark(self.idx2.get(), self.idx2.get() + 1)
            self.update_column(self.select_day.get() + 1, 2)
            self.idx2.set(self.idx2.get() + 1)
        except:
            showwarning("Warning", "Index out of range!")
        
    def clear_days(self, event=None):
        begin_date = 1000 * self.y1.get() + 100 * self.m1.get() + self.d1.get()
        end_date = 1000 * self.y2.get() + 100 * self.m2.get() + self.d2.get()
        del_list = list()
        for day in self.calendar:
            if day < begin_date or day > end_date:
                del_list.append(day)
                
        for day in del_list:
            self.calendar.del_day(day)
        self.update_screen()

    def update_screen(self):
        for i in range(8):
            self.day_alarms[i].delete(1.0, END)
            self.day_remarks[i].delete(1.0, END)
            self.day_labels[i]["bg"] = self.originalBG
            self.day_alarms[i]["bg"] = "white"
            self.day_remarks[i]["bg"] = "white"

        for i in range(8):
            date = self.current_date + (i - 1) * self.day_delta
            if date.weekday() > 4:
                self.day_labels[i]["bg"] = "Orchid"
                self.day_alarms[i]["bg"] = "Lavender Blush"
                self.day_remarks[i]["bg"] = "Lavender Blush"
            if date == datetime.date.today():
                self.day_alarms[i]["bg"] = "Beige"
                self.day_remarks[i]["bg"] = "Beige"
            self.day_vals[i].set(date.strftime("%m/%d(%a)"))
            date_obj = self.calendar.get_day(date)
            if date_obj:
                for index, alarm in enumerate(date_obj.alarms, 1):
                    alarm_time = alarm.isoformat()
                    self.day_alarms[i].insert(END, str(index) + "  " + alarm_time + "\n")

                for index, remark in enumerate(date_obj.remarks, 1):
                    self.day_remarks[i].insert(END, str(index) + "  " + remark + "\n")

    def reset_date_entry(self):
        date = datetime.datetime.today() - datetime.timedelta(days=1)
        self.y1.set(date.year)
        self.m1.set(date.month)
        self.d1.set(date.day)
        self.y2.set(2050)
        self.m2.set(12)
        self.d2.set(31)
    
    def update_column(self, idx, row):
        if row == 1:
            self.day_alarms[idx].delete(1.0, END)
            date = self.current_date + (idx - 1) * self.day_delta
            date_obj = self.calendar.get_day(date)
            if date_obj:
                for index, alarm in enumerate(date_obj.alarms, 1):
                    alarm_time = alarm.isoformat()
                    self.day_alarms[idx].insert(END, str(index) + "  " + alarm_time + "\n")

        else:
            self.day_remarks[idx].delete(1.0, END)
            date = self.current_date + (idx - 1) * self.day_delta
            date_obj = self.calendar.get_day(date)
            if date_obj:
                for index, remark in enumerate(date_obj.remarks, 1):
                    self.day_remarks[idx].insert(END, str(index) + "  " + remark + "\n")


    def close(self):
        content = self.overall_text.get(1.0, END).strip()
        with open("calendar.dat", "wb") as fout:
            pickle.dump(self.calendar, fout)
        with open("remarks.dat", "w") as fout:
            fout.write(content)
        self.parent.restart()


if __name__ == "__main__":
    c = Calendar()
    c.add_day(datetime.date.today())
    d = c.get_day(datetime.date.today())
    d.add_alarm(15, 40, 00)
    d.add_alarm(16, 00, 00)
    d.add_remark("Hello!")
    d.add_remark("哈哈")
    with open("calendar.dat", "wb") as fout:
        pickle.dump(c, fout)


    

