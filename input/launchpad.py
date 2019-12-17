import json
from subprocess import Popen, PIPE
from threading import Thread
from typing import Callable

import constants as cn
from utils import logger


class LaunchpadAPI:
    def __init__(self):
        self.process = Popen(['node', f'{cn.BASE_DIR}/launchpad-api/main.js'], stdin=PIPE, stdout=PIPE)

        self.callbacks = []
        self.active = True
        Thread(target=self.stdout_read_loop).start()

    def register_callback(self, callback: Callable[[str], None]) -> None:
        self.callbacks.append(callback)

    class COLORS:
        red = 'red'
        green = 'green'
        yellow = 'yellow'

    def set_color(self, x: int, y: int, color: str):
        self._send_command({'event': 'col', 'x': x, 'y': y, 'color': color})

    def reset(self):
        self._send_command({'event': 'reset'})

    def _send_command(self, command):
        self.process.stdin.write(json.dumps(command).encode())
        self.process.stdin.write('\n'.encode())
        self.process.stdin.flush()

    def stdout_read_loop(self):
        while self.process.poll() is None:
            input_line = self.process.stdout.readline()
            try:
                data = json.loads(input_line.decode().strip() or '{"event": "close"}')
                for callback in self.callbacks:
                    callback(data)
            except json.JSONDecodeError:
                logger.warning(f'Invalid json received: {input_line}')

    def close(self):
        self.process.kill()


if __name__ == '__main__':
    lapi = LaunchpadAPI()
    lapi.register_callback(lambda x: print(x))
    lapi.set_color(3, 3, LaunchpadAPI.COLORS.red)

    def trigger(data):
        if 'event' in data and data['event'] == 'key':
            if (0, 0) == (data['x'], data['y']):
                lapi.close()
            if (1, 1) == (data['x'], data['y']):
                lapi.reset()

            lapi.set_color(data['x'] + 1, data['y'] + 1, 'yellow')


    lapi.register_callback(trigger)
