# Bash version:
# socat -d -d pty,raw,echo=0 pty,raw,echo=0
# echo "Test" > /dev/ttys002
# cat < /dev/ttys001
import math
import os
import threading
import time
from random import randint
from subprocess import Popen, PIPE

import constants as cn
from utils import logger

VALUES_RANGE = 20
TICK_CHANGE = 1


def randomize_data():
    logger.info('randomizing data..')
    for k in current:
        current[k] = randint(-VALUES_RANGE // 2, VALUES_RANGE // 2)


def generate_data():
    sensor_id = cn.SENSOR_ID_OFFSET + randint(0, cn.SENSOR_COUNT - 1)
    for k in current:
        current[k] += math.copysign(randint(0, TICK_CHANGE),
                                    randint(-VALUES_RANGE * 4, VALUES_RANGE * 4) - current[k])
    return f'{sensor_id}\taworld\t{current["x"]}\t{current["y"]}\t{current["z"]}'


def start_ttys():
    p = Popen(['socat', '-d', '-d', 'pty,raw,echo=0', 'pty,raw,echo=0'], stderr=PIPE)
    _left = p.stderr.readline().decode().split(' ')[-1]
    _right = p.stderr.readline().decode().split(' ')[-1]
    return _left, _right


def put_data(tty, delay=0.1):
    while True:
        if please_exit:
            return
        data = generate_data()
        os.system(f'echo "{data}" > {tty}')
        time.sleep(delay)


current = {'x': 0, 'y': 0, 'z': 0}
randomize_data()
please_exit = False

if __name__ == '__main__':
    left, right = start_ttys()
    logger.info(f'Listen on {left}')
    data_thread = threading.Thread(target=put_data, args=(right, 0.01))
    data_thread.start()

    while True:
        i = input()
        if i == 'e':
            break
        randomize_data()
    please_exit = True
