from typing import Dict

from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QLineEdit

import constants as cn
from graphics.event_filter import GlobalEventFilter
from graphics.widgets.session.base_slide import BaseSlide

MEDIA_FOLDER = cn.SESSIONS_FOLDER / 'media'


class InputSlide(BaseSlide):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(main_layout)
        input_widgets: Dict[str, QLineEdit] = {}

        def advance(_: QObject, event: QKeyEvent):
            if event.type() == QKeyEvent.KeyPress and not event.isAutoRepeat():
                GlobalEventFilter.get_instance().remove_key_hook(Qt.Key_Return, advance)
                for input_widget in input_widgets:
                    self.storage.data[input_widget] = input_widgets[input_widget].text()

                self.next_callback()
                return True

        GlobalEventFilter.get_instance().install_key_hook(Qt.Key_Return, advance)

        for input_field in self.spec['inputs']:
            field_layout = QHBoxLayout()
            field_layout.addWidget(QLabel(self.spec['inputs'][input_field]))
            input_widgets[input_field] = QLineEdit()
            field_layout.addWidget(input_widgets[input_field])

            main_layout.addLayout(field_layout)

        main_layout.addWidget(QLabel('Press enter to continue'))
