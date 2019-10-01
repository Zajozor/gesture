import numpy as np
from graphics.shaders.grid_lines import VERTEX_SHADER, FRAGMENT_SHADER
from vispy import app, gloo


class SignalCanvas(app.Canvas):
    def __init__(self, rows=1, cols=1, length=200,
                 program=gloo.Program(VERTEX_SHADER, FRAGMENT_SHADER), *args, **kwargs):
        """
        Creates a canvas that displays multiple signals in a grid.
        :param rows: Row count in the grid.
        :param cols: Column count in the grid.
        :param length: Length of a single sequence.
        :param program: The gloo program being used.
        :param args:
        :param kwargs:
        """
        app.Canvas.__init__(self, *args, **kwargs)
        gloo.set_clear_color((1, 1, 1, 1))
        gloo.set_viewport(0, 0, *self.physical_size)

        self.rows = rows
        self.cols = cols
        self.length = length

        self.program = program
        self.signal_positions = np.empty(0, dtype=np.float32)
        self.signal_colors = np.empty((0, 3), dtype=np.float32)
        self.indices = np.empty((0, 3), dtype=np.float32)
        self._update_program_data()

        self.program['u_scale'] = (1., 1.)
        self.program['u_size'] = (rows, cols)
        self.program['u_n'] = length

        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
        self.show()

    def _update_program_data(self):
        self.program['a_position'] = self.signal_positions
        self.program['a_color'] = self.signal_colors
        self.program['a_index'] = self.indices

    def add_signal(self, row, col):
        """
        Adds a signal into given row and column.
        :return: ID used to set signal data later on.
        """
        assert 0 <= row < self.rows
        assert 0 <= col < self.cols
        signal_id = self.indices.shape[0]
        self.indices = np.concatenate([self.indices,
                                       np.c_[
                                           np.repeat(col, self.length),
                                           np.repeat(row, self.length),
                                           np.arange(self.length)
                                       ].astype(np.float32),
                                       np.array([[-1, -1, 0]]).astype(np.float32)])
        # One more point is added here at an invalid positions in order to enable clipping with line_strip
        self.signal_positions = np.concatenate([self.signal_positions, np.zeros(self.length + 1).astype(np.float32)])
        self.signal_colors = np.concatenate([self.signal_colors, np.zeros((self.length + 1, 3)).astype(np.float32)])
        self._update_program_data()
        return signal_id

    def add_signal_multi(self, row, col, count=3):
        """
        Adds multiple signals into given row and column.
        :return: tuple of IDs used to set signal data later on.
        """
        return tuple([self.add_signal(row, col) for _ in range(count)])

    def set_signal_data(self, signal_id, positions=None, colors=None):
        if positions is not None:
            self.signal_positions[signal_id: signal_id + self.length] = positions
        if colors is not None:
            self.signal_colors[signal_id: signal_id + self.length] = colors
        self._update_program_data()

    def set_signal_data_multi(self, signal_ids, positions=None, colors=None):
        count = len(signal_ids)
        if positions is not None:
            assert count == positions.shape[0]
            for i in range(count):
                self.signal_positions[signal_ids[i]: signal_ids[i] + self.length] = positions[i]
        if colors is not None:
            assert count == colors.shape[0]
            for i in range(count):
                self.signal_colors[signal_ids[i]: signal_ids[i] + self.length] = colors[i]
        self._update_program_data()

    def roll_signal_data(self, signal_id, positions=None, colors=None):
        # TODO optimize rolling
        if positions is not None:
            roll_count = positions.shape[0]
            assert roll_count < self.length
            self.signal_positions[signal_id: signal_id + self.length] = np.concatenate([
                self.signal_positions[signal_id + roll_count: signal_id + self.length],
                positions
            ])
        if colors is not None:
            roll_count = colors.shape[0]
            assert roll_count < self.length
            self.signal_colors[signal_id: signal_id + self.length] = np.concatenate([
                self.signal_colors[signal_id + roll_count: signal_id + self.length],
                colors
            ])
        self._update_program_data()

    def roll_signal_data_multi(self, signal_ids, positions=None, colors=None):
        # TODO optimize rolling and reuse the single method
        count = len(signal_ids)
        if positions is not None:
            assert count == positions.shape[0]
            for i in range(count):
                roll_count = positions.shape[1]
                signal_id = signal_ids[i]
                assert roll_count < self.length
                self.signal_positions[signal_id: signal_id + self.length] = np.concatenate([
                    self.signal_positions[signal_id + roll_count: signal_id + self.length],
                    positions[i]
                ])
        if colors is not None:
            assert count == colors.shape[0]
            for i in range(count):
                roll_count = colors.shape[1]
                signal_id = signal_ids[i]
                assert roll_count < self.length
                self.signal_colors[signal_id: signal_id + self.length] = np.concatenate([
                    self.signal_colors[signal_id + roll_count: signal_id + self.length],
                    colors[i]
                ])
        self._update_program_data()

    def on_draw(self, _):
        gloo.clear(color=True)
        self.program.draw('line_strip')

    def on_timer(self, _):
        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.physical_size)


if __name__ == '__main__':
    # Running the code below shows examples of using the SignalCanvas
    c = SignalCanvas(3, 3, length=1000)

    o1 = c.add_signal(2, 2)
    o2 = c.add_signal(1, 1)
    o3 = c.add_signal(1, 1)

    o4 = c.add_signal_multi(2, 0)
    c.set_signal_data_multi(o4, colors=np.stack([
        np.tile((1., 0., 0.), (1000, 1)),
        np.tile((0., 1., 0.), (1000, 1)),
        np.tile((0., 0., 1.), (1000, 1))
    ]))

    o5 = c.add_signal_multi(0, 2)
    c.set_signal_data_multi(o5, colors=np.stack([
        np.tile((1., 0., 0.5), (1000, 1)),
        np.tile((0.5, 1., 0.), (1000, 1)),
        np.tile((0., 0.5, 1.), (1000, 1))
    ]))

    c.set_signal_data(o3, colors=np.tile((1., 0., 0.), (1000, 1)))


    def update(_):
        c.set_signal_data(o1, np.random.rand(1000))
        c.set_signal_data(o2, np.concatenate([np.random.rand(500), np.repeat(1, 500)]))
        c.set_signal_data(o3, np.concatenate([np.random.rand(500), np.repeat(1, 500)]))

        c.set_signal_data_multi(o4, positions=np.random.rand(3, 1000))
        c.roll_signal_data_multi(o5, positions=np.random.rand(3, 1))


    timer = app.Timer()
    timer.connect(update)
    timer.start()

    app.run()
