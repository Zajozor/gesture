from typing import Union, List

import numpy as np
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

        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignTop)

        self.name = self.item_spec['name']
        self.signal_count = self.item_spec['count']
        self.signal_widgets: List[StaticSignalWidget] = [
            StaticSignalWidget() for _ in range(self.signal_count)
        ]
        for i, signal_widget in enumerate(self.signal_widgets):
            signal_widget.setMinimumWidth(600)
            signal_widget.setFixedHeight(160)

            def create_select_callback(index):
                return lambda _: self.select_signal_widget(index)

            signal_widget.mouse_press_callback = create_select_callback(i)
            self.layout.addWidget(signal_widget)
        self.selected_index = 0
        self.select_signal_widget(0)

    def space_callback(self, _: QObject, event: QKeyEvent) -> bool:
        event_type = event.type()
        if event_type == QKeyEvent.KeyPress and not event.isAutoRepeat():
            self.recording_consumer.start_recording()
            return True
        if event_type == QKeyEvent.KeyRelease:
            self.recording_consumer.stop_recording()
            self.update_signal_widgets()
            return True
        return False

    def update_signal_widgets(self):
        selected_widget = self.signal_widgets[self.selected_index]
        selected_widget.plot_data(self.recording_consumer.gesture_data)
        self.select_signal_widget((self.selected_index + 1) % len(self.signal_widgets))

    def select_signal_widget(self, index):
        self.signal_widgets[self.selected_index].setStyleSheet('')
        self.selected_index = index
        if self.signal_widgets[index].graphics_layout.childItems():
            style = 'border-radius: 5px; border: 5px solid "#7AB567";'
        else:
            style = 'border-radius: 5px; border: 5px solid "#AA5C65";'
        self.signal_widgets[index].setStyleSheet(style)

    def get_widget(self) -> Union[QWidget, None]:
        widget = QWidget()
        widget.setLayout(self.layout)
        widget.setMinimumSize(600, 615)
        widget.setMaximumSize(1000, 820)

        self.data_router.add_consumer(self.recording_consumer)
        GlobalEventFilter.get_instance().install_key_hook(Qt.Key_Space, self.space_callback)
        return widget

    def finish(self):
        new_data = np.array([signal.data for signal in self.signal_widgets])
        self.storage.store_signal_data(self.name, new_data)
        self.data_router.remove_consumer(self.recording_consumer)
        GlobalEventFilter.get_instance().remove_key_hook(Qt.Key_Space, self.space_callback)
