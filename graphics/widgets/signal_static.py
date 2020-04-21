import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

import constants as cn


class StaticSignalWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(600, 150)

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.canvas = FigureCanvas(Figure(figsize=(5, 1), tight_layout=True))
        self.canvas.figure.patch.set_linewidth(3)
        # TODO close figure!
        layout.addWidget(self.canvas)

        self.data = np.empty(0)
        self.mouse_press_callback = None
        self.canvas.mpl_connect('button_press_event', self.figure_on_click)

    def plot_data(self, data, draw_stride=1):
        self.canvas.figure.clear()
        if data is None or data.shape == (0,):
            self.set_background('gray')
            self.canvas.draw()
            return
        self.set_background('white')

        self.data = data.copy()
        draw_data = self.data[::draw_stride] * cn.SENSOR_DRAW_COEFFICIENT + cn.SENSOR_DRAW_OFFSET

        assert len(draw_data.shape) == 3
        length = draw_data.shape[0]
        cols = draw_data.shape[1]
        assert draw_data.shape[2] == cn.SENSOR_CHANNEL_COUNT

        # [time, sensor, channel]
        xs = np.arange(length)
        axs = self.canvas.figure.subplots(1, cols, gridspec_kw={'wspace': 0})

        for i, ax in enumerate(axs):
            for j in range(cn.SENSOR_CHANNEL_COUNT):
                ax.plot(xs, draw_data[:, i, j], c=cn.COLORS.DEFAULT_SIGNAL_COLORS[j], linewidth=0.6)
            ax.set_ylim(-1, 1)
            ax.set_xticks(())
            ax.set_yticks(())
            ax.set_title(f'{data.shape}')

        self.canvas.figure.tight_layout()
        for ax in axs:
            ax.figure.canvas.draw()

    def figure_on_click(self, e):
        if self.mouse_press_callback:
            self.mouse_press_callback(e)

    def set_background(self, color):
        self.canvas.figure.patch.set_facecolor(color)

    def set_border_color(self, color):
        self.canvas.figure.patch.set_edgecolor(color)
        self.canvas.draw()


# TODO use ConsoleWidget somewhere
if __name__ == '__main__':
    app = QApplication([])
    main_widget = StaticSignalWidget()
    main_widget.plot_data(np.random.rand(30, 5, 6) * 2 - 1)


    def redraw():
        main_widget.plot_data(np.random.rand(20, 5, 6) * 2 - 1)
        QTimer.singleShot(600, redraw)


    redraw()
    main_widget.show()
    app.exec_()
