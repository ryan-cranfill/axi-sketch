from pyaxidraw import axidraw 

class PlotterManager:
    def __init__(self) -> None:
        # Set up the AxiDraw
        ad = axidraw.AxiDraw()

        ad.interactive()
        ad.options.units = 2 # 2 = mm
        ad.options.speed_pendown = 50
        ad.options.speed_penup = 50
        ad.options.pen_rate_lower = 50
        ad.options.pen_rate_raise = 50
        ad.options.pen_pos_up = 60
        ad.options.pen_pos_down = 20
        ad.options.accel = 100
        ad.options.pen_delay_down = 0
        ad.options.pen_delay_up = 0
        ad.options.pen_width = 0.5
        ad.options.pen_color = "black"
        ad.options.model = 2

        if not ad.connect():            # Open serial port to AxiDraw;
            self.ad = None
            return
        
        self.ad = ad
        self.pen_is_down = False

    def update(self):
        pass

    def moveto(self, x, y):
        if self.ad:
            print("Moving AxiDraw to ({}, {})...".format(x, y))
            self.ad.moveto(x, y)
    
    def goto(self, x, y):
        if self.ad:
            print("Going to ({}, {})...".format(x, y))
            self.ad.goto(x, y)

    def lift_pen(self):
        if self.ad:
            print("Lifting AxiDraw pen...")
            self.ad.penup()
    
    def lower_pen(self):
        if self.ad:
            print("Lowering AxiDraw pen...")
            self.ad.pendown()
    
    def toggle_pen(self):
        if self.ad:
            if self.pen_is_down:
                self.lift_pen()
            else:
                self.lower_pen()
            self.pen_is_down = not self.pen_is_down

    def home_axidraw(self):
        if self.ad:
            print("Homing AxiDraw...")
            self.lift_pen()
            self.ad.goto(0, 0)

    def on_exit(self):
        self.home_axidraw()
        if self.ad:
            self.ad.disconnect()