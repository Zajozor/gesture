from typing import Tuple

import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from vispy import app, gloo
from vispy.visuals import transforms, InfiniteLineVisual

import constants as cn
from graphics.shaders.grid_lines import VERTEX_SHADER, FRAGMENT_SHADER


class DynamicSignalWidget(app.Canvas):
    def __init__(self, rows: int = 1, cols: int = cn.SENSOR_COUNT, length: int = 100,
                 program: gloo.Program = None, show_grid=True, *args, **kwargs):
        """
        Creates a canvas that displays multiple signals in a grid.
        :param rows: Row count in the grid.
        :param cols: Column count in the grid.
        :param length: Length of a single sequence.
        :param program: The gloo program being used.
        """
        super().__init__(*args, size=cn.DEFAULT_WINDOW_SIZE, **kwargs)
        gloo.set_clear_color((1, 1, 1, 1))
        gloo.set_viewport(0, 0, *self.physical_size)
        self.native.setMinimumSize(300, 150)

        self.rows: int = rows
        self.cols: int = cols
        self.length: int = length

        self.program: gloo.Program = program if program else gloo.Program(VERTEX_SHADER, FRAGMENT_SHADER)
        self.signal_values: np.ndarray = np.empty(0, dtype=np.float32)
        self.signal_colors: np.ndarray = np.empty((0, 3), dtype=np.float32)
        self.row_col_time_indices: np.ndarray = np.empty((0, 3), dtype=np.float32)

        self._update_program()

        self.program['u_scale'] = (1., 1.)
        self.program['u_size'] = (rows, cols)
        self.program['u_n'] = length

        self._timer: app.Timer = app.Timer(connect=self.update, start=True)

        self.connect(self.on_close)

        self.visuals = []
        if show_grid:
            for i in range(cols - 1):
                self.visuals.append(InfiniteLineVisual((i + 1) / cols, color=(0, 0, 0, 1)))
            for i in range(rows - 1):
                self.visuals.append(InfiniteLineVisual((i + 1) / rows, vertical=False, color=(0, 0, 0, 1)))

    def _update_program_colors(self):
        self.program['a_color'] = self.signal_colors

    def _update_program_values(self):
        self.program['a_value'] = self.signal_values

    def _update_program(self):
        self.program['a_index'] = self.row_col_time_indices
        self._update_program_colors()
        self._update_program_values()

    def add_new_signal(self, row: int, col: int) -> int:
        """
        Adds a signal into given row and column. We add one additional sentinel to help with clipping.
        :return: ID used to set signal data later on.
        """
        assert 0 <= row < self.rows
        assert 0 <= col < self.cols
        signal_id = self.row_col_time_indices.shape[0]

        self.row_col_time_indices = np.concatenate((
            self.row_col_time_indices,
            np.c_[  # Add the (row, col, time) triples for the new signal
                np.repeat(col, self.length),
                np.repeat(row, self.length),
                np.arange(self.length)
            ].astype(np.float32),
            np.array([[-1, -1, 0]]).astype(np.float32)  # Sentinel to break the line
        ))
        self.signal_values = np.concatenate((
            self.signal_values,
            np.zeros(self.length + 1).astype(np.float32)
        ))
        self.signal_colors = np.concatenate((
            self.signal_colors,
            np.zeros((self.length + 1, 3)).astype(np.float32)
        ))
        self._update_program()
        return signal_id

    def set_signal_color(self, signal_id: int, color: Tuple[float, float, float]):
        self.set_signal_colors(signal_id, np.tile(color, (self.length, 1)))

    def set_signal_colors(self, signal_id: int, colors: np.ndarray):
        assert len(colors) == self.length
        self.signal_colors[signal_id: signal_id + self.length] = colors
        self._update_program_colors()

    def set_signal_values(self, signal_id: int, values: np.ndarray):
        assert len(values) == self.length
        self.signal_values[signal_id: signal_id + self.length] = values
        self._update_program_values()

    def roll_signal_values(self, signal_id: int, values: np.ndarray):
        roll_count = values.shape[0]
        self.signal_values[signal_id: signal_id + self.length] = np.concatenate((
            self.signal_values[signal_id + roll_count: signal_id + self.length],
            values
        ))
        self._update_program_values()

    def on_draw(self, _):
        gloo.clear(color=True)
        self.program.draw('line_strip')
        for visual in self.visuals:
            visual.draw()

    def on_close(self):
        self._timer.stop()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.physical_size)
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        for visual in self.visuals:
            # TODO on Retina display, this needs to be 0.5, due to Hi-DPI, otherwise
            # lines are not shown where expected
            scale = 1
            visual.transform = transforms.STTransform(scale=(vp[2] * scale, vp[3] * scale, 1.))
            visual.transforms.configure(canvas=self, viewport=vp)


if __name__ == '__main__':
    q_app = QApplication([])

    win = QWidget()
    layout = QHBoxLayout()
    win.setLayout(layout)

    c1 = DynamicSignalWidget(3, 3)
    s1 = c1.add_new_signal(0, 1)
    c1.set_signal_values(s1, np.random.rand(100))

    s2 = c1.add_new_signal(1, 1)
    c1.set_signal_values(s2, np.tile(0.3, 100))
    c1.set_signal_color(s2, (0.9, 0.2, 0.3))


    def change_c2(_):
        c1.set_signal_values(s1, np.random.rand(100))
        c1.roll_signal_values(s2, np.random.rand(10))


    timer = app.Timer(connect=change_c2, start=True)
    layout.addWidget(c1.native)

    win.show()
    q_app.exec_()
