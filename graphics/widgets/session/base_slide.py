from typing import Callable

from PyQt5.QtWidgets import QWidget

from graphics.widgets.session.storage import SessionStorage


class BaseSlide(QWidget):
    def __init__(self, spec: dict, next_callback: Callable[[], None], storage: SessionStorage, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spec = spec
        self.next_callback = next_callback
        self.storage = storage
