from typing import Callable, Dict, List, Type

from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from graphics.event_filter import GlobalEventFilter
from graphics.widgets.session.item_base import BaseItem
from graphics.widgets.session.item_image import ImageItem
from graphics.widgets.session.item_input import InputItem
from graphics.widgets.session.item_text import TextItem
from graphics.widgets.session.storage import SessionStorage
from utils import logger

ITEM_CLASSES: Dict[str, Type[BaseItem]] = {
    'text': TextItem,
    'image': ImageItem,
    'input': InputItem,
}


class Slide(QWidget):
    def __init__(self, slide_spec: dict, next_callback: Callable[[], None], storage: SessionStorage, *args, **kwargs):
        super().__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(main_layout)
        items: List[BaseItem] = []

        for item in slide_spec['items']:
            if item['type'] not in ITEM_CLASSES:
                message = f'Item type {item["type"]} is not supported in sessions.'
                main_layout.addWidget(QLabel(message))
                logger.info(message)
                continue
            item_instance = ITEM_CLASSES[item['type']](item, storage)
            items.append(item_instance)

            item_widget = item_instance.get_widget()
            if item_widget:
                main_layout.addWidget(item_widget)

        def advance(_: QObject, event: QKeyEvent):
            if event.type() == QKeyEvent.KeyPress and not event.isAutoRepeat():
                GlobalEventFilter.get_instance().remove_key_hook(Qt.Key_Return, advance)
                for finishing_item in items:
                    finishing_item.finish()
                next_callback()
                return True

        GlobalEventFilter.get_instance().install_key_hook(Qt.Key_Return, advance)
