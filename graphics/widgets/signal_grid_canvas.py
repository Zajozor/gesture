from typing import Tuple, List

import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from vispy import app, gloo
from vispy.visuals import transforms, LineVisual

import constants as cn
from graphics.shaders.grid_lines import VERTEX_SHADER, FRAGMENT_SHADER


class SignalGridCanvas(app.Canvas):
    def __init__(self, rows: int = 1, cols: int = 1, length: int = 200,
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

        self._timer: app.Timer = app.Timer('auto', connect=self.on_timer, start=True)

        self.visuals = []

        if show_grid:
            # noinspection PyTypeChecker
            self.visuals += [
                                LineVisual(np.array([[0, (i + 1) / rows], [1, (i + 1) / rows]]))
                                for i in range(rows - 1)
                            ] + [
                                LineVisual(np.array([[(i + 1) / cols, 0], [(i + 1) / cols, 1]]))
                                for i in range(cols - 1)
                            ]

    def _update_program_indices(self):
        """
        Called to pass new index data inside the numpy arrays to the gloo program
        """
        self.program['a_index'] = self.row_col_time_indices

    def _update_program_colors(self):
        self.program['a_color'] = self.signal_colors

    def _update_program_values(self):
        """
        Called to pass new data inside the numpy arrays to the gloo program
        """
        self.program['a_value'] = self.signal_values

    def _update_program(self):
        self._update_program_indices()
        self._update_program_colors()
        self._update_program_values()

    def add_new_signal(self, row: int, col: int) -> int:
        """
        Adds a signal into given row and column.
        :return: ID used to set signal data later on.
        """
        assert 0 <= row < self.rows
        assert 0 <= col < self.cols
        signal_id = self.row_col_time_indices.shape[0]
        # Add one more invalid point for clipping to indices, values and colors

        self.row_col_time_indices = np.concatenate([
            self.row_col_time_indices,
            np.c_[  # Add the (row, col, time) triples for the new signal
                np.repeat(col, self.length),
                np.repeat(row, self.length),
                np.arange(self.length)
            ].astype(np.float32),
            np.array([[-1, -1, 0]]).astype(np.float32)
        ])
        self.signal_values = np.concatenate([
            self.signal_values,
            np.zeros(self.length + 1).astype(np.float32)
        ])
        self.signal_colors = np.concatenate([
            self.signal_colors,
            np.zeros((self.length + 1, 3)).astype(np.float32)
        ])
        self._update_program()
        return signal_id

    def add_new_signals(self, row: int, col: int, count: int = 3) -> Tuple[int]:
        """
        Adds multiple signals into given row and column.
        :return: tuple of IDs used to set signal data later on.
        """
        return tuple([self.add_new_signal(row, col) for _ in range(count)])

    def set_signal_single_color(self, signal_id: int, color: Tuple[float, float, float]):
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
        # TODO optimize rolling
        roll_count = values.shape[0]
        assert roll_count <= self.length
        self.signal_values[signal_id: signal_id + self.length] = np.concatenate([
            self.signal_values[signal_id + roll_count: signal_id + self.length],
            values
        ])
        self._update_program_values()

    def roll_signal_values_multi(self, signals: List[Tuple[int, np.ndarray]]):
        for signal_id, values in signals:
            self.roll_signal_values(signal_id, values)

    # TODO add removed methods

    def on_draw(self, _):
        gloo.clear(color=True)
        self.program.draw('line_strip')
        for visual in self.visuals:
            visual.draw()

    def on_timer(self, _):
        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.physical_size)
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        for visual in self.visuals:
            visual.transform = transforms.STTransform(scale=(vp[2], vp[3], 1.))
            visual.transforms.configure(canvas=self, viewport=vp)

    @staticmethod
    def canvas_from_data(data: np.ndarray, length=None, title=None, rows=1, cols=None):
        """
        Creates a canvas from the given data. Suitable for one-off canvas creation.
        :param data: A numpy array, [length, sensor_count, colors]
        :param length: Length - if not specified is calculated from the received data.
        :param title: Title of the window (applicable if shown).
        :param rows: Amount of rows in the canvas.
        :param cols: Amount of columns in the canvas.
        :return: canvas itself
        """
        assert len(data.shape) == 3
        if length is None:
            length = data.shape[0]
        if cols is None:
            cols = data.shape[1]
        assert data.shape[2] == 3  # Three different colors

        canvas = SignalGridCanvas(rows, cols, length, title=title)

        for i in range(cols):
            signal_id = canvas.add_new_signals(0, i)
            for j in range(3):
                canvas.set_signal_single_color(signal_id[j], cn.COLORS.DEFAULT_SIGNAL_COLORS[j])
                canvas.roll_signal_values(signal_id[j], data[:, i, j])

        return canvas


if __name__ == '__main__':
    q_app = QApplication([])

    win = QWidget()
    layout = QHBoxLayout()
    win.setLayout(layout)

    c1 = SignalGridCanvas(3, 3, 100)
    s1 = c1.add_new_signal(0, 1)
    c1.set_signal_values(s1, np.random.rand(100))

    s2 = c1.add_new_signal(1, 1)
    c1.set_signal_values(s2, np.tile(0.3, 100))
    c1.set_signal_single_color(s2, (0.9, 0.2, 0.3))
    layout.addWidget(c1.native)

    c2 = SignalGridCanvas(3, 1, 50)
    s3 = c2.add_new_signals(1, 0)
    c2.set_signal_single_color(s3[1], (0, 1, 0))
    c2.roll_signal_values_multi([s, np.random.rand(50)] for s in s3)
    layout.addWidget(c2.native)

    c3 = SignalGridCanvas.canvas_from_data(np.random.rand(300, 5, 3))
    layout.addWidget(c3.native)

    win.show()
    q_app.exec_()
