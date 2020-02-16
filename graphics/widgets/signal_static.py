import math

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication

import constants as cn


class StaticSignalWidget(pg.GraphicsView):
    def __init__(self, data: np.ndarray, length=None, rows=1, cols=None,
                 *args, **kwargs):
        """
        Creates a PlotWidget from the given data. Suitable for one-off plots.
        :param data: A three dimensional array of shape [time, sensor/signal, axis]
        :param length: length to show (calculated if None)
        :param rows: Amount of rows in the canvas.
        :param cols: Amount of columns in the canvas (calculated if None).
        """
        assert len(data.shape) == 3

        if length is None:
            length = data.shape[0]
        if cols is None:
            cols = math.ceil(data.shape[1] / rows)
        assert data.shape[2] == 3  # Three different axes

        super().__init__(background='w')

        self.data = data
        self.length = length
        self.rows = rows
        self.cols = cols
        self.graphics_layout = pg.GraphicsLayout(*args, **kwargs)
        self.setCentralItem(self.graphics_layout)

        for i in range(self.rows):
            for j in range(self.cols):
                signal = i * self.rows + j
                p = self.graphics_layout.addPlot()
                for k in range(3):
                    p.plot(self.data[:self.length, signal, k], pen=cn.COLORS.PEN_COLORS[k])
                if j > 0:
                    p.hideAxis('left')
                p.vb.setMouseEnabled(False, False)
            self.graphics_layout.nextRow()
        self.graphics_layout.setContentsMargins(0, 0, 0, 0)
        self.graphics_layout.setSpacing(0)
        # TODO possibly reduce the space taken by the axes a little more

    # # noinspection PyPep8Naming
    # def mouseDoubleClickEvent(self, event):
    #     # Opens up the data in new window to explore
    #     # TODO window is not shown for some reason
    #     win = pg.GraphicsWindow()
    #
    #     for i in range(self.rows):
    #         for j in range(self.cols):
    #             signal = i * self.rows + j
    #             p = win.addPlot()
    #             for k in range(3):
    #                 p.plot(self.data[:self.length, signal, k], pen=cn.COLORS.PEN_COLORS[k])
    #     win.show()
    #     super().mouseDoubleClickEvent(event)


# TODO use ConsoleWidget somewhere
if __name__ == '__main__':
    app = QApplication([])
    main_widget = StaticSignalWidget(np.random.rand(150, 5, 3))
    main_widget.show()
    app.exec_()
