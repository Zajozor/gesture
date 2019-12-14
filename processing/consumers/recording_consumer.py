import time
from os import path
from threading import Event
from threading import Thread
from typing import List

import numpy as np

import constants as cn
from graphics.widgets.recording_controller import RecordingController
from graphics.widgets.signal_grid_canvas import create_simple_canvas
from processing.consumers.consumer_mixin import ConsumerMixin
from utils import logger


class RecordingConsumer(ConsumerMixin):
    def __init__(self, frequency: int = 60, max_length: int = 1000):
        self.sleep_time: float = 1.0 / frequency
        self.max_length: int = max_length

        self._record = Event()
        self.should_stop = False

        self._gesture_name = 'test'
        self.gesture_data: np.ndarray = np.empty((self.max_length, cn.SENSOR_COUNT, 3))
        self.current_index = 0

        self.controller = RecordingController(lambda: self.start_recording(), lambda: self.stop_recording())
        self.shown_canvases = []

    def start_recording(self):
        if self._record.is_set():
            logger.waring('Warning, start record was already set.')
        self.controller.start_button.setEnabled(False)
        self.controller.stop_button.setEnabled(True)

        self.current_index = 0
        self._record.set()

    def stop_recording(self):
        if not self._record.is_set():
            logger.warning('Warning, stop record was already set')
        self.controller.start_button.setEnabled(True)
        self.controller.stop_button.setEnabled(False)
        self._record.clear()

        should_show = self.controller.show
        should_save = self.controller.save
        gesture_name = self.controller.gesture_name()

        if should_show:
            self.shown_canvases.append(
                create_simple_canvas(self.gesture_data[:self.current_index],
                                     self.current_index,
                                     gesture_name))

        if should_save:
            t = Thread(target=self.save_gesture, args=(gesture_name, self.gesture_data[:self.current_index]))
            t.start()

    @staticmethod
    def save_gesture(gesture_name, gesture_data):
        filename = f'g-{gesture_name}-{time.strftime("%Y%m%d-%H%M%S")}'
        logger.warning(f'Saving gesture {gesture_name} to {filename}.')
        np.save(path.join(cn.DATA_FOLDER, filename), gesture_data)

    def set_gesture_name(self, gesture_name):
        self._gesture_name = gesture_name

    def receive_data(self, data: np.ndarray, data_changed: List[bool]):
        if self._record.is_set():
            self.gesture_data[self.current_index] = data
            self.current_index += 1
