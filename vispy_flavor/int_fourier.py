import numpy as np
from vispy import app, gloo
from threading import Thread
import math


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


class GestureCanvas(app.Canvas):
    def __init__(self, gesture_size, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        gloo.set_clear_color((1, 1, 1, 1))

        self.gesture_size = gesture_size
        self.current_data = np.zeros((self.gesture_size, 2)).astype(np.float32)

        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
        self.gesture_program = gloo.Program(vertex, fragment)
        self.gesture_program['positions'] = self.current_data
        self.gesture_program['colors'] = np.zeros((self.gesture_size, 3)).astype(np.float32)

    def on_draw(self, event):
        gloo.clear(color=True)
        self.gesture_program.draw('points')

    phase = 1

    def on_timer(self, event):
        self.gesture_program['positions'] = self.current_data
        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.size)

    def get_from_queue(self, queue):
        v_x = 0
        v_y = 0
        while True:
            a = queue.get()
            v_x += math.trunc(a[0]/10)
            v_y += math.trunc(a[1]/10)
            self.current_data[self.phase][0] = self.current_data[self.phase-1][0] + v_x/10000000.0
            self.current_data[self.phase][1] = self.current_data[self.phase-1][1] + v_y/10000000.0
            if self.phase % 100 == 0:
                print(a[0], a[1], v_x, v_y, self.current_data[self.phase][0], self.current_data[self.phase][1])

            self.phase += 1
            if self.phase >= self.gesture_size:
                self.current_data = np.zeros((self.gesture_size, 2)).astype(np.float32)
                self.phase = 1
                v_x = 0
                v_y = 0


def entry_2d_gesture_display(queue, gesture_size=500):
    canvas = GestureCanvas(gesture_size, keys='interactive', always_on_top=True, title='a', position=(45, 100))

    th = Thread(target=canvas.get_from_queue, args=(queue, ), daemon=True)
    th.start()

    canvas.show()
    app.run()
    pass
