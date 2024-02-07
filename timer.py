import customtkinter as ctk
import tkinter as tk
from settings import *
from time import time
from math import sin, cos, radians
from openpyxl import Workbook

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
        self.active = False
        self.lap_data = []

        # widgets
        self.clock = Clock(self)
        self.control_buttons = ControlButtons(parent = self,
                                              font = self.button_font,
                                              start = self.start,
                                              pause = self.pause,
                                              resume = self.resume,
                                              reset = self.reset,
                                              create_lap = self.create_lap)
        self.lap_container = LapContainer(self)

        # Bind "T" key to start the stopwatch
        self.bind("T".lower(), self.start_handler)

        self.mainloop()

    def animate(self):
        if self.active:
            self.clock.draw(self.timer.get_time())
            self.after(FRAMERATE, self.animate)

    def start(self):
        if not self.active:
            self.timer.start()
            self.active = True
            self.control_buttons.start_button.configure(text="Stop (T)", fg_color=RED, hover_color=RED_HIGHLIGHT, text_color=RED_TEXT)
            self.animate()
    
    def pause(self):
        self.timer.pause()
        self.active = False
        self.control_buttons.start_button.configure(text="Start (T)", fg_color=GREEN, hover_color=GREEN_HIGHLIGHT, text_color=GREEN_TEXT)
        self.create_lap("Pause")
    
    def resume(self):
        if not self.active:
            self.timer.resume()
            self.active = True
            self.control_buttons.start_button.configure(text="Stop (T)", fg_color=RED, hover_color=RED_HIGHLIGHT, text_color=RED_TEXT)
            self.animate()
    
    def reset(self):
        self.timer.reset()
        self.clock.draw(0)
        self.control_buttons.start_button.configure(text="Start (T)", fg_color=GREEN, hover_color=GREEN_HIGHLIGHT, text_color=GREEN_TEXT)

        # reset the laps
        self.lap_data.clear()
        self.lap_container.clear_container()
    
    def create_lap(self,lap_type):
        lap_num = len([lap for lap in self.lap_data if lap[0] == "Lap"]) + 1
        index = str(lap_num) if lap_type == "Lap" else ""
        self.lap_data.append((lap_type,index,self.timer.get_time()))
        self.lap_container.create(self.lap_data)

    def start_handler(self, event=None):
        if self.active:
            self.pause()
            self.control_buttons.start_button.configure(text="Stop (T)", fg_color=RED, hover_color=RED_HIGHLIGHT, text_color=RED_TEXT)
            self.control_buttons.lap_button.configure(text="Reset")
            self.save_to_excel()
        else:
            if self.timer.paused:
                self.resume()
            else:
                self.start()

        if self.active:
            self.save_to_excel()

    def save_to_excel(self):
        wb = Workbook()
        ws = wb.active
        ws.append(["Lap Type", "Time (ms)"])

        for lap in self.lap_data:
            ws.append((lap[0], lap[1], convert_ms_to_time_string(lap[2])))

        wb.save("match_data.xlsx")


class Clock(tk.Canvas):
    def __init__(self,parent):
        super().__init__(parent,background=BLACK,bd=0,highlightthickness=0,relief="ridge")
        self.grid(column=0,row=0,sticky="nsew",padx=5,pady=5)
        self.bind("<Configure>",self.setup)
        
    def setup(self,event):
        self.center = (event.width / 2, event.height / 2)
        self.size = (event.width, event.height)

        self.outer_radius = (event.width / 2) * 0.95
        self.inner_radius = (event.width / 2) * 0.85
        self.middle_radius = (event.width / 2) * 0.9
        self.number_radius = (event.width / 2) * 0.7
        self.start_radius = (event.width / 2) * 0.2

        self.draw()

    def draw(self, milliseconds=0):

        seconds = milliseconds / 1000
        angle = (seconds % 60) * 6

        self.delete("all")
        self.create_rectangle((0,0),self.size,fill=BLACK)

        self.draw_clock()
        self.draw_text(milliseconds)
        self.draw_hand(angle)
        self.draw_center()        
    
    def draw_center(self):
        self.create_oval(self.center[0]-CENTER_SIZE,
                         self.center[1]-CENTER_SIZE,
                         self.center[0]+CENTER_SIZE,
                         self.center[1]+CENTER_SIZE,
                         fill=BLACK,
                         outline=ORANGE,
                         width=LINE_WIDTH)

    def draw_clock(self):
        for angle in range(360):            
            sin_a = sin(radians(angle-90))
            cos_a = cos(radians(angle-90))

            x = self.center[0] + (cos_a * self.outer_radius)
            y = self.center[1] + (sin_a * self.outer_radius)

            if angle % 30 == 0:
                # draw the line
                x_inner = self.center[0] + (cos_a * self.inner_radius)
                y_inner = self.center[1] + (sin_a * self.inner_radius)
                self.create_line((x_inner,y_inner),(x,y),fill=WHITE,width=LINE_WIDTH)

                # draw the numbers
                x_number = self.center[0] + (cos_a * self.number_radius)
                y_number = self.center[1] + (sin_a * self.number_radius)
                self.create_text((x_number,y_number),text=f"{int(angle / 6)}",font=FONT,fill=WHITE)

            elif angle %6 == 0:
                x_middle = self.center[0] + (cos_a * self.middle_radius)
                y_middle = self.center[1] + (sin_a * self.middle_radius)

                self.create_line((x_middle,y_middle),(x,y),fill=GREY,width=LINE_WIDTH)

    def draw_hand(self, angle=0):
            sin_a = sin(radians(angle-90))
            cos_a = cos(radians(angle-90))    

            x_end = self.center[0] + (cos_a * self.outer_radius)
            y_end = self.center[1] + (sin_a * self.outer_radius)  

            x_start = self.center[0] - (cos_a * self.start_radius)
            y_start = self.center[1] - (sin_a * self.start_radius)

            self.create_line((x_start,y_start),(x_end,y_end),fill=ORANGE,width=LINE_WIDTH)

    def draw_text(self,milliseconds):
            output_text = convert_ms_to_time_string(milliseconds)
            self.create_text((self.center[0],self.center[1] + 50), text=output_text,fill=WHITE,anchor="center",font=f"{FONT}{CLOCK_FONT_SIZE}")

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
            text="Start (T)",
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
            self.create_lap("Lap")
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

class LapContainer(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent,fg_color=BLACK)
        self.grid(column=0,row=2,sticky="nsew")
        self.canvas = None
    
    def create(self,data):
        self.clear_container()

        item_number = len(data)
        list_height = item_number * LAP_ITEM_HEIGHT
        scrollable = list_height > self.winfo_height()
        scroll_height = list_height if scrollable else self.winfo_height()

        # canvas setup
        self.canvas = tk.Canvas(self,background=BLACK,
                                scrollregion=(0,0,self.winfo_width(),
                                              scroll_height),
                                bd=0,
                                highlightthickness=0,
                                relief="ridge")
        self.canvas.pack(fill="both",expand=True)

        # create items
        display_frame = ctk.CTkFrame(self,fg_color=BLACK)
        for index, item in enumerate(data):
            last_one = index == item_number -1
            self.item(display_frame,item,last_one).pack(fill="both",expand=True)

        if scrollable:
            self.canvas.bind_all("<MouseWheel>",lambda event:self.canvas.yview_scroll(-int(event.delta / 60),"units"))

        # place the displaty frame on canvas
        self.canvas.create_window((0,0),
                                  anchor="nw",
                                  window=display_frame,
                                  width=self.winfo_width(),
                                  height=list_height)

    def item(self,parent,info,last_one):
        frame = ctk.CTkFrame(parent,fg_color=BLACK)
        info_frame = ctk.CTkFrame(frame,fg_color=BLACK)
        ctk.CTkLabel(info_frame,text=f"{info[0]} {info[1]}",text_color=WHITE).pack(side="left",padx=10)
        ctk.CTkLabel(info_frame,text=f"{convert_ms_to_time_string(info[2])}",text_color=WHITE).pack(side="right",padx=10)
        info_frame.pack(fill="both",expand=True)

        if not last_one:
            ctk.CTkFrame(frame,fg_color=GREY,height=1).pack(fill="x")

        return frame

    def clear_container(self):                
        if self.canvas:
            self.canvas.pack_forget()

def convert_ms_to_time_string(milliseconds):
    if milliseconds > 0:
        milliseconds_only = str(milliseconds)[-3:-1]
        seconds_only = str(milliseconds)[:-3] if milliseconds >= 1000 else 0

        minutes, seconds = divmod(int(seconds_only),60)
        hours, minutes = divmod(minutes, 60)

        second_string = str(seconds) if seconds >= 10 else f"0{seconds}"
        minute_string = str(minutes) if minutes >= 10 else f"0{minutes}"
        hour_string = str(hours) if hours >= 10 else f"0{hours}"

        if hours > 0:
            output_text = f"{hour_string}:{minute_string}:{second_string}.{milliseconds}"
        elif minutes > 0:
            output_text = f"{minute_string}:{second_string}.{milliseconds_only}"
        else:
            output_text = f"{second_string}.{milliseconds}"

    else:
        output_text = ""
    return output_text

if __name__ == "__main__":
    App()