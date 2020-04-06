"""
Bash version of what is happening in this file:
$ socat -d -d pty,raw,echo=0 pty,raw,echo=0
In a loop:
    $ echo "The simulated content" > /dev/ttys002
To see output:
    $ cat < /dev/ttys001
"""
import os
import time
from subprocess import Popen, PIPE
from threading import Thread

import numpy as np

import constants as cn
from utils import logger


class SerialSimulator:
    def __init__(self,
                 tick_change=cn.SIMULATOR_TICK_CHANGE,
                 frequency=cn.SIMULATOR_FREQUENCY):
        """
        Opens the subprocess and reads tty names of the two ends of the pipe
        """
        try:
            self.p = Popen(['socat', '-d', '-d', 'pty,raw,echo=0', 'pty,raw,echo=0'],
                           stdout=PIPE,
                           stderr=PIPE)
        except FileNotFoundError:
            logger.warning('Socat binary was not found in path, simulation depends on it!')
            return

        self.output_socket_for_app = self.p.stderr.readline().decode().strip().split(' ')[-1]
        self.input_socket_for_simulator = self.p.stderr.readline().decode().strip().split(' ')[-1]
        logger.info(f'Simulated Serial created, Listen on `{self.output_socket_for_app}`')

        self.tick_change = tick_change
        self.current_values = np.empty((cn.SENSOR_COUNT, 6), dtype=cn.SENSOR_DATA_DTYPE)
        self.exit_requested = True
        self.sleep_time = 1 / frequency
        self.simulation_thread = None

    def randomize_data(self):
        logger.info('Randomizing data.')
        self.current_values *= 0
        self.current_values += np.random.randint(-2 ** 15, 2 ** 15,
                                                 self.current_values.shape, dtype=cn.SENSOR_DATA_DTYPE)

    def generate_data(self):
        self.current_values += np.random.randint(-self.tick_change / 2,
                                                 self.tick_change / 2,
                                                 self.current_values.shape,
                                                 dtype=cn.SENSOR_DATA_DTYPE)
        return self.current_values.tobytes()

    def set_frequency(self, frequency):
        self.sleep_time = 1 / frequency

    def start(self, threaded=True):
        # TODO exiting the serial simulator is not implemented, because
        #  it requires timeouts on writes/flush to the corresponding side of the serial port
        #  - if no one is reading from the other side, the write just hangs, which seems
        #  to be complicated to handle
        self.exit_requested = False

        def put_data(socket_name):
            try:
                # We open it as a file instead of using serial to enable higher throughput
                with open(socket_name, 'wb+') as serial_port:
                    while not self.exit_requested:
                        serial_port.write(self.generate_data())
                        serial_port.write(cn.SENSOR_READING_DELIMITER)
                        serial_port.flush()
                        time.sleep(self.sleep_time)

                logger.debug(f'Closed socket {socket_name}')
            except Exception as e:
                logger.error(f'Put data received invalid specifier {e}')

        self.simulation_thread = Thread(target=put_data, args=(self.input_socket_for_simulator,))
        self.simulation_thread.start()

        if not threaded:
            self.simulation_thread.join()

    def kill_socket(self):
        self.exit_requested = True
        # TODO socat is still not closed properly in certain cases
        #   run `killall socat` on host machine to fix that
        if hasattr(self, 'p'):
            self.p.kill()
            os.system(f'kill -9 {self.p.pid}')
            logger.info('Killing socat process.')


if __name__ == '__main__':
    sim = SerialSimulator()
    sim.start()

    try:
        while True:
            i = input()
            if i == 'e':
                break
            sim.randomize_data()
    except KeyboardInterrupt:
        print('received KBI')
        sim.kill_socket()
