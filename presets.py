# Presets for different midi controllers
from dataclasses import dataclass

@dataclass
class ControllerPreset:
    x_control_channel: int # The midi control channel for the x axis
    y_control_channel: int # The midi control channel for the y axis
    pen_up_control_channel: int # The midi control channel for the pen up button
    go_home_control_channel: int # The midi control channel for the go home button
    go_bottom_left_control_channel: int # The midi control channel for the go bottom left button
    go_bottom_right_control_channel: int # The midi control channel for the go bottom right button
    go_top_right_control_channel: int # The midi control channel for the go top right button
    go_top_left_control_channel: int # The midi control channel for the go top left button
    control_channel: int = 0 # Only listen to messages on this channel
    left_button_preset: int = None # The midi control channel for the left button
    right_button_preset: int = None # The midi control channel for the right button
    up_button_preset: int = None
    down_button_preset: int = None
    x_acceleration: float = 1 # The amount to multiply the x axis by
    y_acceleration: float = 1 # The amount to multiply the y axis by
    max_x_speed: float = 30 # The maximum speed of the x axis
    max_y_speed: float = 30 # The maximum speed of the y axis


bcr2000 = ControllerPreset(
    x_control_channel=6,
    y_control_channel=2,
    pen_up_control_channel=40,
    go_home_control_channel=39,
    go_bottom_left_control_channel=79,
    go_bottom_right_control_channel=80,
    go_top_right_control_channel=72,
    go_top_left_control_channel=71
)

digitakt = ControllerPreset(
    control_channel=9,
    x_control_channel=74,
    y_control_channel=77,
    pen_up_control_channel=40,
    go_home_control_channel=39,
    go_bottom_left_control_channel=79,
    go_bottom_right_control_channel=80,
    go_top_right_control_channel=72,
    go_top_left_control_channel=71,
    left_button_preset=48,
    right_button_preset=49,
    up_button_preset=50,
    down_button_preset=51,
    x_acceleration=1.25,
    y_acceleration=2.5,
    # max_x_speed=10,
    # max_y_speed=10,
)
