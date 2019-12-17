import time
from threading import Thread
from typing import List, Union

import numpy as np

import constants as cn
from input.serial_port_parser import SerialPortParser
from processing.consumers.consumer_mixin import ConsumerMixin
from utils import logger


class DataRouter:
    """
    DataRouter is an intermediary between a serial port parser and some data consumers.
    It is initialized with a SerialPortParser instance and then consumers are added to it.
    Each of these consumers then receives data through the consumer interface.
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
                    if current_time - self.last_update > cn.SENSOR_UPDATE_LOG_FREQUENCY:
                        self.last_update = current_time
                        logger.info(f'Update counts after {cn.SENSOR_UPDATE_LOG_FREQUENCY}s: '
                                    f'{self.update_counts}, Σ: {sum(self.update_counts)}')
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
