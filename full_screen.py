from tkinter import Toplevel, Frame, Label, StringVar, W, E, font
import datetime
from tkinter.messagebox import showwarning
import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)


class FullScreenDemo:
    def __init__(self, parent, endtime):
        self.parent = parent
        self.endtime = endtime
        self.state = True
        self.root = Toplevel()
        self.root.title("Demo")
        self.frame = Frame(self.root)
        self.frame.pack(pady=200)
        self.root.protocol("WM_DELETE_WINDOW", self.warning)

        ft = font.Font(family='Consolas', size=16)

        self.current_time = StringVar()
        self.label1 = Label(
            self.frame, text="Current time: ", font=ft)
        self.label2 = Label(
            self.frame, text="Task ends at: ", font=ft)
        self.label3 = Label(
            self.frame, textvariable=self.current_time, font=ft)
        self.label4 = Label(self.frame, text=self.endtime.strftime(
            "%H:%M:%S"), font=ft)
        self.label1.grid(row=1, column=1, sticky=W, pady=40)
        self.label2.grid(row=2, column=1, sticky=W, pady=40)
        self.label3.grid(row=1, column=2, sticky=E)
        self.label4.grid(row=2, column=2, sticky=E)

        self.toggle_fullscreen()
        #self.root.bind("<F11>", self.toggle_fullscreen)
        #self.root.bind("<Escape>", self.end_fullscreen)
        self.check_end()
        self.root.tk.call('tk', 'scaling', ScaleFactor/75)
        self.root.mainloop()

    def warning(self):
        showwarning("Task not over", "Task is not over yet!")

    def toggle_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)

    def check_end(self):
        now = datetime.datetime.now().time()
        self.current_time.set(now.strftime("%H:%M:%S"))
        if self.state and now >= self.endtime:
            self.root.attributes("-fullscreen", False)
            self.root.attributes("-topmost", False)
            self.state = False
            self.close()
        else:
            self.root.after(1000, self.check_end)

    def close(self):
        self.parent.restart()


if __name__ == "__main__":
    FullScreenDemo(datetime.time(11, 4, 10))
