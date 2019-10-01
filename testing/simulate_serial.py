# Bash version:
# socat -d -d pty,raw,echo=0 pty,raw,echo=0
# echo "Test" > /dev/ttys002
# cat < /dev/ttys001
import math
import os
import time
import threading
from random import randint
from sarge import Capture, run
from utils import logger

VALUES_RANGE = 2000
TICK_CHANGE = 100
SENSOR_COUNT = 5


def randomize_data():
    logger.info('randomizing data..')
    for k in current:
        current[k] = randint(-VALUES_RANGE // 2, VALUES_RANGE // 2)


def generate_data():
    sensor_id = randint(0, SENSOR_COUNT - 1)
    for k in current:
        current[k] += math.copysign(randint(0, TICK_CHANGE),
                                    randint(-VALUES_RANGE * 4, VALUES_RANGE * 4) - current[k])
    return f'{sensor_id}\taworld\t{current["x"]}\t{current["y"]}\t{current["z"]}'


def start_ttys():
    p = run('socat -d -d pty,raw,echo=0 pty,raw,echo=0', stderr=Capture(), async_=True)
    time.sleep(0.05)  # Wait for output to be available
    lines = p.stderr.text.split('\n')
    assert(len(lines) == 4)
    _left = lines[0].split(' ')[-1]
    _right = lines[1].split(' ')[-1]
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
