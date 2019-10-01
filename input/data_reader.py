from threading import Thread
import numpy as np
from vispy import app

from constants import DATA_NORMALIZATION_COEFFICIENT
from graphics.signal_canvas import SignalCanvas
from input.input_parser import InputParser
import time

from utils import logger


class DataReader:
    def __init__(self, input_parser_instance, length=200, sensor_count=5,
                 signal_canvas_instance: SignalCanvas = None, log_counts=False, frequency=60):
        self.input_parser_instance = input_parser_instance
        self.signal_canvas_instance = signal_canvas_instance

        self.log_counts = log_counts
        self.length = length
        self.sensor_count = sensor_count
        self.sleep_time = 1.0 / frequency

        self.last_update = time.time()
        self.update_counts = [0] * sensor_count

        self.current_data = np.zeros((length, sensor_count, 3)).astype(np.float32)
        self.running = False
        self.run_thread = None

        self.signal_ids = []
        if self.signal_canvas_instance:
            for i in range(self.sensor_count):
                self.signal_ids.append(
                    self.signal_canvas_instance.add_signal_multi(
                        i % self.signal_canvas_instance.rows, i // self.signal_canvas_instance.rows, count=3))
                self.signal_canvas_instance.set_signal_data_multi(self.signal_ids[i], colors=np.stack([
                    np.tile((1., 0.3, 0.), (self.length, 1)),
                    np.tile((0.3, 1., 0.4), (self.length, 1)),
                    np.tile((0.2, 0.1, 1.), (self.length, 1))
                ]))

    def start(self, threaded):
        self.running = True
        if threaded:
            self.run_thread = Thread(target=self.update, daemon=True)
            self.run_thread.start()
        else:
            self.update()

    def update(self):
        while self.running:
            has_new_data = self.input_parser_instance.has_new_data[:]
            data = np.array(self.input_parser_instance.get_data()) / DATA_NORMALIZATION_COEFFICIENT
            if data is not None:
                self.current_data = np.roll(self.current_data, -1, 0)
                self.current_data[-1] = data

            if self.signal_canvas_instance:
                for sensor_id in range(self.sensor_count):
                    if has_new_data[sensor_id]:
                        self.update_counts[sensor_id] += 1
                        self.signal_canvas_instance.roll_signal_data_multi(self.signal_ids[sensor_id],
                                                                           positions=data[sensor_id].reshape(3, 1))

            if self.log_counts:
                current_time = time.time()
                if current_time - self.last_update > 1:
                    self.last_update = current_time
                    logger.info(f'Update counts: {self.update_counts}, total: {sum(self.update_counts)}')
                    self.update_counts = [0] * self.sensor_count

            time.sleep(self.sleep_time)


if __name__ == '__main__':
    canvas = SignalCanvas(2, 3, length=200)
    ip = InputParser('/dev/cu.SLAB_USBtoUART')
    # ip = InputParser('/dev/ttys000')
    ip.start(threaded=True)

    dr = DataReader(ip, signal_canvas_instance=canvas, log_counts=True)
    dr.start(threaded=True)

    app.run()
