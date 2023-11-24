import customtkinter as ctk
from settings import *

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("300x600")
        self.title("Stopwatch")
        self.configure(fg_color=BLACK)
        self.resizable(False,False)

        self.mainloop()

if __name__ == "__main__":
    App()