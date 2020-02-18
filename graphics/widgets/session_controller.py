import os

import yaml
from yaml.parser import ParserError
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QListWidget, QStackedLayout

import constants as cn
from graphics.widgets.session.slide import Slide
from graphics.widgets.session.storage import SessionStorage
from utils import logger, application_state


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
        sessions = map(lambda name: name.rsplit('.', 1)[0],
                       filter(lambda name: name.endswith('.yml'),
                              os.listdir(cn.SESSIONS_FOLDER)))
        for session in sessions:
            self.selection_listbox.addItem(session)
        self.selection_listbox.setCurrentRow(0)

    def play_session(self, session):
        self.stacked_layout.setCurrentIndex(1)
        self.session_active = True
        application_state.get_main_window().set_tab_switching_enabled(False)

        with open(cn.SESSIONS_FOLDER / f'{session}.yml') as session_file:
            try:
                session_spec = yaml.full_load(session_file)
            except ParserError:
                self.stacked_layout.setCurrentIndex(0)
                self.session_active = False
                logger.info(f'Malformed yaml file: {session}.yml')
                return

        session_length = len(session_spec['slides'])
        current_session_index = -1
        current_slide_widget = None
        session_storage = SessionStorage()

        def next_slide():
            nonlocal current_session_index, session_length, current_slide_widget
            logger.debug(f'Storage after slide {current_session_index}: {session_storage}')

            current_session_index += 1

            if current_slide_widget:
                current_slide_widget.close()

            if current_session_index == session_length:
                self.stacked_layout.setCurrentIndex(0)
                self.session_active = False
                application_state.get_main_window().set_tab_switching_enabled(True)
                return

            slide_spec = session_spec['slides'][current_session_index]
            current_slide_widget = Slide(slide_spec, next_slide, session_storage)
            self.play_layout.addWidget(current_slide_widget)
            current_slide_widget.activateWindow()

        next_slide()
