import numpy as np
from vispy import app, gloo
from threading import Thread
from time import sleep
import queue
import math
import scipy.spatial
from vispy.visuals import TextVisual
from vispy.visuals.transforms import TransformSystem


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


class FourierCanvas(app.Canvas):
    def __init__(self, gesture_size, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        gloo.set_clear_color((1, 1, 1, 1))

        self.gesture_size = gesture_size

        self.loaded_data = np.zeros((3, self.gesture_size)).astype(np.float32)
        self.loaded_colors = np.array([[[1, 0, 0]] * self.gesture_size,
                                       [[0, 1, 0]] * self.gesture_size,
                                       [[0, 0, 1]] * self.gesture_size]).astype(np.float32)
        self.mapping = np.linspace(-0.95, 0.95, self.gesture_size)
        self.loaded_fourier = np.zeros((3, self.gesture_size)).astype(np.complex128)

        self.current_data = np.zeros((3, self.gesture_size)).astype(np.float32)
        self.current_fourier = np.zeros((3, self.gesture_size)).astype(np.complex128)

        self.distances = np.zeros(3)
        self.dist_text = TextVisual('init')
        self.dist_text.pos = 250, 50
        self.dist_program = gloo.Program(vertex, fragment)
        self.dist_data = np.zeros(gesture_size).astype(np.float32)
        self.dist_colors = np.array([[0, 0, 0]] * self.gesture_size).astype(np.float32)

        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
        self.gesture_programs = [gloo.Program(vertex, fragment) for i in range(3)]
        self.update_program_data()
        self.transform_system = TransformSystem(self)

    def update_program_data(self):
        for i in range(len(self.gesture_programs)):
            self.gesture_programs[i]['positions'] = np.c_[
                self.mapping,
                self.loaded_data[i]].astype(np.float32)
            self.gesture_programs[i]['colors'] = self.loaded_colors[i]
        self.dist_program['positions'] = np.c_[
            self.mapping,
            self.dist_data].astype(np.float32)
        self.dist_program['colors'] = self.dist_colors

        self.dist_text.text = '{} {} {} {}'.format(format(np.sum(self.distances), '.1f'),
                                                   format(self.distances[0], '.1f'),
                                                   format(self.distances[1], '.1f'),
                                                   format(self.distances[2], '.1f'))

    def on_draw(self, event):
        gloo.clear(color=True)
        for p in self.gesture_programs:
            p.draw('line_strip')
        self.dist_program.draw('line_strip')

        self.dist_text.draw(self.transform_system)

    def on_timer(self, event):
        self.update_program_data()
        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.size)

    recording = False
    recording_phase = 0

    def on_key_press(self, event):
        print(event.key.name)
        if event.key.name == "Space" and not self.recording:
            self.recording = True
            self.recording_phase = 0

    def get_from_queue(self, queue):
        c = 10000.0
        c_dist = 1.3
        #c_dist = 300
        part_dist = 32

        while True:
            if not self.recording:
                try:
                    while True:
                        a = queue.get(block=False)

                        self.current_data = np.roll(self.current_data, -1, 1)
                        for i in range(3):
                            self.current_data[i][-1] = a[i]/c

                except Exception as e: # Queue empty exception without valid naming, maybe format error on data
                        pass

                for i in range(3):
                    self.current_fourier[i] = np.fft.fft(self.current_data[i])
                    self.distances[i] = scipy.spatial.distance.cosine(
                        abs(self.current_fourier[i][:self.gesture_size//part_dist]),
                        abs(self.loaded_fourier[i][:self.gesture_size//part_dist]))
                    #self.distances[i] = np.linalg.norm(
                    #   self.current_fourier[i][:self.gesture_size//part_dist] -
                    #   self.loaded_fourier[i][:self.gesture_size//part_dist])

                self.dist_data = np.roll(self.dist_data, -1, 0)
                self.dist_data[-1] = np.sum(self.distances)/c_dist

                sleep(.05)
                continue

            while self.recording_phase < self.gesture_size:
                a = queue.get() # three floats

                try:
                    for i in range(3):
                        self.loaded_data[i][self.recording_phase] = a[i] / c
                except:
                    print('format error on fourier')

                self.recording_phase += 1
                sleep(.005)

            for i in range(3):
                self.loaded_fourier[i] = np.fft.fft(self.loaded_data[i])
            self.recording = False


def entry_fourier_display(queue, gesture_size=500):
    canvas = FourierCanvas(gesture_size, keys='interactive', always_on_top=False, title='Fourier', position=(50, 150))

    th = Thread(target=canvas.get_from_queue, args=(queue, ), daemon=True)
    th.start()

    canvas.show()
    app.run()
    pass
