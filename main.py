import atexit
import turtle
import signal

from midi import MidiManager
from plotter import PlotterManager

plotter = PlotterManager()
midi = MidiManager()

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500
# Coordinates of the top left corner of the window
WINDOW_X = 0 - int(WINDOW_WIDTH / 2)
WINDOW_Y = 0 + int(WINDOW_HEIGHT / 2)

MAX_X = WINDOW_WIDTH / 2
MIN_X = 0 - MAX_X
MAX_Y = WINDOW_HEIGHT / 2
MIN_Y = 0 - MAX_Y

ARROW_KEY_MULTIPLIER = 4


# Set up the turtle window
turtle.setup(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
turtle.title("Etch-a-Sketch")
turtle.bgcolor("white")

# Create the turtle
t = turtle.Turtle()
t.pensize(5)
t.speed(0)
# Move the turtle to the top left corner of the window
t.penup()
t.setx(WINDOW_X)
t.sety(WINDOW_Y)
t.pendown()

def on_exit():
    print("Exiting...")
    plotter.on_exit()
    midi.on_exit()
    turtle.bye()

atexit.register(on_exit)
signal.signal(signal.SIGTERM, on_exit)
signal.signal(signal.SIGINT, on_exit)

def update_axidraw():
    x = t.xcor()
    y = t.ycor()
    # print(x, y)
    # Correct for the turtle's coordinate system
    x = x - WINDOW_X
    y = WINDOW_Y - y
    print(x, y)
    # Convert to mm
    x = x * 0.352777778
    y = y * 0.352777778
    # Move the AxiDraw
    plotter.moveto(x, y)

# Define the functions for moving the turtle
def move_up():
    t.setheading(90)
    t.forward(10)
    update_axidraw()

def move_down():
    t.setheading(270)
    t.forward(10)
    update_axidraw()

def move_left(steps=1):
    t.setheading(180)
    t.forward(10 * steps)
    update_axidraw()

def move_right(steps=1):
    t.setheading(0)
    t.forward(5 * steps)
    update_axidraw()

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
    distance = 1 * (abs(x_steps) + abs(y_steps))

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
    x = x - WINDOW_X
    y = WINDOW_Y - y
    
    # Convert to mm
    x = x * 0.352777778
    y = y * 0.352777778

    plotter.goto(x, y)

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

for key in key_directions:
    bind_key(key)

# Start listening for key inputs
turtle.listen()

# Writing our own update loop so that we can check for midi messages
while True:
    x, y, pen_toggle = midi.update()
    
    if pen_toggle:
        plotter.toggle_pen()

    for key in keys_pressed:
        x_step, y_step = key_directions[key]
        x += x_step * ARROW_KEY_MULTIPLIER
        y += y_step * ARROW_KEY_MULTIPLIER

    if x or y:
        move(x, y)
    
    turtle.update()
