import numpy as np
from constants import *
from PyQt5.QtCore import Qt


class MinSquareGesture:
    data_x = np.empty(0, dtype=int)
    data_y = np.empty(0, dtype=int)
    data_z = np.empty(0, dtype=int)

    rel_dist_data = np.empty(0, dtype=int)

    def __init__(self, length, plot_widget=None, diff_label=None, threshold=DEFAULT_MIN_SQUARE_THRESHOLD):
        self.set_data(np.zeros(length), np.zeros(length), np.zeros(length))
        self.plot_widget = plot_widget
        self.threshold = threshold
        self.rel_dist_data = np.zeros(length)
        if self.plot_widget:
            self.curve_x = self.plot_widget.plot(self.data_x, pen=SENSOR_X_COLOR)
            self.curve_y = self.plot_widget.plot(self.data_y, pen=SENSOR_Y_COLOR)
            self.curve_z = self.plot_widget.plot(self.data_z, pen=SENSOR_Z_COLOR)
            self.rel_curve = self.plot_widget.plot(self.rel_dist_data, pen=REL_DIST_COLOR)
        self.diff_label = diff_label
        if self.diff_label:
            self.diff_label.setText('0')
            self.diff_label.setTextFormat(Qt.RichText)

    # def __init__(self, data_x, data_y, data_z):
    #    self.set_data(data_x, data_y, data_z)

    def set_data(self, data_x, data_y, data_z):
        self.data_x = data_x
        self.data_y = data_y
        self.data_z = data_z

    def get_distance(self, gesture):
        x_dist = np.linalg.norm(gesture.data_x - self.data_x)
        y_dist = np.linalg.norm(gesture.data_y - self.data_y)
        z_dist = np.linalg.norm(gesture.data_z - self.data_z)

        rel_x_dist = x_dist / (1+np.linalg.norm(self.data_x))
        rel_y_dist = y_dist / (1+np.linalg.norm(self.data_y))
        rel_z_dist = z_dist / (1+np.linalg.norm(self.data_z))
        if self.diff_label:
            text = ''

            text_color = 'red'
            if x_dist+y_dist+z_dist < self.threshold:
                text_color = 'green'

            text += ' '.join(('<font color="{}"'.format(text_color),
                              '>x~', str(x_dist),
                              'y~', str(y_dist),
                              'z~', str(z_dist),
                              '</font><br/>'))

            rel_text_color = 'red'
            overall_rel_dist = rel_x_dist+rel_y_dist+rel_z_dist
            if overall_rel_dist < 0.75:
                rel_text_color = 'green'

            self.rel_dist_data[:-1] = self.rel_dist_data[1:]
            self.rel_dist_data[-1] = overall_rel_dist
            self.rel_curve.setData(self.rel_dist_data)

            text += ' '.join(('<font color="{}"'.format(rel_text_color),
                              '>x~', str(rel_x_dist),
                              'y~', str(rel_y_dist),
                              'z~', str(rel_z_dist),
                              '</font><br />'))

            text += str(overall_rel_dist)

            self.diff_label.setText(text)

        return x_dist, y_dist, z_dist

    # overall through time
    data_pushed = 0

    def push_data(self, data_x, data_y, data_z):
        self.data_pushed += 1
        self.data_x[:-1] = self.data_x[1:]
        self.data_y[:-1] = self.data_y[1:]
        self.data_z[:-1] = self.data_z[1:]

        self.data_x[-1] = data_x
        self.data_y[-1] = data_y
        self.data_z[-1] = data_z

    def update_plot(self):
        if self.plot_widget:
            self.curve_x.setData(self.data_x)
            self.curve_y.setData(self.data_y)
            self.curve_z.setData(self.data_z)
