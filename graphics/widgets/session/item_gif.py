from pathlib import Path
from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel, QWidget, QFrame

import constants as cn
from graphics.widgets.session.item_base import BaseItem

MEDIA_FOLDER = cn.SESSIONS_FOLDER / 'media'


class GIFItem(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gif_path = Path(cn.MODELS_FOLDER) / f'{self.item_spec["gif"]}.gif'
        self.width = self.item_spec.get('width', cn.GIF_RECORDING_SIZE[0] * cn.GIF_DISPLAY_SIZE)
        self.height = self.item_spec.get('height', cn.GIF_RECORDING_SIZE[1] * cn.GIF_DISPLAY_SIZE)

    def get_widget(self) -> Union[QWidget, None]:
        label = QLabel()
        if self.gif_path.exists():
            movie = QMovie(self.gif_path.as_posix())
            movie.start()
            label.setMovie(movie)
        else:
            label.setMovie(None)
            label.setText(f'Missing gif for "{self.gif_path}".')

        label.setScaledContents(True)
        label.setFixedSize(self.width, self.height)
        label.setAlignment(Qt.AlignCenter)
        label.setFrameStyle(QFrame.Panel)
        return label

    def finish(self):
        pass
