from typing import Union

from PyQt5.QtWidgets import QLabel, QHBoxLayout, QLineEdit, QWidget

from graphics.widgets.session.item_base import BaseItem
from utils import logger


class InputItem(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line_edit = QLineEdit()

    def get_widget(self) -> Union[QWidget, None]:
        layout = QHBoxLayout()
        layout.addWidget(QLabel(self.item_spec.get('label', '')))
        layout.addWidget(self.line_edit)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def finish(self):
        if self.item_spec['name'] in self.storage.data:
            logger.warn(f'Overwriting already present key in storage: {self.item_spec["name"]}')
        self.storage.data[self.item_spec['name']] = self.line_edit.text()
