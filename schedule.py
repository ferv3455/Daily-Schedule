import pickle
import datetime
from tkinter import Toplevel, Frame, Label, Text, Button, Entry, IntVar, W, END
from tkinter.messagebox import showwarning

class Planner:
    def __init__(self, parent):
        self.parent = parent

        with open("schedule.dat", "rb") as fin:
            self.schedule = pickle.load(fin)

        root = Toplevel()
        root.title("Planner")

        root.protocol("WM_DELETE_WINDOW", self.close);

        self.text = Text(root, width=30, height=20)
        frame = Frame(root)
        self.text.grid(row=0, column=0)
        frame.grid(row=0, column=1)

        self.v1 = IntVar()
        self.v2 = IntVar()
        self.v3 = IntVar()
        self.v4 = IntVar()
        self.v5 = IntVar()
        self.v6 = IntVar()
        self.v7 = IntVar()
        self.clear_entries()

        entry1 = Entry(frame, width=3, textvariable=self.v1)
        entry1.bind("<Return>", self.delete)
        label1 = Label(frame, text="Index: ")
        label1.grid(row=1, column=0)
        entry1.grid(row=1, column=1, pady=50)
        bt1 = Button(frame, text="Delete", command=self.delete)
        bt1.bind("<Return>", self.delete)
        bt1.grid(row=1, column=2)

        entry2 = Entry(frame, width=3, textvariable=self.v2)
        entry3 = Entry(frame, width=3, textvariable=self.v3)
        entry4 = Entry(frame, width=3, textvariable=self.v4)
        entry5 = Entry(frame, width=3, textvariable=self.v5)
        entry6 = Entry(frame, width=3, textvariable=self.v6)
        entry7 = Entry(frame, width=3, textvariable=self.v7)
        entry7.bind("<Return>", self.add)
        lb_beg = Label(frame, text="Begin:")
        lb_end = Label(frame, text="End:")

        lb_beg.grid(row=2, column=0, columnspan=3, sticky=W)
        entry2.grid(row=3, column=0)
        entry3.grid(row=3, column=1)
        entry4.grid(row=3, column=2)
        lb_end.grid(row=4, column=0, columnspan=3, sticky=W)
        entry5.grid(row=5, column=0)
        entry6.grid(row=5, column=1)
        entry7.grid(row=5, column=2)

        bt2 = Button(frame, text="Add", command=self.add)
        bt2.bind("<Return>", self.add)
        bt2.grid(row=6, column=0, columnspan=3)

        self.show_schedule()

        root.mainloop()

    def show_schedule(self):
        self.text.delete(1.0, END)
        for index, task in enumerate(self.schedule, 1):
            task_str = task[0].strftime(
                "%H:%M:%S") + " - " + task[1].strftime("%H:%M:%S")
            self.text.insert(END, str(index) + "\t" + task_str + "\n")

    def update_schedule(self):
        self.schedule.sort()
        with open("schedule.dat", "wb") as fout:
            pickle.dump(self.schedule, fout)

    def delete(self, event=None):
        if self.v1.get() - 1 >= len(self.schedule) or self.v1.get() - 1 < 0:
            showwarning("Warning", "Index out of range!")
            return
        del self.schedule[self.v1.get() - 1]
        self.update_schedule()
        self.show_schedule()
        self.clear_entries()

    def add(self, event=None):
        d1 = datetime.time(self.v2.get(), self.v3.get(), self.v4.get())
        d2 = datetime.time(self.v5.get(), self.v6.get(), self.v7.get())
        if d1 >= d2:
            showwarning("Warning", "Task time not valid!")
            return
        if not self.valid_input(d1, d2):
            showwarning("Warning", "Overlapping existing tasks!")
            return
        self.schedule.append((d1, d2))
        self.update_schedule()
        self.show_schedule()
        self.clear_entries()

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
        
    def clear_entries(self):
        self.v1.set(1)
        self.v2.set(0)
        self.v3.set(0)
        self.v4.set(0)
        self.v5.set(0)
        self.v6.set(0)
        self.v7.set(0)

    def close(self):
        self.parent.restart()
        

if __name__ == "__main__":
    Planner()
