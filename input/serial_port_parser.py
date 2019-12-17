import time
from threading import Thread
from typing import Union, List, Tuple

import numpy as np
import serial

import constants as cn
from utils import logger


class SerialPortParser:
    """
    The responsibility of the SerialPortParser is to open up a serial port and read data from it.
    This data can contain errors, the sensor can drop out, etc. so all the errors and retrying
    should be handled here.
    The data is read as fast as possible, relying on the fact, that the throughput of the
    serial port will not be too high for this to be a problem.

    Input: Serial port
    Output: Data in a buffer
    """

    def __init__(self, serial_port_name, verbose: bool = False):
        self.serial_port_name: str = serial_port_name
        self.serial_port: Union[serial.Serial, None] = None

        self.buffer: List[Tuple[float, float, float]] = [(0.0, 0.0, 0.0) for _ in range(cn.SENSOR_COUNT)]
        self._data_changed: List[bool] = [False] * cn.SENSOR_COUNT

        self.verbose: bool = verbose
        self.active: bool = False
        self.thread: Union[Thread, None] = None

    def start(self, threaded):
        def run_serial_parsing():
            while True:  # If the serial drops, try init again and then reading
                self.init_serial()
                self.read_serial()
                time.sleep(0.1)

        if threaded:
            self.thread = Thread(target=run_serial_parsing, daemon=True)
            self.thread.start()
        else:
            run_serial_parsing()

    def init_serial(self):
        while not self.active:
            try:
                self.serial_port = serial.Serial(port=self.serial_port_name,
                                                 baudrate=cn.SERIAL_PORT_BAUD_RATE,
                                                 timeout=1000,
                                                 write_timeout=1000)
                self.serial_port.write(b"starting")
                self.serial_port.readline().rstrip().decode("utf-8")
                logger.info('Serial port successfully opened.')
                self.active = True
            except (ValueError, serial.SerialException):
                logger.warning('Error during serial port init.')
                self.stop_serial()
                time.sleep(0.5)

    def read_serial(self):
        while self.active:
            try:
                data = self.serial_port.readline().rstrip().decode().split()
                if self.verbose:
                    logger.debug(f'Serial received data: {data}')
            except (AttributeError, UnicodeDecodeError, TypeError, serial.SerialException) as e:
                logger.warning(f'Serial reading error: {e}')
                self.stop_serial()
                break
            try:
                sensor_id = int(data[0]) - cn.SENSOR_ID_OFFSET
                if 0 <= sensor_id < cn.SENSOR_COUNT:
                    self.buffer[sensor_id] = (float(data[2]), float(data[3]), float(data[4]))
                    self._data_changed[sensor_id] = True
            except (ValueError, IndexError, TypeError):
                # On format errors, we do not restart the serial
                logger.warning(f'Invalid data received: {data}')

    def stop_serial(self):
        if self.active:
            try:
                self.serial_port.close()
            except (serial.SerialException, AttributeError):
                self.serial_port = None
            self.active = False

    # TODO change serial...

    @property
    def data(self):
        self._data_changed = [False] * cn.SENSOR_COUNT
        return np.array(self.buffer) / cn.DATA_NORMALIZATION_COEFFICIENT

    @property
    def data_changed(self):
        return self._data_changed[:]


if __name__ == '__main__':
    """Example usage below"""


    def raw_serial():
        serial_port = serial.Serial(port='/dev/cu.SLAB_USBtoUART',
                                    baudrate=9600,
                                    timeout=1000,
                                    write_timeout=1000)
        logger.warning('Running in echo mode for the serial port')
        while True:
            serial_line = serial_port.readline().rstrip().decode("utf-8")
            logger.info(serial_line)


    def try_input_parser():
        ip = SerialPortParser('/dev/cu.SLAB_USBtoUART')
        ip.start(threaded=True)
        prev_buffer = ip.buffer
        while True:
            changed = 0
            for i in range(len(ip.buffer)):
                if prev_buffer[i] != ip.buffer[i]:
                    changed += 1
            logger.info(f'Changed count: {changed}, Buffer is: {ip.buffer}')
            prev_buffer = ip.buffer[:]
            time.sleep(0.1)


    # raw_serial()
    try_input_parser()
