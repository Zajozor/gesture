import time
from typing import Union

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QProgressBar

from graphics.styles import Q_PROGRESS_BAR_STYLE
from graphics.widgets.session.item_base import BaseItem

PROGRESS_TIMEOUT = 50


class PauseItem(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.advance_slide_callback())
        self.timer.setInterval(self.item_spec['timeout-ms'])
        self.timer.setSingleShot(True)

        self.show_widget = self.item_spec.get('show', True)
        self.progress_timer = QTimer()
        self.progress_timer.setInterval(PROGRESS_TIMEOUT)

    def get_widget(self) -> Union[QWidget, None]:
        self.timer.start()

        if not self.show_widget:
            return None

        progress_bar = QProgressBar()
        progress_bar.setMaximum(self.item_spec['timeout-ms'])
        progress_bar.setTextVisible(False)
        progress_bar.setStyleSheet(Q_PROGRESS_BAR_STYLE)
        start_time = time.time()

        def update_progress_bar():
            progress_bar.setValue((time.time() - start_time) * 1000)

        self.progress_timer.timeout.connect(update_progress_bar)
        self.progress_timer.start()

        return progress_bar

    def finish(self):
        self.timer.stop()
        self.progress_timer.stop()
