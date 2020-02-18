from typing import Union

from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from graphics.event_filter import GlobalEventFilter
from graphics.widgets.session.item_base import BaseItem
from graphics.widgets.signal_static import StaticSignalWidget
from input.data_router import DataRouter
from processing.consumers.recording import RecordingConsumer
from utils import application_state


class RecordItem(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_router: DataRouter = application_state.get_main_window().data_router
        self.recording_consumer = RecordingConsumer()
        self.data_router.add_consumer(self.recording_consumer)
        self.layout = QVBoxLayout()

    def space_callback(self, _: QObject, event: QKeyEvent) -> bool:
        event_type = event.type()
        if event_type == QKeyEvent.KeyPress and not event.isAutoRepeat():
            self.recording_consumer.start_recording()
            return True
        if event_type == QKeyEvent.KeyRelease:
            self.recording_consumer.stop_recording()
            self.layout.addWidget(StaticSignalWidget(self.recording_consumer.gesture_data))
            return True
        return False

    def get_widget(self) -> Union[QWidget, None]:
        widget = QWidget()
        widget.setLayout(self.layout)
        GlobalEventFilter.get_instance().install_key_hook(Qt.Key_Space, self.space_callback)
        return widget

    def finish(self):
        self.data_router.remove_consumer(self.recording_consumer)
        GlobalEventFilter.get_instance().remove_key_hook(Qt.Key_Space, self.space_callback)
