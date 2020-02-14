from typing import Union

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget

import constants as cn
from graphics.widgets.session.item_base import BaseItem

MEDIA_FOLDER = cn.SESSIONS_FOLDER / 'media'


class ImageItem(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pixmap = QPixmap(str(MEDIA_FOLDER / self.item_spec['image']))

    def get_widget(self) -> Union[QWidget, None]:
        label = QLabel()
        label.setPixmap(self.pixmap)
        return label

    def finish(self):
        pass
