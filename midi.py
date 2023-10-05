import mido
from dataclasses import dataclass

from settings import VERBOSE


@dataclass
class MidiUpdate:
    x_change: int = 0 # The amount of steps to change the x position by
    y_change: int = 0 # The amount of steps to change the y position by
    pen_toggle: bool = False # The pen should be toggled
    go_home: bool = False # The pen should go home
    go_bottom_left: bool = False # The pen should go to the bottom left corner
    go_bottom_right: bool = False # The pen should go to the bottom right corner
    go_top_right: bool = False # The pen should go to the top right corner
    go_top_left: bool = False # The pen should go to the top left corner


class MidiManager:
    def __init__(self, x_control_channel=6, y_control_channel=2) -> None:
        self.x_control_channel = x_control_channel
        self.y_control_channel = y_control_channel
        
        self.pen_up_control_channel = 40
        self.go_home_control_channel = 39
        self.go_bottom_left_control_channel = 79
        self.go_bottom_right_control_channel = 80
        self.go_top_right_control_channel = 72
        self.go_top_left_control_channel = 71
        
        self.x_val = None
        self.y_val = None

        # Show the available MIDI devices
        print("Available MIDI devices:")
        for device in mido.get_output_names():
            print("    {}".format(device))
        
        try:
            self.outport = mido.open_output()
            self.inport = mido.open_input()
            print("Using MIDI device: {}".format(self.outport))
        except:
            print("No MIDI devices found")
            self.outport = None
            self.inport = None
            return
    
    def update(self) -> MidiUpdate:
        # Process midi messages that have happened since the last update
        update: MidiUpdate = MidiUpdate()

        if self.inport:
            for msg in self.inport.iter_pending():
                if VERBOSE: 
                    print(msg)

                if msg.type == "control_change":
                    val = msg.value
                    if msg.control == self.x_control_channel:
                        if self.x_val is None:
                            self.x_val = val

                        # We can't reset the value, so we need to check if the last value was the min (0) or max (127) and if so, increment or decrement the change
                        if self.x_val == 0 and val == 0:
                            update.x_change -= 1
                        elif self.x_val == 127 and val == 127:
                            update.x_change += 1
                        else:
                            update.x_change += val - self.x_val
                        self.x_val = val
                    elif msg.control == self.y_control_channel:
                        if self.y_val is None:
                            self.y_val = val

                        # We can't reset the value, so we need to check if the last value was the min (0) or max (127) and if so, increment or decrement the change
                        if self.y_val == 0 and val == 0:
                            update.y_change -= 1
                        elif self.y_val == 127 and val == 127:
                            update.y_change += 1
                        else:
                            update.y_change += val - self.y_val
                        self.y_val = val
                    
                    elif msg.control == self.pen_up_control_channel:
                        # Toggle the pen up or down, and do the same in turtle
                        update.pen_toggle = True
                    
                    elif msg.control == self.go_home_control_channel:
                        # Signal to home the pen
                        update.go_home = True
                    
                    elif msg.control == self.go_bottom_left_control_channel:
                        update.go_bottom_left = True
                    
                    elif msg.control == self.go_bottom_right_control_channel:
                        update.go_bottom_right = True

                    elif msg.control == self.go_top_right_control_channel:
                        update.go_top_right = True

                    elif msg.control == self.go_top_left_control_channel:
                        update.go_top_left = True
        
        return update  # Return the negative values because the knobs are backwards


    def on_exit(self):
        # Things to do when the program exits
        if self.outport:
            self.outport.close()
        if self.inport:
            self.inport.close()