import numpy as np
from vispy import app, gloo
from threading import Thread
import math

app.use_app('PyQt5')


vertex = """
attribute vec2 a_position;
void main (void)
{
    gl_Position = vec4(a_position, 0.0, 1.0);
}
"""

fragment = """
void main()
{
    gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
}
"""

program = gloo.Program(vertex, fragment)

program['a_position'] = np.c_[
        np.linspace(-1.0, +1.0, 1000),
        #np.random.uniform(-0.5, +0.5, 1000)].astype(np.float32)
        np.zeros(1000)].astype(np.float32)


class Canvas(app.Canvas):
    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
        self.tick = 0

    def on_draw(self, event):
        gloo.clear(color=True)
        program.draw('line_strip')

    def on_timer(self, event):
        #program['a_position'] = np.c_[
        #    np.linspace(-1.0, +1.0, 1000),
        #    np.random.uniform(-0.5, +0.5, 1000)].astype(np.float32)
        self.tick += 1 / 60.0
        c = abs(math.sin(self.tick))
        gloo.set_clear_color((c, c, c, 1))
        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.size)


def threaded(arg):
    pass

th = Thread(target=threaded, args=(10,))
th.start()
#th.join()

print(program['a_position'][0])

canvas = Canvas(keys='interactive', always_on_top=True)
canvas.show()
app.run()

