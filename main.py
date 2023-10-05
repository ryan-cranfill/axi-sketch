import atexit
import turtle
import signal

import presets
from midi import MidiManager
from plotter import PlotterManager


WINDOW_WIDTH = 600
WINDOW_HEIGHT = 450
# Coordinates of the top left corner of the window
WINDOW_TOP_X = 0 - int(WINDOW_WIDTH / 2)
WINDOW_TOP_Y = 0 + int(WINDOW_HEIGHT / 2)
WIDTH_MM = WINDOW_WIDTH * 0.352777778
HEIGHT_MM = WINDOW_HEIGHT * 0.352777778

MAX_X = WINDOW_WIDTH / 2
MIN_X = 0 - MAX_X
MAX_Y = WINDOW_HEIGHT / 2
MIN_Y = 0 - MAX_Y

ARROW_KEY_MULTIPLIER = 4

#####################################################################
# Setup
#####################################################################

pen_is_down = False

plotter = PlotterManager(WIDTH_MM, HEIGHT_MM)
midi = MidiManager(presets.bcr2000)

# Set up the turtle window
turtle.setup(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
turtle.title("Axi-Sketch")
turtle.bgcolor("white")

# Create the turtle
t = turtle.Turtle()
t.pensize(5)
t.speed(0)
# Move the turtle to the top left corner of the window
t.penup()
t.setx(WINDOW_TOP_X)
t.sety(WINDOW_TOP_Y)

#####################################################################
# Exit handling
#####################################################################

def on_exit():
    print("Exiting...")
    plotter.on_exit()
    midi.on_exit()
    turtle.bye()

# Bind the escape and q keys to exit
turtle.onkeypress(on_exit, "Escape")
turtle.onkeypress(on_exit, "q")

#####################################################################
# Movement functions
#####################################################################

def get_angle(x_steps, y_steps):
    # Get the heading, weighted by the amount to move in each direction
    heading = 0
    if x_steps != 0 or y_steps != 0:
        x_weight = abs(x_steps) / (abs(x_steps) + abs(y_steps))
        y_weight = abs(y_steps) / (abs(x_steps) + abs(y_steps))
        heading = 90 * y_weight + 180 * x_weight
        if x_steps < 0:
            heading = 180 - heading
        if y_steps < 0:
            heading = 360 - heading

    return heading

def move(x_steps, y_steps):
    # Get the heading, weighted by the amount to move in each direction
    heading = get_angle(x_steps, y_steps)
    # Set the heading of the turtle
    t.setheading(heading)

    # Get the distance to move
    distance = (abs(x_steps) + abs(y_steps)) * (0.45 if pen_is_down else 1.5)

    # Move the turtle
    t.forward(distance)
    
    # Check that the turtle is still in the window
    # If not, move it back to the bounds
    x = t.xcor()
    y = t.ycor()
    if x > MAX_X:
        x = MAX_X
        t.setx(x)
    elif x < MIN_X:
        x = MIN_X
        t.setx(x)

    if y > MAX_Y:
        y = MAX_Y
        t.sety(y)
    elif y < MIN_Y:
        y = MIN_Y
        t.sety(y)
    
    # Correct for the turtle's coordinate system
    x = x - WINDOW_TOP_X
    y = WINDOW_TOP_Y - y
    
    # Convert to mm
    x = x * 0.352777778
    y = y * 0.352777778

    plotter.goto(x, y)

def toggle_pen():
    # Toggle the pen up or down, and do the same in turtle
    global pen_is_down
    pen_is_down = not pen_is_down

    if pen_is_down:
        t.pendown()
        plotter.lower_pen()

    else:
        t.penup()
        plotter.lift_pen()

# Clear the screen and move the pen to the top left corner
def clear_screen():
    t.clear()
    t.setx(WINDOW_TOP_X)
    t.sety(WINDOW_TOP_Y)
    plotter.home_axidraw()

# Move to the top left corner
def go_top_left():
    t.setx(WINDOW_TOP_X)
    t.sety(WINDOW_TOP_Y)
    plotter.go_top_left()

# Move to the top right corner
def go_top_right():
    t.setx(WINDOW_TOP_X + WINDOW_WIDTH)
    t.sety(WINDOW_TOP_Y)
    plotter.go_top_right()

# Move to the bottom left corner
def go_bottom_left():
    t.setx(WINDOW_TOP_X)
    t.sety(WINDOW_TOP_Y - WINDOW_HEIGHT)
    plotter.go_bottom_left()

# Move to the bottom right corner
def go_bottom_right():
    t.setx(WINDOW_TOP_X + WINDOW_WIDTH)
    t.sety(WINDOW_TOP_Y - WINDOW_HEIGHT)
    plotter.go_bottom_right()

#####################################################################
# Bindings
#####################################################################
# Bind c to clear the screen
turtle.onkeypress(clear_screen, "c")

# Bind the space bar to toggle the pen
turtle.onkeypress(toggle_pen, "space")


# Bind the arrow keys to the turtle movements
keys_pressed = set()

key_directions = {
    "Up": (0, 1),
    "Down": (0, -1),
    "Left": (1, 0),
    "Right": (-1, 0)
}

def bind_key(key):
    turtle.onkeypress(lambda: keys_pressed.add(key), key)
    turtle.onkeyrelease(lambda: keys_pressed.remove(key), key)

# Bind movement keys
for key in key_directions:
    bind_key(key)

# Start listening for key inputs
turtle.listen()


#####################################################################
# Clean exit handling
#####################################################################

atexit.register(on_exit)
signal.signal(signal.SIGTERM, on_exit)
signal.signal(signal.SIGINT, on_exit)

if __name__ == "__main__":
    # Writing our own update loop so that we can check for midi messages
    while True:
        midi_update = midi.update()
        x, y = midi_update.x_change, midi_update.y_change
        
        if midi_update.pen_toggle:
            toggle_pen()
        
        if midi_update.go_home:
            clear_screen()
        elif midi_update.go_top_left:
            go_top_left()
        elif midi_update.go_top_right:
            go_top_right()
        elif midi_update.go_bottom_left:
            go_bottom_left()
        elif midi_update.go_bottom_right:
            go_bottom_right()
            

        for key in keys_pressed:
            x_step, y_step = key_directions[key]
            x += x_step * ARROW_KEY_MULTIPLIER
            y += y_step * ARROW_KEY_MULTIPLIER

        if x or y:
            move(x, y)
        
        turtle.update()
