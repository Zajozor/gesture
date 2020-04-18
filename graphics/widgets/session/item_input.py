from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QLineEdit, QWidget, QPushButton

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
        layout.setAlignment(Qt.AlignCenter)

        if 'choices' in self.item_spec:
            for choice in self.item_spec['choices']:
                button = QPushButton(choice)

                def choice_callback(text):
                    return lambda: self.line_edit.setText(text)

                button.clicked.connect(choice_callback(choice))
                layout.addWidget(button)

        widget = QWidget()
        widget.setLayout(layout)
        widget.setMaximumWidth(600)
        return widget

    def finish(self):
        if self.item_spec['name'] in self.storage.data:
            logger.warn(f'Overwriting already present key in storage: {self.item_spec["name"]}')
        self.storage.data[self.item_spec['name']] = self.line_edit.text()
