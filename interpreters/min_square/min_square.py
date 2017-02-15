from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer
from constants import *
from interpreters.interpreter import Interpreter
import pyqtgraph as pg
import logging

from interpreters.min_square.min_square_gesture import MinSquareGesture
from qlabel_log_handler import QLabelHandler


class MinSquareInterpreter(Interpreter):

    @staticmethod
    def get_name():
        return MIN_SQUARE_INTERPRETER_NAME

    def __init__(self, int_id=0):
        self.interpreter_window = QWidget()
        self.interpreter_window.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.interpreter_window.show()
        self.interpreter_window.setWindowTitle(self.get_name())
        self.interpreter_window.resize(INTERPRETER_WINDOW_WIDTH, INTERPRETER_WINDOW_HEIGHT)

        self.layout = QGridLayout()
        self.interpreter_window.setLayout(self.layout)

        self.interpret_plot = pg.PlotWidget()
        self.current_interpret_gesture = MinSquareGesture(
            DEFAULT_MIN_SQUARE_GESTURE_LENGTH, self.interpret_plot)
        self.layout.addWidget(self.interpret_plot, 0, 1)

        record_control_widget = QWidget()
        self.layout.addWidget(record_control_widget, 0, 0)

        log_widget = QLabel("Status messages will be shown here:\n")
        log_widget.setWordWrap(False)

        log_scroll_area = QScrollArea()
        log_scroll_area.setWidget(log_widget)
        self.layout.addWidget(log_scroll_area, 0, 2)
        self.log_id = int_id
        self.logger = logging.getLogger('min_square' + str(int_id))
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(QLabelHandler(log_widget))

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 3)
        self.layout.setColumnStretch(2, 2)

        saved_gestures_widget = QWidget()
        self.saved_gestures_layout = QHBoxLayout()
        saved_gestures_widget.setLayout(self.saved_gestures_layout)
        self.layout.addWidget(saved_gestures_widget, 1, 0, 1, 3)

        record_control_layout = QVBoxLayout()
        record_control_widget.setLayout(record_control_layout)

        self.start_recording_button = QPushButton('Record')
        record_control_layout.addWidget(self.start_recording_button)
        self.start_recording_button.clicked.connect(self.record)

        self.interpret_checkbox = QCheckBox('Interpret')
        record_control_layout.addWidget(self.interpret_checkbox)
        self.interpret_checkbox.stateChanged.connect(self.interpret_change)

        self.max_distance_label = QLabel('Max distance')
        self.max_distance_edit = QLineEdit()
        self.max_distance_edit.setText(str(DEFAULT_MIN_SQUARE_THRESHOLD))
        self.max_distance = DEFAULT_MIN_SQUARE_THRESHOLD
        self.gesture_length_label = QLabel('Gesture length')
        self.gesture_length_edit = QLineEdit()
        self.gesture_length_edit.setText(str(DEFAULT_MIN_SQUARE_GESTURE_LENGTH))
        self.gesture_length = DEFAULT_MIN_SQUARE_GESTURE_LENGTH

        self.set_max_distance_button = QPushButton("Set max distance")
        self.set_max_distance_button.clicked.connect(self.on_click_max_distance)
        self.set_gesture_length_button = QPushButton("Set gesture length")
        self.set_gesture_length_button.clicked.connect(self.on_click_gesture_length)

        record_control_layout.addWidget(self.max_distance_label)
        record_control_layout.addWidget(self.max_distance_edit)
        record_control_layout.addWidget(self.set_max_distance_button)
        record_control_layout.addWidget(self.gesture_length_label)
        record_control_layout.addWidget(self.gesture_length_edit)
        record_control_layout.addWidget(self.set_gesture_length_button)

        self.close_button = QPushButton('Close Interpreter')
        record_control_layout.addWidget(self.close_button)
        self.close_button.clicked.connect(self.close_interpreter)

        self.refresh_gesture_distances_timer = QTimer()
        self.refresh_gesture_distances_timer.timeout.connect(self.refresh_gesture_distances)
        self.refresh_gesture_distances_timer.start(25)

    # used to stop receiving data from input_parser
    on_close_function = None

    def on_click_max_distance(self):
        self.max_distance = int(self.max_distance_edit.text())

    def on_click_gesture_length(self):
        self.gesture_length = int(self.gesture_length_edit.text())

        self.current_interpret_gesture = MinSquareGesture(
            self.gesture_length, self.interpret_plot)

    def set_close_interpreter(self, f):
        self.on_close_function = f

    def close_interpreter(self):
        self.on_close_function()
        self.interpreter_window.close()

    def interpret_change(self):
        self.interpreting = self.interpret_checkbox.isChecked()

    recording = False
    interpreting = False

    current_record_gesture = None
    saved_gestures = []

    def refresh_gesture_distances(self):
        if self.interpreting:
            self.current_interpret_gesture.update_plot()

        for g in self.saved_gestures:
            g.get_distance(self.current_interpret_gesture)

    def latest_data(self, data):
        if self.interpreting:
            self.current_interpret_gesture.push_data(data[0], data[1], data[2])

        if self.recording:
            self.current_record_gesture.push_data(data[0], data[1], data[2])
            self.current_record_gesture.update_plot()

            if self.current_record_gesture.data_pushed == self.gesture_length:
                self.recording = False
                self.start_recording_button.setDisabled(False)
                self.logger.info('Recorded successfully')

    def record(self):
        self.start_recording_button.setDisabled(True)

        self.logger.info('Started recording')

        current_gesture_layout = QVBoxLayout()
        current_gesture_widget = QWidget()
        current_gesture_widget.setLayout(current_gesture_layout)

        current_plot_widget = pg.PlotWidget()
        current_gesture_layout.addWidget(current_plot_widget)

        current_plot_label = QLabel()
        current_gesture_layout.addWidget(current_plot_label)
        self.saved_gestures_layout.addWidget(current_gesture_widget)

        self.current_record_gesture = MinSquareGesture(self.gesture_length,
                                                       current_plot_widget,
                                                       current_plot_label,
                                                       self.max_distance)
        self.saved_gestures.append(self.current_record_gesture)

        self.recording = True









