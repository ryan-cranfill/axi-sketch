import mido
import math
from dataclasses import dataclass

import presets
from settings import VERBOSE


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


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
    def __init__(self, preset: presets.ControllerPreset = presets.bcr2000) -> None:
        self.preset = preset
        self.control_listen_channel = preset.control_channel
        self.x_control_channel = preset.x_control_channel
        self.y_control_channel = preset.y_control_channel
        
        self.pen_up_control_channel = preset.pen_up_control_channel
        self.go_home_control_channel = preset.go_home_control_channel
        self.go_bottom_left_control_channel = preset.go_bottom_left_control_channel
        self.go_bottom_right_control_channel = preset.go_bottom_right_control_channel
        self.go_top_right_control_channel = preset.go_top_right_control_channel
        self.go_top_left_control_channel = preset.go_top_left_control_channel
        
        self.x_val = None
        self.y_val = None

        # Show the available MIDI devices
        print("Available MIDI devices:")
        for device in mido.get_output_names():
            print("    {}".format(device))
        
        try:
            self.outport = mido.open_output()
            self.inport = mido.open_input()
            print("Using MIDI out device: {}".format(self.outport))
            print("Using MIDI in device: {}".format(self.inport))
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
                    print('IGNORED' if msg.channel != self.control_listen_channel else '', msg)
                
                if not msg.channel == self.control_listen_channel:
                    continue

                if msg.type == "control_change":
                    val = msg.value
                    if msg.control == self.x_control_channel:
                        if self.x_val is None:
                            self.x_val = val

                        # We can't reset the value, so we need to check if the last value was the min (0) or max (127) and if so, increment or decrement the change
                        change = 0
                        if self.x_val == 0 and val == 0:
                            change = -1
                            # self.x_val = 99999
                        elif self.x_val == 127 and val == 127:
                            change = 1
                            # self.x_val = -99999
                        else:
                            change = val - self.x_val

                        self.x_val = val
                        update.x_change -=  change  # Subtract because the knobs are backwards

                    elif msg.control == self.y_control_channel:
                        if self.y_val is None:
                            self.y_val = val

                        # We can't reset the value, so we need to check if the last value was the min (0) or max (127) and if so, increment or decrement the change
                        change = 0
                        if self.y_val == 0 and val == 0:
                            change = -1
                        elif self.y_val == 127 and val == 127:
                            change = 1
                        else:
                            change = val - self.y_val
                        
                        self.y_val = val
                        update.y_change -= change  # Subtract because the knobs are backwards
                    
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
                    
                    # Clamp the values
                    update.x_change = clamp(update.x_change * self.preset.x_acceleration, -self.preset.max_x_speed, self.preset.max_x_speed)
                    update.y_change = clamp(update.y_change * self.preset.y_acceleration, -self.preset.max_y_speed, self.preset.max_y_speed)
        
                # self.outport.send(mido.Message("control_change", channel=0, control=self.y_control_channel, value=63))
                # self.outport.send(
                #     mido.Message('note_on', note=29, velocity=100, channel=0)
                # )
                # self.outport.send(
                #     mido.Message('note_on', note=13, velocity=100, channel=9)
                # )
        
        return update  # Return the negative values because the knobs are backwards


    def on_exit(self):
        # Things to do when the program exits
        if self.outport:
            self.outport.close()
        if self.inport:
            self.inport.close()