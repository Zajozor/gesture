from vispy import gloo
import numpy as np

from graphics.shaders.simple_point import VERTEX_SHADER, FRAGMENT_SHADER
from graphics.simple_canvas import SimpleCanvas


class StatusCanvas(SimpleCanvas):
    def __init__(self, data_reader):
        super().__init__(keys='interactive', always_on_top=False, position=(850, 100))
        self.data_reader = data_reader
        self.programs = [gloo.Program(VERTEX_SHADER, FRAGMENT_SHADER) for _ in range(3)]
        self.mapping = np.linspace(-0.95, 0.95, 1000)
        self.current_colors = np.array([[[1, 0, 0]] * 1000, [[0, 1, 0]] * 1000, [[0, 0, 1]] * 1000]).astype(np.float32)

        self.draw_callback = self.draw_status_data
        self.update_callback = self.update_status_data

        self.update_callback()  # Call it for the first time, so programs have some data at start

    def update_status_data(self):
        for i in range(len(self.programs)):
            self.programs[i]['positions'] = np.c_[
                self.mapping,
                self.data_reader.current_data[i]].astype(np.float32)
            self.programs[i]['colors'] = self.current_colors[i]

    def draw_status_data(self):
        for p in self.programs:
            p.draw('line_strip')


status_canvas = SimpleCanvas()