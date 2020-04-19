from threading import Event

import numpy as np

import constants as cn
from processing.consumers.consumer_mixin import ConsumerMixin
from utils import logger


class RecordingConsumer(ConsumerMixin):
    def __init__(self,
                 frequency: int = cn.RECORDING_POLL_FREQUENCY,
                 max_length: int = cn.RECORDING_MAX_LENGTH,
                 sensor_count: int = cn.SENSOR_COUNT):
        super().__init__()
        self.sleep_time: float = 1.0 / frequency
        self.max_length: int = max_length
        self.sensor_count: int = sensor_count

        self.recording_active: Event = Event()
        self.raw_gesture_data: np.ndarray = np.empty((self.max_length, sensor_count, cn.SENSOR_CHANNEL_COUNT))
        self.current_gesture_index: int = 0

    @property
    def gesture_data(self):
        # Here we return a copy of the data, so that it remains constant (if we return only a view, it can change)
        return np.copy(self.raw_gesture_data[:self.current_gesture_index])

    def start_recording(self):
        self.current_gesture_index = 0
        self.recording_active.set()

    def stop_recording(self):
        self.recording_active.clear()

    def receive_data(self, data: np.ndarray, _):
        if self.recording_active.is_set():
            self.raw_gesture_data[self.current_gesture_index] = data
            self.current_gesture_index += 1
            if self.current_gesture_index >= self.max_length:
                logger.error('Maximum gesture length exceeded, overflowing..')
                self.current_gesture_index = 0
