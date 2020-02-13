import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QListWidget, QStackedLayout

import constants as cn
from graphics.widgets.session.main import SLIDE_WIDGETS
from graphics.widgets.session.storage import SessionStorage


class SessionController(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selection_listbox = QListWidget()

        self.play_session_button = QPushButton('Play')
        self.play_session_button.clicked.connect(
            lambda: self.play_session(self.selection_listbox.selectedItems()[0].text()))

        self.selection_layout = QHBoxLayout()
        select_label = QLabel('Please select a session:')
        self.selection_layout.addWidget(select_label)
        self.selection_layout.addWidget(self.selection_listbox)
        self.selection_layout.addWidget(self.play_session_button)
        self.selection_layout.setSpacing(50)

        self.play_layout = QVBoxLayout()
        self.play_layout.setSpacing(25)
        self.play_layout.setAlignment(Qt.AlignCenter)

        self.stacked_layout = QStackedLayout()
        selection_layout_widget_wrapper = QWidget()
        selection_layout_widget_wrapper.setLayout(self.selection_layout)
        self.stacked_layout.addWidget(selection_layout_widget_wrapper)

        play_layout_widget_wrapper = QWidget()
        play_layout_widget_wrapper.setLayout(self.play_layout)
        self.stacked_layout.addWidget(play_layout_widget_wrapper)

        huge_font = QFont('Menlo', 32)
        select_label.setFont(huge_font)
        self.selection_listbox.setFont(huge_font)
        self.play_session_button.setFont(huge_font)

        self.setLayout(self.stacked_layout)

        self.load_sessions()

        self.session_active = False

    def is_session_active(self):
        return self.session_active

    def load_sessions(self):
        sessions = map(lambda name: name[:-5],
                       filter(lambda name: name.endswith('.json'),
                              os.listdir(cn.SESSIONS_FOLDER)))
        for session in sessions:
            self.selection_listbox.addItem(session)
        self.selection_listbox.setCurrentRow(0)

    def play_session(self, session):
        self.stacked_layout.setCurrentIndex(1)
        self.session_active = True

        with open(cn.SESSIONS_FOLDER / f'{session}.json') as session_file:
            session_spec = json.load(session_file)

        session_length = len(session_spec)
        current_session_index = -1
        current_slide_widget = None
        session_storage = SessionStorage()

        def next_slide():
            nonlocal current_session_index, session_length, current_slide_widget
            current_session_index += 1

            if current_slide_widget:
                current_slide_widget.close()

            if current_session_index == session_length:
                self.stacked_layout.setCurrentIndex(0)
                self.session_active = False
                return

            slide_spec = session_spec[current_session_index]
            current_slide_widget = SLIDE_WIDGETS[slide_spec['type']](spec=slide_spec,
                                                                     next_callback=next_slide,
                                                                     storage=session_storage)
            self.play_layout.addWidget(current_slide_widget)
            current_slide_widget.activateWindow()

        next_slide()
