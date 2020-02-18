from typing import Union

from PyQt5.QtWidgets import QWidget

from graphics.widgets.session.item_base import BaseItem
from input.data_router import DataRouter
from processing.consumers.dynamic_signal_widget import DynamicSignalWidgetConsumer
from utils import application_state


class SignalItem(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_router: DataRouter = application_state.get_main_window().data_router
        self.dynamic_signal_widget_consumer = DynamicSignalWidgetConsumer()

    def get_widget(self) -> Union[QWidget, None]:
        self.data_router.add_consumer(self.dynamic_signal_widget_consumer)
        return self.dynamic_signal_widget_consumer.native

    def finish(self):
        self.data_router.remove_consumer(self.dynamic_signal_widget_consumer)
