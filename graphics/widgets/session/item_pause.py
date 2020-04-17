import time
from typing import Union

import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QProgressBar

import constants as cn
from graphics.styles import Q_PROGRESS_BAR_STYLE
from graphics.widgets.session.item_base import BaseItem
from input.data_router import DataRouter
from processing.consumers.recording import RecordingConsumer
from utils import application_state

PROGRESS_TIMEOUT = 50


class PauseItem(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.advance_slide_callback())
        self.timer.setInterval(self.item_spec['timeout-ms'])
        self.timer.setSingleShot(True)

        self.show_widget = self.item_spec.get('show', True)
        self.progress_timer = QTimer()
        self.progress_timer.setInterval(PROGRESS_TIMEOUT)

        self.record_null_class = self.item_spec.get('record', True)
        self.record_class_name = self.item_spec.get('class', cn.GESTURES[cn.NULL_CLASS_INDEX].slug)

        self.data_router: DataRouter = application_state.get_main_window().data_router
        self.recording_consumer = RecordingConsumer()

    def get_widget(self) -> Union[QWidget, None]:
        self.timer.start()

        if not self.show_widget:
            return None

        progress_bar = QProgressBar()
        progress_bar.setMaximum(self.item_spec['timeout-ms'])
        progress_bar.setTextVisible(False)
        progress_bar.setStyleSheet(Q_PROGRESS_BAR_STYLE)
        start_time = time.time()

        def update_progress_bar():
            progress_bar.setValue((time.time() - start_time) * 1000)

        self.progress_timer.timeout.connect(update_progress_bar)
        self.progress_timer.start()

        if self.record_null_class:
            self.data_router.add_consumer(self.recording_consumer)
            self.recording_consumer.start_recording()

        return progress_bar

    def finish(self):
        self.timer.stop()
        self.progress_timer.stop()

        if self.record_null_class:
            self.data_router.remove_consumer(self.recording_consumer)
            # We wrap the recording this way, to be compatible with normal recording
            instances = np.empty(1, dtype=object)
            instances[0] = self.recording_consumer.gesture_data
            self.storage.store_signal_data(self.record_class_name, instances)
