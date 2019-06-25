import time
from constants import *
import serial
from serial import SerialException
from threading import Thread


class InputParser:
    def __init__(self, serial_port_name=''):
        self.serial_port_name = serial_port_name if serial_port_name else SERIAL_PORT_NAME
        self.serial_port = None
        self.buffer = (0, 0, 0)

        self.reading = False
        self.status = 'pre-init'
        self.run_thread = None

    def get_data(self):
        return self.buffer

    def start(self, threaded):
        if threaded:
            self.run_thread = Thread(target=self.init_serial, daemon=True)
            self.run_thread.start()
        else:
            self.init_serial()

    def init_serial(self):
        # Open the serial port
        if not self.reading:
            self.reading = True

            try:
                self.status = 'init'
                self.serial_port = serial.Serial(port=self.serial_port_name,
                                                 baudrate=SERIAL_PORT_BAUD_RATE,
                                                 timeout=1000,
                                                 write_timeout=1000)
            except (ValueError, SerialException):
                try:
                    self.serial_port.close()
                except (SerialException, AttributeError):
                    self.serial_port = None
                self.status = 'error in init'
                self.reading = False

        # Read the first handshake values
        reading_init = True
        while self.reading and reading_init:
            try:
                self.serial_port.write(b"ready")
                self.status = 'sent ready'
            except (ValueError, SerialException):
                self.status = 'write error'

            try:
                serial_line = self.serial_port.readline().rstrip().decode("utf-8")

                for prefix in SENSOR_DATA_PREFIXES:
                    if serial_line.startswith(prefix):
                        reading_init = False
                        self.status = 'reading'
                        break
            except (ValueError, SerialException):
                self.status = 'read error'

            # Give the sensor a time to initialize
            time.sleep(0.1)

        # Start reading
        if not reading_init and self.reading:
            self.read_serial()

    def read_serial(self):
        while self.reading:
            try:
                data = self.serial_port.readline().rstrip().decode("utf-8").split()  # Semi-Blocking io from serial
            except (AttributeError, UnicodeDecodeError, TypeError):
                self.status = 'format read error'
                continue
            except SerialException:
                self.status = 'serial read error'
                break

            try:
                self.buffer = list(map(float, data[1:4]))
            except (ValueError, IndexError, TypeError):
                self.status = 'format read error'
            if data[0] == 'switching':
                print(data)

    def stop_serial(self):
        if self.reading:
            try:
                self.serial_port.close()
            except (SerialException, AttributeError):
                self.serial_port = None
            self.reading = False
            self.status = 'stopped'
