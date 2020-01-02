"""
Bash version of what is happening in this file:
$ socat -d -d pty,raw,echo=0 pty,raw,echo=0
$ echo "Test" > /dev/ttys002
$ cat < /dev/ttys001
"""
import math
import time
from random import random, randint
from subprocess import Popen, PIPE
from threading import Thread

import constants as cn
from utils import logger


class SerialSimulator:
    def __init__(self,
                 values_range=cn.SIMULATOR_VALUES_RANGE,
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
            logger.warning('Socat binary was not found, simulation will not work!')
            return

        self.left = self.p.stderr.readline().decode().strip().split(' ')[-1]
        self.right = self.p.stderr.readline().decode().strip().split(' ')[-1]
        logger.info(f'Simulated Serial created, Listen on `{self.left}`')

        self.values_range = values_range
        self.tick_change = tick_change

        self.current_values = {'x': 0, 'y': 0, 'z': 0}
        self.exit_requested = True

        self.randomize_data()
        self.sleep_time = 1 / frequency

        def put_data(right):
            try:
                with open(right, 'wb+') as term:
                    while not self.exit_requested:
                        for sensor_id in range(cn.SENSOR_ID_OFFSET,
                                               cn.SENSOR_ID_OFFSET + cn.SENSOR_COUNT):
                            data = self.generate_data(sensor_id)
                            term.write(data.encode())
                            term.write('\n'.encode())
                            term.flush()
                        time.sleep(self.sleep_time)
            except Exception as e:
                logger.error('Put data received invalid specifier', str(e))

        self.data_process = Thread(target=put_data, args=(self.right,))

    def randomize_data(self):
        logger.info('Randomizing data.')
        for k in self.current_values:
            self.current_values[k] = random() * self.values_range - self.values_range // 2

    def generate_data(self, sensor_id=None):
        if sensor_id is None:
            sensor_id = cn.SENSOR_ID_OFFSET + randint(0, cn.SENSOR_COUNT - 1)
        for k in self.current_values:
            self.current_values[k] += math.copysign(
                random() * self.tick_change,
                random() * self.values_range * 8 - self.values_range * 4 - self.current_values[k])
        return f'{sensor_id}\t' \
               f'aworld\t' \
               f'{self.current_values["x"]:.5f}\t' \
               f'{self.current_values["y"]:.5f}\t' \
               f'{self.current_values["z"]:.5f}'

    def set_frequency(self, frequency):
        self.sleep_time = 1 / frequency

    def start(self, threaded=True):
        self.exit_requested = False
        self.data_process.start()

        if not threaded:
            self.data_process.join()

    def kill_socket(self):
        self.exit_requested = True
        # TODO socat is still not closed properly in certain cases
        # run `killall socat` on host machine to fix that
        if hasattr(self, 'p'):
            self.p.kill()
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
