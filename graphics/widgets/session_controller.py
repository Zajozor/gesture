import os
import pickle
import time
from random import choice

import yaml
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QListWidget, QStackedLayout, \
    QProgressBar
from yaml.parser import ParserError

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
        self.play_layout.setSpacing(5)
        self.play_layout.setContentsMargins(0, 0, 0, 0)
        self.play_layout.setAlignment(Qt.AlignCenter)

        self.stacked_layout = QStackedLayout()
        selection_layout_widget_wrapper = QWidget()
        selection_layout_widget_wrapper.setLayout(self.selection_layout)
        self.stacked_layout.addWidget(selection_layout_widget_wrapper)

        play_layout_widget_wrapper = QWidget()
        outer_play_layout = QVBoxLayout()
        outer_play_layout.setContentsMargins(0, 0, 0, 0)
        outer_play_layout.setSpacing(5)
        self.session_progress_bar = QProgressBar()
        outer_play_layout.addWidget(self.session_progress_bar)
        outer_play_layout.addLayout(self.play_layout)

        play_layout_widget_wrapper.setLayout(outer_play_layout)
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
        sessions = sorted(
            map(lambda name: name.rsplit('.', 1)[0],
                filter(lambda name: name.endswith('.yml'),
                       os.listdir(cn.SESSIONS_FOLDER)
                       )
                )
        )
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
        session_spec['slides'] = SessionController.expand_slides(session_spec['slides'])

        session_length = len(session_spec['slides'])
        self.session_progress_bar.setMaximum(session_length)
        current_session_index = -1
        current_slide_widget = None
        session_storage = SessionStorage()

        def next_slide_callback(quit_session=False):
            nonlocal current_session_index, session_length, current_slide_widget

            current_session_index += 1
            self.session_progress_bar.setValue(current_session_index)

            if current_slide_widget:
                current_slide_widget.close()
                current_slide_widget.deleteLater()

            if current_session_index == session_length or quit_session:
                self.stacked_layout.setCurrentIndex(0)
                self.session_active = False
                SessionController.save_session_data(session_storage, quit_session)
                application_state.get_main_window().set_tab_switching_enabled(True)
                return

            slide_spec = session_spec['slides'][current_session_index]
            current_slide_widget = Slide(slide_spec, next_slide_callback, session_storage)
            self.play_layout.addWidget(current_slide_widget)
            current_slide_widget.activateWindow()

        next_slide_callback()

    @staticmethod
    def save_session_data(storage, quit_session=False):
        session_name = cn.FILE_NAME_SEPARATOR.join([
            cn.SESSION_PREFIX,
            time.strftime(cn.FILE_NAME_DATETIME_FORMAT)
        ])
        if quit_session:
            session_name += '.quit'
        with open(cn.DATA_FOLDER / session_name, 'wb') as f:
            pickle.dump(storage.data, f)
        logger.info(f'Successfully saved session {session_name}')

    @staticmethod
    def expand_slides(slides):
        """
        Performs expansion upon special slide types, that repeat/shuffle somehow
        """

        def replace_in_slide(needle, new_value, item):
            if type(item) == list or type(item) == tuple:
                return type(item)(map(lambda x: replace_in_slide(needle, new_value, x), item))
            if type(item) == dict:
                return dict(map(lambda x: replace_in_slide(needle, new_value, x), list(item.items())))
            if type(item) == str and item[0] == '$':
                return item[1:].replace(needle, new_value)
            return new_value if item == needle else item

        expanded_slides = []
        for slide in slides:
            if 'items' in slide:
                expanded_slides.append(slide)
                continue
            if 'shuffle' in slide:
                template = slide['shuffle']['template']
                values = slide['shuffle']['values']
                while len(values) > 0:
                    chosen_value = choice(values)
                    values.remove(chosen_value)

                    # add slide
                    expanded_slides.append(replace_in_slide(template, chosen_value, slide['item']))

                    # remove value
                    if len(values) > 0:
                        expanded_slides.append(slide['between'])
                continue
            raise ValueError(f'Unknown slide format: {slide}')
        return expanded_slides
