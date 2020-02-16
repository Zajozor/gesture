from os import path
from threading import Thread
from typing import List

import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout

import constants as cn
from graphics.widgets.recording_controller import RecordingController
from graphics.widgets.signal_static import StaticSignalWidget
from processing.consumers.consumer_mixin import ConsumerMixin
from utils import logger


class RecordingConsumer(RecordingController, ConsumerMixin):
    def __init__(self, frequency: int = 60, max_length: int = 1000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sleep_time: float = 1.0 / frequency
        self.max_length: int = max_length

        self.gesture_data: np.ndarray = np.empty((self.max_length, cn.SENSOR_COUNT, 3))
        self.current_gesture_index = 0

    def start_recording(self):
        super().start_recording()
        self.current_gesture_index = 0

    def stop_recording(self):
        super().stop_recording()
        if self.save:
            self.save_gesture_async()
        if self.show:
            self.add_displayed_signal(
                StaticSignalWidget(self.gesture_data[:self.current_gesture_index]),
                self.readable_gesture_name,
                self.gesture_record_time,
            )

    def save_gesture_async(self):
        if self._recording.is_set():
            logger.warning('Saving in the middle of recording.')
        Thread(target=self.save_gesture, args=(
            self.full_gesture_filename,
            self.readable_gesture_name,
            self.gesture_data[:self.current_gesture_index]
        )).start()

    @staticmethod
    def save_gesture(filename, gesture_name, gesture_data):
        logger.warning(f'Saving gesture {gesture_name} to {filename}.')
        np.save(path.join(cn.DATA_FOLDER, filename), gesture_data)

    def receive_data(self, data: np.ndarray, data_changed: List[bool]):
        if self._recording.is_set():
            self.gesture_data[self.current_gesture_index] = data
            self.current_gesture_index += 1
            if self.current_gesture_index >= self.max_length:
                logger.error('Maximum gesture length exceeded, overflowing..')
                self.current_gesture_index = 0


if __name__ == '__main__':
    q_app = QApplication([])

    win = QWidget()
    layout = QHBoxLayout()
    win.setLayout(layout)

    r = RecordingConsumer()
    layout.addWidget(r)

    win.show()
    q_app.exec()
