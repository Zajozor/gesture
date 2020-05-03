import time
from threading import Thread
from typing import Union

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

        self.buffer: np.ndarray = np.zeros((cn.SENSOR_COUNT, 6), dtype=cn.SENSOR_DATA_DTYPE)
        self._data_changed: bool = False

        self.verbose: bool = verbose
        self.current_active_state: bool = False
        self.target_active_state: bool = False
        self.thread: Union[Thread, None] = None

    def start(self, threaded):
        self.target_active_state = True

        def run_serial_parsing():
            while self.target_active_state:  # If the serial drops, try init again and then reading
                self.init_serial()
                self.read_serial()
                time.sleep(0.1)

        if threaded:
            self.thread = Thread(target=run_serial_parsing, daemon=True)
            self.thread.start()
        else:
            run_serial_parsing()

    def init_serial(self):
        while not self.current_active_state and self.target_active_state:
            try:
                baud_rate = cn.SIMULATED_SERIAL_PORT_BAUD_RATE \
                    if self.serial_port_name.startswith(cn.SIMULATED_SERIAL_PORT_PREFIX) \
                    else cn.SERIAL_PORT_BAUD_RATE
                self.serial_port = serial.Serial(port=self.serial_port_name,
                                                 baudrate=baud_rate,
                                                 timeout=1000,
                                                 write_timeout=1000)
                self.serial_port.read_until(cn.SENSOR_READING_DELIMITER, 2 * cn.SENSOR_CORRECT_READING_LENGTH)
                logger.info('Serial port successfully opened.')
                self.current_active_state = True
            except (ValueError, serial.SerialException):
                logger.warning('Error during serial port init.')
                self.cleanup_serial()
                time.sleep(0.5)

    def read_serial(self):
        while self.current_active_state and self.target_active_state:
            try:
                data = self.serial_port.read_until(cn.SENSOR_READING_DELIMITER, 2 * cn.SENSOR_CORRECT_READING_LENGTH)
                data = data[:-len(cn.SENSOR_READING_DELIMITER)]
                if self.verbose:
                    logger.debug(f'Serial port raw received data: `{",".join([str(x) for x in data])}`')
            except (AttributeError, UnicodeDecodeError, TypeError, serial.SerialException) as e:
                logger.warning(f'Serial reading error: {e}')
                self.cleanup_serial()
                break
            try:
                if len(data) != cn.SENSOR_CORRECT_READING_LENGTH:
                    raise ValueError(f'Expecting input of length {cn.SENSOR_CORRECT_READING_LENGTH}.')
                self.buffer = np.frombuffer(data, dtype=cn.SENSOR_DATA_DTYPE).reshape(self.buffer.shape)
                self._data_changed = True
            except (ValueError, IndexError, TypeError):
                # On format errors, we do not restart the serial
                logger.warning(f'Invalid data received: `{",".join([str(x) for x in data])}`')

    def cleanup_serial(self):
        if self.current_active_state:
            try:
                self.serial_port.close()
            except (serial.SerialException, OSError, AttributeError):
                self.serial_port = None
            self.current_active_state = False

    def stop_serial(self):
        self.target_active_state = False
        self.cleanup_serial()

    def set_serial_port_name(self, new_name):
        if not self.current_active_state:
            self.serial_port_name = new_name
        else:
            raise RuntimeError('Cannot rename a running serial port!')

    @property
    def data(self):
        self._data_changed = False
        return self.buffer / cn.DATA_NORMALIZATION_COEFFICIENT

    @property
    def data_changed(self):
        return self._data_changed


if __name__ == '__main__':
    """Example usage below"""


    def raw_serial():
        serial_port = serial.Serial(port='/dev/cu.SLAB_USBtoUART',
                                    baudrate=cn.SERIAL_PORT_BAUD_RATE,
                                    timeout=1000,
                                    write_timeout=1000)
        logger.warning('Running in echo mode for the serial port')
        last_time = time.time()
        counter = 0
        while True:
            serial_line = serial_port.read_until(cn.SENSOR_READING_DELIMITER, 2 * cn.SENSOR_CORRECT_READING_LENGTH)
            logger.debug(f'Received {len(serial_line) - len(cn.SENSOR_READING_DELIMITER)} bytes')
            counter += 1
            if time.time() - last_time > 1:
                last_time = time.time()
                logger.info(f'Frequency {counter}')
                counter = 0


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
