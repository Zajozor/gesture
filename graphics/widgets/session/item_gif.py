from typing import Union

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel, QWidget, QFrame, QVBoxLayout, QProgressBar

import constants as cn
from graphics.widgets.session.item_base import BaseItem

MEDIA_FOLDER = cn.SESSIONS_FOLDER / 'media'


class GIFItem(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gesture_id = self.item_spec['id']
        self.verbose_name = cn.GESTURES[self.gesture_id].verbose_name
        self.gif_path = cn.MODELS_FOLDER / f'{cn.GESTURES[self.gesture_id].slug}.gif'

        if not self.gif_path.exists():
            raise ValueError(f'Missing gif at {self.gif_path}.')
        self.width = self.item_spec.get('width', cn.GIF_RECORDING_SIZE[0] * cn.GIF_DISPLAY_SIZE)
        self.height = self.item_spec.get('height', cn.GIF_RECORDING_SIZE[1] * cn.GIF_DISPLAY_SIZE)

    def get_widget(self) -> Union[QWidget, None]:
        name_label = QLabel(self.verbose_name)
        name_label.setAlignment(Qt.AlignCenter)

        gif_label = QLabel()
        movie = QMovie(self.gif_path.as_posix())
        movie.start()
        gif_label.setMovie(movie)

        gif_label.setScaledContents(True)
        gif_label.setFixedSize(self.width, self.height)
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setFrameStyle(QFrame.Panel)

        gif_progress_bar = QProgressBar()
        gif_progress_bar.setMaximum(movie.frameCount() - 1)

        def update_animation_progress(frame_index):
            gif_progress_bar.setValue(frame_index)
            if frame_index == 0:
                movie.setPaused(True)
                QTimer.singleShot(1000, lambda: movie.setPaused(False))

        movie.frameChanged.connect(update_animation_progress)

        layout = QVBoxLayout()
        layout.addWidget(name_label)
        layout.addWidget(gif_label)
        layout.addWidget(gif_progress_bar)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        widget = QWidget()
        widget.setLayout(layout)
        widget.setFixedSize(self.width, self.height + 50)
        return widget

    def finish(self):
        pass
