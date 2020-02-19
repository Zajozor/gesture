from typing import Dict, Type
from typing import Union, List

from PyQt5.QtWidgets import QHBoxLayout, QWidget

from graphics.widgets.session.item_base import BaseItem
from graphics.widgets.session.item_gif import GIFItem
from graphics.widgets.session.item_image import ImageItem
from graphics.widgets.session.item_input import InputItem
from graphics.widgets.session.item_pause import PauseItem
from graphics.widgets.session.item_record import RecordItem
from graphics.widgets.session.item_signal import SignalItem
from graphics.widgets.session.item_state import StateItem
from graphics.widgets.session.item_text import TextItem
from utils import logger


def get_item_from_spec(item_spec, storage, advance_slide_callback):
    if item_spec['type'] not in ITEM_CLASSES:
        message = f'Item type {item_spec["type"]} is not supported in sessions, please check session spec.'
        logger.info(message)
        return get_item_from_spec({'type': 'text', 'text': message, 'color': 'red'}, storage, advance_slide_callback)

    return ITEM_CLASSES[item_spec['type']](item_spec, storage, advance_slide_callback)


class HStackItem(BaseItem):
    """
    This Item stacks widgets horizontally.
    It is placed in the common file due to cyclical dependency:
    get_item_from_spec -> ITEM_CLASSES -> HStackItem -> get_item_from_spec ...
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sub_items: List[BaseItem] = [
            get_item_from_spec(item_spec, self.storage, self.advance_slide_callback)
            for item_spec in self.item_spec['items']
        ]

    def get_widget(self) -> Union[QWidget, None]:
        layout = QHBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(0, 0, 0, 0)
        for sub_item in self.sub_items:
            sub_widget = sub_item.get_widget()
            if sub_widget:
                layout.addWidget(sub_widget)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def finish(self):
        for sub_item in self.sub_items:
            sub_item.finish()


ITEM_CLASSES: Dict[str, Type[BaseItem]] = {
    'text': TextItem,
    'image': ImageItem,
    'input': InputItem,
    'signal': SignalItem,
    'record': RecordItem,
    'state': StateItem,
    'hstack': HStackItem,
    'pause': PauseItem,
    'gif': GIFItem,
}
