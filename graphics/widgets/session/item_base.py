from abc import ABC
from typing import Union, Callable

from PyQt5.QtWidgets import QWidget

from graphics.widgets.session.storage import SessionStorage


class BaseItem(ABC):
    def __init__(self, item_spec: dict, storage: SessionStorage, advance_slide_callback: Callable[[bool], None]):
        self.item_spec = item_spec
        self.storage = storage
        self.advance_slide_callback = advance_slide_callback

    def get_widget(self) -> Union[QWidget, None]:
        raise NotImplementedError('Each item should implement its own get_widget method')

    def finish(self):
        raise NotImplementedError('Each item should implement its own finish method')
