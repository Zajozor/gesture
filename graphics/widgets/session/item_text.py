from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QWidget

import constants as cn
from graphics.widgets.session.item_base import BaseItem


class TextItem(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.text = self.item_spec.get('text', '')
        font_spec = self.item_spec.get('font', None)
        self.font = QFont(*font_spec) if font_spec else cn.EMOJI_FONT

        self.style_sheet_active = 'color' in self.item_spec or 'bg-color' in self.item_spec
        color_style_sheet = f'color: {self.item_spec["color"]}' if 'color' in self.item_spec else ''
        bg_color_style_sheet = f'background-color: {self.item_spec["bg-color"]}' if 'bg-color' in self.item_spec else ''
        self.style_sheet = f'QLabel {{ {color_style_sheet} {bg_color_style_sheet} }}'

    def get_widget(self) -> Union[QWidget, None]:
        label = QLabel(self.text)
        if self.style_sheet_active:
            label.setStyleSheet(self.style_sheet)
        label.setAlignment(Qt.AlignHCenter)
        label.setFont(self.font)
        return label

    def finish(self):
        pass
