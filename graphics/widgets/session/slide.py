from typing import Callable, List

from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from graphics.event_filter import GlobalEventFilter
from graphics.widgets.session.common import get_item_from_spec
from graphics.widgets.session.item_base import BaseItem
from graphics.widgets.session.storage import SessionStorage


class Slide(QWidget):
    def __init__(self, slide_spec: dict, next_callback: Callable[[bool], None], storage: SessionStorage,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(main_layout)

        self.items: List[BaseItem] = [
            get_item_from_spec(item_spec, storage, self.advance_slide)
            for item_spec in slide_spec['items']
        ]
        self.next_callback = next_callback

        for item in self.items:
            item_widget = item.get_widget()
            if item_widget:
                main_layout.addWidget(item_widget)

        self.advance_hooks = []

        def create_advance(should_quit, key: Qt.Key):
            def advance(_: QObject, event: QKeyEvent) -> bool:
                if event.type() == QKeyEvent.KeyPress and not event.isAutoRepeat():
                    if should_quit or not slide_spec.get('disable-advance', False):
                        self.advance_slide(should_quit)
                        return True
                return False

            return key, advance

        self.advance_hooks = [create_advance(False, Qt.Key_Return),
                              create_advance(True, Qt.Key_Escape)]
        for fn_key, fn in self.advance_hooks:
            GlobalEventFilter.get_instance().install_key_hook(fn_key, fn)

    def advance_slide(self, should_quit: bool = False):
        for fn_key, fn in self.advance_hooks:
            GlobalEventFilter.get_instance().remove_key_hook(fn_key, fn)

        for finishing_item in self.items:
            finishing_item.finish()
        self.next_callback(should_quit)
