from typing import Tuple, List

import numpy as np
from vispy import app, gloo

import constants as cn
from graphics.shaders.grid_lines import VERTEX_SHADER, FRAGMENT_SHADER


class SignalGridCanvas(app.Canvas):
    def __init__(self, rows: int = 1, cols: int = 1, length: int = 200,
                 program: gloo.Program = None, *args, **kwargs):
        """
        Creates a canvas that displays multiple signals in a grid.
        :param rows: Row count in the grid.
        :param cols: Column count in the grid.
        :param length: Length of a single sequence.
        :param program: The gloo program being used.
        """

        app.Canvas.__init__(self, *args, size=cn.DEFAULT_WINDOW_SIZE, **kwargs)
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

    def on_timer(self, _):
        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.physical_size)


def create_simple_canvas(data, length, title, standalone):
    simple_canvas = SignalGridCanvas(1, cn.SENSOR_COUNT, length, title=title, show=standalone)

    signal_ids = [simple_canvas.add_new_signals(0, i) for i in range(cn.SENSOR_COUNT)]
    for i in range(cn.SENSOR_COUNT):
        simple_canvas.set_signal_single_color(signal_ids[i][0], cn.COLORS.RED)
        simple_canvas.set_signal_single_color(signal_ids[i][1], cn.COLORS.GREEN)
        simple_canvas.set_signal_single_color(signal_ids[i][2], cn.COLORS.BLUE)

        for j in range(3):
            simple_canvas.roll_signal_values(
                signal_ids[i][j],
                data[:, i, j])

    return simple_canvas
