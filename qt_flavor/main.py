import sys

import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QDesktopWidget, QLabel, \
    QScrollArea
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from input_parser import InputParser

from constants import *
from qt_flavor.interpreters.min_square.min_square import MinSquareInterpreter

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Init the sensor window, resize and reposition
    sensor_window = QWidget()
    sensor_window.show()
    sensor_window.setWindowTitle(SENSOR_WINDOW_TITLE)
    sensor_window.resize(SENSOR_WINDOW_WIDTH, SENSOR_WINDOW_HEIGHT)

    frame_geometry = sensor_window.frameGeometry()
    center_point = QDesktopWidget().availableGeometry().center()
    frame_geometry.moveCenter(center_point)
    sensor_window.move(frame_geometry.topLeft())

    # Init the sensor window layout and components
    layout = QGridLayout()
    sensor_window.setLayout(layout)

    sensor_plot = pg.PlotWidget()
    layout.addWidget(sensor_plot, 0, 0, 1, 5)
    input_control_widget = QWidget()
    layout.addWidget(input_control_widget, 1, 0)

    log_widget = QLabel("Status messages will be shown here:\n")
    log_widget.setWordWrap(False)

    log_scroll_area = QScrollArea()
    log_scroll_area.setWidget(log_widget)
    layout.addWidget(log_scroll_area, 1, 1)

    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(1, 3)
    layout.setColumnStretch(2, 1)

    input_parser = InputParser(sensor_plot, input_control_widget, log_widget)

    interpreters = [MinSquareInterpreter, ]
    interpreter_chooser = QWidget()
    layout.addWidget(interpreter_chooser, 1, 2)
    interpreter_chooser_layout = QVBoxLayout()
    interpreter_chooser.setLayout(interpreter_chooser_layout)

    interpreter_listbox = QListWidget()
    interpreter_chooser_layout.addWidget(interpreter_listbox)

    interpreter_count = 0

    def add_interpreter():
        global interpreter_count
        j = interpreters[interpreter_listbox.currentIndex().row()](interpreter_count)
        input_parser.add_target(interpreter_count, j.latest_data)
        j.set_close_interpreter(lambda: input_parser.remove_target(j.log_id))
        interpreter_count += 1

    for i in interpreters:
        interpreter_listbox.addItem(i.get_name())

    interpreter_add_button = QPushButton('Add this')
    interpreter_chooser_layout.addWidget(interpreter_add_button)
    interpreter_add_button.clicked.connect(add_interpreter)


    def close_event(self, e):
        input_parser.try_reading = False
    import types
    sensor_window.closeEvent = types.MethodType(close_event, sensor_window)

    sys.exit(app.exec_())
