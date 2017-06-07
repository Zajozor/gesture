import numpy as np
from vispy import app, gloo
from threading import Thread
from numpy.random import random
from time import sleep
import serial

app.use_app('PyQt5')


vertex = """
attribute vec2 a_position;
void main (void)
{
    gl_Position = vec4(a_position, 0.0, 1);
}
"""

fragment = """
void main()
{
    gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
}
"""

program = gloo.Program(vertex, fragment)
current_data = np.zeros(1000)


def update_program_data():
    program['a_position'] = np.c_[
        np.linspace(-0.95, 1, 1000),
        current_data].astype(np.float32)
update_program_data()


class Canvas(app.Canvas):
    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        gloo.set_clear_color((1, 1, 1, 1))
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

    def on_draw(self, event):
        gloo.clear(color=True)
        program.draw('line_strip')

    def on_timer(self, event):
        update_program_data()
        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.size)


def threaded(arg):
    while True:
        global current_data
        current_data = np.roll(current_data, -1, 0)
        current_data[-1] = random()
        sleep(.05)


th = Thread(target=threaded, args=(10,), daemon=True)
th.start()

canvas = Canvas(keys='interactive', always_on_top=True)
canvas.show()
app.run()


