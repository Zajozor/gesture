import constants as cn
import serial
import time
from threading import Thread
from utils import logger


class InputParser:
    def __init__(self, serial_port_name='', sensor_count=5, verbose=False):
        self.serial_port_name = serial_port_name if serial_port_name else cn.SERIAL_PORT_NAME
        self.serial_port = None
        self.sensor_count = sensor_count
        self.buffer = [(0.0, 0.0, 0.0) for _ in range(sensor_count)]
        self.has_new_data = [False] * sensor_count
        self.verbose = verbose

        self.active = False
        self.run_thread = None

    def get_data(self, i=None):
        if i is None:
            for j in range(self.sensor_count):
                self.has_new_data[j] = False
            return self.buffer
        self.has_new_data[i] = False
        return self.buffer[i]

    def start(self, threaded):
        if threaded:
            self.run_thread = Thread(target=self.run_serial, daemon=True)
            self.run_thread.start()
        else:
            self.run_serial()

    def run_serial(self):
        while True:  # If the serial drops, try init again and then reading
            self.init_serial()
            self.read_serial()
            time.sleep(0.1)

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
                sensor_id_offset = 2 # TODO extract constant (this is the multiplexer offset)
                sensor_id = int(data[0]) - sensor_id_offset
                if 0 <= sensor_id < self.sensor_count:
                    self.buffer[sensor_id] = (float(data[2]), float(data[3]), float(data[4]))
                    self.has_new_data[sensor_id] = True
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
        ip = InputParser('/dev/cu.SLAB_USBtoUART')
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
