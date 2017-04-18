import numpy as np
from vispy import app, gloo
from threading import Thread
from time import sleep
from vispy_flavor.input_parser import InputParser

app.use_app('PyQt5')


vertex = """
attribute vec2 positions;
attribute vec3 colors;

varying vec4 vColor;

void main ()
{
    gl_Position = vec4(positions, 0.0, 1);
    vColor = vec4(colors, 1.);
}
"""

fragment = """
varying vec4 vColor;
void main()
{
    gl_FragColor = vColor;
}
"""

programs = [gloo.Program(vertex, fragment) for i in range(3)]  # Programs for three coordinates
current_data = np.zeros((3, 1000)).astype(np.float32)
current_colors = np.array([[[1, 0, 0]]*1000, [[0, 1, 0]]*1000, [[0, 0, 1]]*1000]).astype(np.float32)
mapping = np.linspace(-0.95, 0.95, 1000)


def update_program_data():
    for i in range(len(programs)):
        programs[i]['positions'] = np.c_[
            mapping,
            current_data[i]].astype(np.float32)
        programs[i]['colors'] = current_colors[i]

update_program_data()


class Canvas(app.Canvas):
    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        gloo.set_clear_color((1, 1, 1, 1))
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

    def on_draw(self, event):
        gloo.clear(color=True)
        for p in programs:
            p.draw('line_strip')

    def on_timer(self, event):
        update_program_data()
        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.size)

input_parser = InputParser()


def threaded(arg):
    global current_data
    while True:
        data = input_parser.get_next()
        if data is not None:
            current_data = np.roll(current_data, -1, 1)
            # todo data is a tuple
            c = 10000.0
            current_data[0][-1] = data[0]/c
            current_data[1][-1] = data[1]/c
            current_data[2][-1] = data[2]/c
        sleep(.005)


th = Thread(target=input_parser.init_serial, daemon=True)
th.start()


th2 = Thread(target=threaded, args=(10,), daemon=True)
th2.start()


canvas = Canvas(keys='interactive', always_on_top=True)
canvas.show()
app.run()

input_parser.stop_serial()

