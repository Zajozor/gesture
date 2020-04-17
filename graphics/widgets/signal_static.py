import math

import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

import constants as cn


class StaticSignalWidget(pg.GraphicsView):
    def __init__(self, *args, **kwargs):
        """
        Creates a PlotWidget. Suitable for one-off plots.
        To actually show some data, the plot_data method needs to be used.
        """
        super().__init__(background='w')
        self.graphics_layout = pg.GraphicsLayout(*args, **kwargs)
        self.setCentralItem(self.graphics_layout)

        self.setMinimumSize(600, 150)
        self.graphics_layout.setContentsMargins(0, 0, 0, 0)
        self.graphics_layout.setSpacing(0)
        # TODO possibly reduce the space taken by the axes a little more
        self.mouse_press_callback = None
        self.data = np.empty(0)

    def plot_data(self, data: np.ndarray, length=None, rows=1, cols=None):
        """
        :param data: A three dimensional array of shape [time, sensor/signal, channel/axis]
        :param length: length to show (calculated if None)
        :param rows: Amount of rows in the canvas.
        :param cols: Amount of columns in the canvas (calculated if None)
        """
        self.graphics_layout.clear()
        self.setBackground('w')
        if data is None or data.shape == (0,):
            self.graphics_layout.addItem(pg.LabelItem('No data'))
            self.setBackground(0.9)
            return

        self.data = data.copy()
        draw_data = self.data * cn.SENSOR_DRAW_COEFFICIENT + cn.SENSOR_DRAW_OFFSET

        assert len(draw_data.shape) == 3

        if length is None:
            length = draw_data.shape[0]
        if cols is None:
            cols = math.ceil(draw_data.shape[1] / rows)
        assert draw_data.shape[2] == cn.SENSOR_CHANNEL_COUNT

        for i in range(rows):
            for j in range(cols):
                signal = i * rows + j
                p = self.graphics_layout.addPlot()
                p.addLine(y=1 - 2 * cn.SENSOR_DRAW_COEFFICIENT[0])
                for k in range(cn.SENSOR_CHANNEL_COUNT):
                    p.plot(draw_data[:length, signal, k], pen=cn.COLORS.PEN_COLORS[k])
                p.hideAxis('left')
                p.vb.setMouseEnabled(False, False)
                p.setYRange(-1, 1)
            self.graphics_layout.nextRow()

    def mousePressEvent(self, e):
        if self.mouse_press_callback:
            self.mouse_press_callback(e)
        super().mousePressEvent(e)


# TODO use ConsoleWidget somewhere
if __name__ == '__main__':
    app = QApplication([])
    main_widget = StaticSignalWidget()
    main_widget.plot_data(np.random.rand(30, 5, 6) * 2 - 1)


    def redraw():
        main_widget.plot_data(np.random.rand(20, 5, 6) * 2 - 1)
        QTimer.singleShot(100, redraw)


    redraw()
    main_widget.show()
    app.exec_()
