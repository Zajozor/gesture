from threading import Thread
from typing import List, Union

import numpy as np
from PyQt5.QtWidgets import QApplication
from vispy import app

from input.serial_port_parser import SerialPortParser
import time
import constants as cn
from processing.consumers.consumer_mixin import ConsumerMixin
from processing.consumers.recording_consumer import RecordingConsumer
from processing.consumers.signal_grid_consumer import SignalGridCanvasConsumer, CellContentTriple

from utils import logger


class DataRouter:
    """
    DataRouter is an intermediary between a serial port parser and some data consumers.
    """
    def __init__(self,
                 serial_port_parser_instance: SerialPortParser,
                 enable_count_logs: bool = False,
                 frequency: int = 60):
        self.serial_port_parser_instance: SerialPortParser = serial_port_parser_instance

        self.enable_count_logs: bool = enable_count_logs
        self.sleep_time: float = 1.0 / frequency
        self.last_update: float = time.time()
        self.update_counts: List[int] = [0] * cn.SENSOR_COUNT

        self.active: bool = False
        self.thread: Union[Thread, None] = None

        self._consumers: List[ConsumerMixin] = []

    def add_consumer(self, consumer: ConsumerMixin):
        self._consumers.append(consumer)

    def start(self, threaded: bool):
        def update():
            while self.active:
                data_changed: List[bool] = self.serial_port_parser_instance.data_changed
                data: np.ndarray = self.serial_port_parser_instance.data

                if self.enable_count_logs:
                    for sensor_id in range(cn.SENSOR_COUNT):
                        if data_changed[sensor_id]:
                            self.update_counts[sensor_id] += 1

                    current_time = time.time()
                    if current_time - self.last_update > 1:
                        self.last_update = current_time
                        logger.info(f'Update counts: {self.update_counts}, total: {sum(self.update_counts)}')
                        self.update_counts = [0] * cn.SENSOR_COUNT

                self.route_data(data, data_changed)

                time.sleep(self.sleep_time)

        self.active = True
        if threaded:
            self.thread = Thread(target=update, daemon=True)
            self.thread.start()
        else:
            update()

    def route_data(self, data: np.ndarray, data_changed: List[bool]):
        for consumer in self._consumers:
            consumer.receive_data(data, data_changed)


if __name__ == '__main__':
    QApplication([])
    canvas_consumer = SignalGridCanvasConsumer(cell_contents=(
        CellContentTriple(0, 0, 0), CellContentTriple(0, 1, 1), CellContentTriple(0, 2, 2),
        CellContentTriple(0, 3, 3), CellContentTriple(0, 4, 4),
    ), rows=1, cols=5, length=100, show=True)

    recording_consumer = RecordingConsumer()

    spp = SerialPortParser('/dev/ttys006')
    spp.start(threaded=True)

    dr = DataRouter(serial_port_parser_instance=spp, enable_count_logs=True)
    dr.start(threaded=True)
    dr.add_consumer(canvas_consumer)
    dr.add_consumer(recording_consumer)
    app.run()
