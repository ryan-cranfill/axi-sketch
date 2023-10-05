import mido
import random

class MidiManager:
    def __init__(self, x_control_channel=6, y_control_channel=2) -> None:
        self.x_control_channel = x_control_channel
        self.y_control_channel = y_control_channel
        self.pen_control_channel = 40
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
    
    def update(self) -> (int, int):
        # Listen for messages
        x_change = 0 # Track the amount of change in the x value
        y_change = 0 # Track the amount of change in the y value
        pen_toggle = False # Track whether the pen should be toggled
        if self.inport:
            for msg in self.inport.iter_pending():
                print(msg)
                if msg.type == "control_change":
                    val = msg.value
                    if msg.control == self.x_control_channel:
                        if self.x_val is None:
                            self.x_val = val

                        # We can't reset the value, so we need to check if the last value was the min (0) or max (127) and if so, increment or decrement the change
                        if self.x_val == 0 and val == 0:
                            x_change -= 1
                        elif self.x_val == 127 and val == 127:
                            x_change += 1
                        else:
                            x_change += val - self.x_val
                        self.x_val = val
                    elif msg.control == self.y_control_channel:
                        if self.y_val is None:
                            self.y_val = val

                        # We can't reset the value, so we need to check if the last value was the min (0) or max (127) and if so, increment or decrement the change
                        if self.y_val == 0 and val == 0:
                            y_change -= 1
                        elif self.y_val == 127 and val == 127:
                            y_change += 1
                        else:
                            y_change += val - self.y_val
                        self.y_val = val
                    
                    elif msg.control == self.pen_control_channel:
                        pen_toggle = True
        
        return 0 - x_change, 0 - y_change, pen_toggle  # Return the negative values because the knobs are backwards


    def on_exit(self):
        # Things to do when the program exits
        if self.outport:
            self.outport.close()
        if self.inport:
            self.inport.close()