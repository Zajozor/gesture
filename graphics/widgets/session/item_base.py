from abc import ABC
from typing import Union

from PyQt5.QtWidgets import QWidget

from graphics.widgets.session.storage import SessionStorage


class BaseItem(ABC):
    def __init__(self, item_spec: dict, storage: SessionStorage):
        self.item_spec = item_spec
        self.storage = storage

    def get_widget(self) -> Union[QWidget, None]:
        raise NotImplementedError('Each item should implement its own get_widget method')

    def finish(self):
        raise NotImplementedError('Each item should implement its own finish method')
