from typing import Union

from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QMovie, QKeyEvent
from PyQt5.QtWidgets import QLabel, QWidget, QFrame, QVBoxLayout, QProgressBar, QGraphicsDropShadowEffect

import constants as cn
from graphics.event_filter import GlobalEventFilter
from graphics.widgets.session.item_base import BaseItem
from utils import logger

MEDIA_FOLDER = cn.SESSIONS_FOLDER / 'media'


class GIFItem(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gesture_id = self.item_spec['id']
        self.verbose_name = cn.GESTURES[self.gesture_id].verbose_name
        gif_path = cn.MODELS_FOLDER / f'{cn.GESTURES[self.gesture_id].slug}.gif'

        if not gif_path.exists():
            raise ValueError(f'Missing gif at {gif_path}.')

        self.width = self.item_spec.get('width', cn.GIF_RECORDING_SIZE[0] * cn.GIF_DISPLAY_SIZE)
        self.height = self.item_spec.get('height', cn.GIF_RECORDING_SIZE[1] * cn.GIF_DISPLAY_SIZE)

        self.movie = QMovie(gif_path.as_posix())
        self.gif_progress_bar = QProgressBar()

    def get_widget(self) -> Union[QWidget, None]:
        name_label = QLabel(self.verbose_name)
        name_label.setAlignment(Qt.AlignCenter)

        gif_label = QLabel()
        gif_label.setMovie(self.movie)
        self.movie.start()

        gif_label.setScaledContents(True)
        gif_label.setFixedSize(self.width, self.height)
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setFrameStyle(QFrame.Panel)

        last_frame = self.movie.frameCount() - 1
        self.gif_progress_bar.setMaximum(last_frame)

        def update_animation_progress(frame_index):
            try:
                self.gif_progress_bar.setValue(frame_index)
                if frame_index == last_frame:
                    self.movie.setPaused(True)
                    QTimer.singleShot(1000, lambda: self.movie.setPaused(False))
            except RuntimeError:
                # This is a temporary fix, because the parent widget is deleted manually
                logger.debug('Gif Item Progress bar deleted before stopping.')
                self.movie.stop()

        self.movie.frameChanged.connect(update_animation_progress)
        GlobalEventFilter.get_instance().install_key_hook(Qt.Key_Space, self.replay_movie)

        layout = QVBoxLayout()
        layout.addWidget(name_label)
        layout.addWidget(gif_label)
        layout.addWidget(self.gif_progress_bar)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        widget = QWidget()
        widget.setLayout(layout)
        widget.setFixedSize(self.width, self.height + 50)
        return widget

    def replay_movie(self, _, event: QEvent):
        key_event = QKeyEvent(event)
        if key_event.type() == QKeyEvent.KeyPress and not key_event.isAutoRepeat():
            self.movie.stop()
            self.movie.start()
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(20)
            effect.setXOffset(0)
            effect.setYOffset(0)
            effect.setColor(Qt.red)
            self.gif_progress_bar.setGraphicsEffect(effect)

        if key_event.type() == QKeyEvent.KeyRelease:
            self.gif_progress_bar.setGraphicsEffect(None)

    def finish(self):
        self.movie.stop()
        GlobalEventFilter.get_instance().remove_key_hook(Qt.Key_Space, self.replay_movie)
