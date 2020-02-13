from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLabel

import constants as cn
from graphics.event_filter import GlobalEventFilter
from graphics.widgets.session.base_slide import BaseSlide

MEDIA_FOLDER = cn.SESSIONS_FOLDER / 'media'


class InfoSlide(BaseSlide):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(main_layout)

        def advance(_: QObject, event: QKeyEvent):
            if event.type() == QKeyEvent.KeyPress and not event.isAutoRepeat():
                GlobalEventFilter.get_instance().remove_key_hook(Qt.Key_Return, advance)
                self.next_callback()
                return True

        GlobalEventFilter.get_instance().install_key_hook(Qt.Key_Return, advance)

        if 'text' in self.spec:
            text_label = QLabel(self.spec['text'])
            text_label.setFont(cn.EMOJI_FONT)
            main_layout.addWidget(text_label)

        if 'image' in self.spec:
            image_label = QLabel()
            pixmap = QPixmap(str(MEDIA_FOLDER / self.spec['image']))
            image_label.setPixmap(pixmap)
            main_layout.addWidget(image_label)

        if self.spec.get('next', True):
            next_button = QPushButton('✅')
            next_button.setFont(cn.EMOJI_FONT)
            next_button.setFixedSize(50, 50)
            next_button.clicked.connect(self.next_callback)
            main_layout.addWidget(next_button)
