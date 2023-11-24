import customtkinter as ctk
import tkinter as tk
from settings import *
from time import time

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("300x600")
        self.title("Stopwatch")
        self.configure(fg_color=BLACK)
        self.resizable(False,False)

        # grid layout
        self.rowconfigure(0,weight=5,uniform="a")
        self.rowconfigure(1,weight=1,uniform="a")
        self.rowconfigure(2,weight=4,uniform="a")
        self.columnconfigure(0,weight=1,uniform="a")

        # fonts
        self.button_font = ctk.CTkFont(family=FONT,size=BUTTON_FONT_SIZE)

        self.timer = Timer()


        # widgets
        self.clock = Clock(self)
        self.control_buttons = ControlButtons(parent = self,
                                              font = self.button_font,
                                              start = self.start,
                                              pause = self.pause,
                                              resume = self.resume,
                                              reset = self.reset,
                                              create_lap = self.create_lap)

        self.mainloop()

    def start(self):
        self.timer.start()
    
    def pause(self):
        self.timer.pause()
    
    def resume(self):
        self.timer.resume()
    
    def reset(self):
        self.timer.reset()
    
    def create_lap(self):
        print(self.timer.get_time())


class Clock(tk.Canvas):
    def __init__(self,parent):
        super().__init__(parent,background=BLACK,bd=0,highlightthickness=0,relief="ridge")
        self.grid(column=0,row=0,sticky="nsew",padx=5,pady=5)
        self.bind("<Configure>",self.setup)
        
    def setup(self,event):
        self.center = (event.width / 2, event.height / 2)
        self.size = (event.width, event.height)
        self.draw()

    def draw(self, milliseconds=0):
        self.draw_center()
    
    def draw_center(self):
        self.create_oval(self.center[0]-CENTER_SIZE,
                         self.center[1]-CENTER_SIZE,
                         self.center[0]+CENTER_SIZE,
                         self.center[1]+CENTER_SIZE,
                         fill=BLACK,
                         outline=ORANGE,
                         width=LINE_WIDTH)


class ControlButtons(ctk.CTkFrame):
    def __init__(self,parent,font,start,pause,resume,reset,create_lap):
        super().__init__(parent,corner_radius=0,fg_color="transparent")
        self.grid(column=0,row=1,sticky="nsew")

        # interaction methods
        self.start = start
        self.pause = pause
        self.resume = resume
        self.reset = reset
        self.create_lap = create_lap

        # state
        self.state = "off"

        # grid layout
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1,uniform="b")
        self.columnconfigure(1,weight=9,uniform="b")
        self.columnconfigure(2,weight=1,uniform="b")
        self.columnconfigure(3,weight=9,uniform="b")
        self.columnconfigure(4,weight=1,uniform="b")

        # lap button
        self.lap_button = ctk.CTkButton(
            master=self,
            text="Lap",
            command=self.lap_handler,
            state="disabled",
            fg_color=GREY,
            font=font
        )

        # start button
        self.start_button = ctk.CTkButton(
            master=self,
            text="Start",
            command=self.start_handler,
            fg_color=GREEN,
            hover_color=GREEN_HIGHLIGHT,
            text_color=GREEN_TEXT,
            font=font
        )


        # place the buttons
        self.lap_button.grid(row=0,column=1,sticky="nsew")
        self.start_button.grid(row=0,column=3,sticky="nsew")

    def start_handler(self):
        if self.state == "off":
            self.start()
            self.state = "on"
        
        elif self.state == "on":
            self.pause()
            self.state = "pause"
        
        elif self.state == "pause":
            self.resume()
            self.state = "on"
        self.update_buttons()

    def lap_handler(self):
        if self.state == "on":
            self.create_lap()
        else:
            self.reset()
            self.state = "off"
        self.update_buttons()

    def update_buttons(self):
        if self.state == "off":
            self.start_button.configure(text="Start",fg_color=GREEN,hover_color=GREEN_HIGHLIGHT,text_color=GREEN_TEXT)
            self.lap_button.configure(state="disabled",text="Lap",fg_color=GREY)
        elif self.state == "on":
            self.lap_button.configure(text="Lap",state="normal",fg_color=ORANGE_DARK,hover_color=ORANGE_HIGHLIGHT,text_color=ORANGE_DARK_TEXT)
            self.start_button.configure(text="Stop",fg_color=RED,hover_color=RED_HIGHLIGHT,text_color=RED_TEXT)
        elif self.state == "pause":
            self.start_button.configure(text="Start",fg_color=GREEN,hover_color=GREEN_HIGHLIGHT,text_color=GREEN_TEXT)
            self.lap_button.configure(text="Reset")

class Timer:
    def __init__(self):
        self.start_time = None
        self.pause_time = None
        self.paused = False

    def start(self):
        self.start_time = time()
        self.reset()
    
    def pause(self):
        self.pause_time = time()
        self.paused = True
    
    def resume(self):
        elapsed_time = time() - self.pause_time
        self.start_time += elapsed_time
        self.paused = False
    
    def reset(self):
        self.pause_time = 0
        self.paused = False
    
    def get_time(self):
        if self.paused:
            return int(round(self.pause_time - self.start_time,2)*1000)
        else:
            return int(round(time() - self.start_time,2)*1000)

if __name__ == "__main__":
    App()