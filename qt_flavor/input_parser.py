import serial
from PyQt5.QtWidgets import QApplication
from serial import SerialException
import numpy as np
from constants import *
from PyQt5.QtWidgets import QPushButton, QLineEdit, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore
import logging
from qlabel_log_handler import QLabelHandler
import threading
import time


class InputParser:

    def __init__(self, plot_widget, input_control_widget, log_widget):
        self.plot_widget = plot_widget
        self.plot_widget.setDownsampling(mode='peak')
        self.plot_widget.setClipToView(True)
        self.plot_widget.setXRange(-300,0)
        self.input_control_widget = input_control_widget
        self.input_control_layout = QVBoxLayout()
        self.input_control_widget.setLayout(self.input_control_layout)
        self.log_widget = log_widget

        # initialize the plotting data
        self.data_x = np.zeros(300)
        self.data_y = np.zeros(300)
        self.data_z = np.zeros(300)
        self.curve_x = plot_widget.plot(self.data_x, pen=SENSOR_X_COLOR)
        self.curve_y = plot_widget.plot(self.data_y, pen=SENSOR_Y_COLOR)
        self.curve_z = plot_widget.plot(self.data_z, pen=SENSOR_Z_COLOR)
        self.curve_counter = 0

        # create input control widgets
        self.serial_port_choice_edit = QLineEdit()
        self.serial_port_choice_edit.setPlaceholderText("Choose a Serial Port name")

        self.serial_read_start_button = QPushButton("Start reading")
        self.serial_read_start_button.clicked.connect(self.start_reading)
        self.serial_read_stop_button = QPushButton("Stop reading")
        self.serial_read_stop_button.clicked.connect(self.stop_reading)

        self.serial_port_status_label = QLabel("-")

        self.input_control_layout.addWidget(self.serial_port_choice_edit)
        self.input_control_layout.addWidget(self.serial_read_start_button)
        self.input_control_layout.addWidget(self.serial_read_stop_button)
        self.input_control_layout.addWidget(self.serial_port_status_label)

        self.serial_port = None
        self.serial_port_read_timer = QTimer()
        self.serial_port_read_timer.timeout.connect(self.read_sensor)

        self.logger = logging.getLogger('input_parser')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(QLabelHandler(self.log_widget))

    def set_serial_status(self, obj):
        self.serial_port_status_label.setText(str(obj))

    def log_serial_status(self, obj):
        self.logger.info(str(obj))

    try_reading = False
    reading_init = False

    def try_reading_init(self):
        while self.reading_init and self.try_reading:
            try:
                self.serial_port.write(b"ready")
                self.log_serial_status("Sent ready..")
            except (ValueError, SerialException) as e:
                self.log_serial_status(e)

            try:
                serial_line = self.serial_port.readline().rstrip().decode("utf-8")
                self.log_serial_status(serial_line)

                for prefix in SENSOR_DATA_PREFIXES:
                    if serial_line.startswith(prefix):
                        self.log_serial_status("First data came: " + serial_line)
                        self.log_serial_status("Finished sensor reading initialisation")
                        self.reading_init = False
                        self.set_serial_status("reading")
                        break
            except (ValueError, SerialException) as e:
                self.log_serial_status(e)

            time.sleep(0.2)

        if not self.reading_init and self.try_reading:
            self.read_sensor()

    def start_reading(self):
        if not self.try_reading:
            self.try_reading = True
            self.reading_init = True

            try:
                self.set_serial_status("init")
                self.log_serial_status("Initializing serial port..")
                self.serial_port = serial.Serial(port=self.serial_port_choice_edit.text(),
                                                 baudrate=SERIAL_PORT_BAUD_RATE,
                                                 timeout=1000,
                                                 write_timeout=1000
                                                 )
                self.log_serial_status("Serial port initialized, initializing sensor reading")
                threading.Thread(target=self.try_reading_init).start()
            except (ValueError, SerialException) as e:
                try:
                    self.serial_port.close()
                except (SerialException, AttributeError):
                    self.serial_port = None
                self.set_serial_status("error in init")
                self.stop_reading()
                self.log_serial_status(e)

    def stop_reading(self):
        if self.try_reading:
            try:
                self.serial_port.close()
            except (SerialException, AttributeError):
                self.serial_port = None
            self.try_reading = False
            self.reading_init = False
            self.set_serial_status("stopped")

    def read_sensor(self):
        while self.try_reading:
            try:
                data = self.serial_port.readline().rstrip().decode("utf-8").split()
            except (AttributeError, UnicodeDecodeError, TypeError) as e:
                self.log_serial_status(e)
                continue
            except SerialException as e:
                self.log_serial_status(e)
                break

            try:
                self.data_x[self.curve_counter] = data[1]
                self.data_y[self.curve_counter] = data[2]
                self.data_z[self.curve_counter] = data[3]
                self.notify_targets((data[1], data[2], data[3]))
            except (ValueError, IndexError, TypeError) as e:
                self.log_serial_status(e)
                self.log_serial_status("data: " + str(data))
                self.set_serial_status("error")
            self.curve_counter += 1
            if self.curve_counter >= self.data_x.shape[0]:
                print('icreasing size on', self.curve_counter)
                tmp_x = self.data_x
                self.data_x = np.empty(self.data_x.shape[0]*2)
                self.data_x[:tmp_x.shape[0]] = tmp_x

                tmp_y = self.data_y
                self.data_y = np.empty(self.data_y.shape[0] * 2)
                self.data_y[:tmp_y.shape[0]] = tmp_y

                tmp_z = self.data_z
                self.data_z = np.empty(self.data_z.shape[0] * 2)
                self.data_z[:tmp_z.shape[0]] = tmp_z

            if self.curve_counter > MAX_CURVE_HISTORY:
                self.curve_counter = 0
                self.data_x = np.zeros(300)
                self.data_y = np.zeros(300)
                self.data_z = np.zeros(300)
            self.curve_x.setData(self.data_x[:self.curve_counter])
            self.curve_y.setData(self.data_y[:self.curve_counter])
            self.curve_z.setData(self.data_z[:self.curve_counter])

            self.plot_widget.setXRange(self.curve_counter, self.curve_counter-300)
            self.plot_widget.update()
            QApplication.processEvents()


    targets = {}

    def add_target(self, t_id, target):
        self.targets[t_id] = target

    def remove_target(self, t_id):
        self.targets.pop(t_id)

    def notify_targets(self, data):
        for t in self.targets.values():
            t(data)

