import time
from threading import Event
from typing import Union

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QMovie
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCheckBox, QListWidget, QHBoxLayout, QLabel, QLineEdit, \
    QFrame
from vispy import app

import constants as cn
from graphics.widgets.extensions.blink import BlinkExtension
from graphics.widgets.extensions.closable import ClosableExtension
from graphics.widgets.extensions.named import NamedExtension
from graphics.widgets.extensions.vertical_scrollable import VerticalScrollableExtension
from utils import logger


class RecordingController(QWidget):
    def __init__(self, max_displayed_gestures=10, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Here we instantiate some members that need to be bound to `self`
        # all the rest of the ui initialization happens in `_setup_..` functions
        self._recording = Event()
        self.start_button = QPushButton('⏺️')
        self.stop_button = QPushButton('⏹️')

        self.show_checkbox = QCheckBox('Show gesture')
        self.save_checkbox = QCheckBox('Save gesture')
        self.launchpad_control_enabled = False
        self.space_control_enabled = False
        self.gesture_choice = QListWidget()
        self.user_name_edit = QLineEdit('user')
        self.user_meta_edit = QLineEdit('')
        self.gesture_filename_label = QLabel('')
        self.instruction_gif_label = QLabel('')

        # Used in the final gesture filename, set when recording starts
        self.gesture_record_time: Union[str, None] = None

        self.display_column_layout = QVBoxLayout()

        self.instruction_column_layout = QVBoxLayout()
        self.setLayout(self._setup_main_layout())
        self.update_shown_gesture_filename()

        self.max_displayed_gestures = max_displayed_gestures
        self.displayed_canvases = []

        self.setup_capturing_keystrokes()

    def _setup_main_layout(self):
        main_layout = QHBoxLayout()
        main_layout.addLayout(self._setup_control_layout(), 1)
        main_layout.addLayout(self._setup_instruction_layout(), 2)
        main_layout.addLayout(self._setup_display_layout(), 3)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        return main_layout

    def _setup_control_layout(self):
        control_column_layout = QVBoxLayout()

        main_button_layout = QHBoxLayout()
        control_column_layout.addLayout(main_button_layout)

        self.start_button.setFont(cn.EMOJI_FONT)
        self.start_button.setFixedSize(50, 50)
        self.start_button.clicked.connect(self.start_recording)
        main_button_layout.addWidget(self.start_button)

        self.stop_button.setFont(cn.EMOJI_FONT)
        self.stop_button.setFixedSize(50, 50)
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        main_button_layout.addWidget(self.stop_button)

        control_column_layout.addLayout(self._setup_session_layout())

        return control_column_layout

    def _setup_session_layout(self):
        session_layout = QVBoxLayout()

        self.show_checkbox.setChecked(True)
        session_layout.addWidget(self.show_checkbox)

        self.save_checkbox.setChecked(True)
        session_layout.addWidget(self.save_checkbox)

        launchpad_control_checkbox = QCheckBox('Use launchpad control')
        launchpad_control_checkbox.setChecked(False)

        def launchpad_control_checkbox_changed(state):
            self.launchpad_control_enabled = state == Qt.Checked
            # TODO call handler etc

        launchpad_control_checkbox.stateChanged.connect(launchpad_control_checkbox_changed)
        session_layout.addWidget(launchpad_control_checkbox)

        space_control_checkbox = QCheckBox('Use space control')
        space_control_checkbox.setChecked(False)

        def space_control_checkbox_changed(state):
            self.space_control_enabled = state == Qt.Checked

        space_control_checkbox.stateChanged.connect(space_control_checkbox_changed)
        session_layout.addWidget(space_control_checkbox)

        self.gesture_choice.addItems(cn.GESTURES)
        self.gesture_choice.setCurrentRow(0)
        self.gesture_choice.setMinimumSize(250, 370)
        # noinspection PyUnresolvedReferences
        self.gesture_choice.currentTextChanged.connect(self.update_shown_gesture_filename)

        session_layout.addWidget(self.gesture_choice)

        self.user_name_edit.textChanged.connect(self.update_shown_gesture_filename)
        user_name_edit_layout = QHBoxLayout()
        user_name_edit_layout.addWidget(QLabel('User:'))
        user_name_edit_layout.addWidget(self.user_name_edit)
        session_layout.addLayout(user_name_edit_layout)

        self.user_meta_edit.textChanged.connect(self.update_shown_gesture_filename)
        user_meta_edit_layout = QHBoxLayout()
        user_meta_edit_layout.addWidget(QLabel('Meta:'))
        user_meta_edit_layout.addWidget(self.user_meta_edit)
        session_layout.addLayout(user_meta_edit_layout)

        session_layout.addWidget(QLabel('Example resulting filename:'))
        session_layout.addWidget(self.gesture_filename_label)

        return session_layout

    def _setup_instruction_layout(self):
        self.instruction_column_layout.addWidget(self.instruction_gif_label)

        def update_shown_gif(new_gesture):
            gif_path = cn.MODELS_FOLDER / f'{cn.NICE_TO_ESCAPED_GESTURES[new_gesture]}.gif'
            if gif_path.exists():
                movie = QMovie(gif_path.as_posix())
                movie.start()
                self.instruction_gif_label.setMovie(movie)
                self.instruction_gif_label.setText('')
            else:
                self.instruction_gif_label.setMovie(None)
                self.instruction_gif_label.setText(f'Missing gif for "{new_gesture}".')

        # noinspection PyUnresolvedReferences
        self.gesture_choice.currentTextChanged.connect(update_shown_gif)
        update_shown_gif(self.gesture_choice.selectedItems()[0].text())
        self.instruction_gif_label.setScaledContents(True)
        scale = 0.5
        self.instruction_gif_label.setFixedSize(960 * scale, 540 * scale)
        self.instruction_gif_label.setAlignment(Qt.AlignCenter)
        self.instruction_gif_label.setFrameStyle(QFrame.Panel)
        return self.instruction_column_layout

    def _setup_display_layout(self):
        return VerticalScrollableExtension(self.display_column_layout)

    def setup_capturing_keystrokes(self):
        # TODO maybe profile this? possibly register only somewhere
        QtWidgets.QApplication.instance().installEventFilter(self)

    def eventFilter(self, source, event):
        if self.space_control_enabled and type(event) == QKeyEvent:
            key_event = QKeyEvent(event)
            if key_event.key() == Qt.Key_Space:
                event_type = key_event.type()
                if event_type == QKeyEvent.KeyPress and not key_event.isAutoRepeat():
                    self.start_recording()
                    return True
                if event_type == QKeyEvent.KeyRelease:
                    self.stop_recording()
                    return True
        return super().eventFilter(source, event)

    def start_recording(self):
        if self._recording.is_set():
            logger.warning('Recording was started multiple times.')
        self._recording.set()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.gesture_record_time = time.strftime(cn.GESTURE_NAME_DATETIME_FORMAT)

    def stop_recording(self):
        if not self._recording.is_set():
            logger.warning('Recording was stopped multiple times.')
        self._recording.clear()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    @property
    def save(self):
        return self.save_checkbox.isChecked()

    @property
    def show(self):
        return self.show_checkbox.isChecked()

    @property
    def readable_gesture_name(self):
        return self.gesture_choice.selectedItems()[0].text()

    @property
    def full_gesture_filename(self):
        return cn.GESTURE_NAME_SEPARATOR.join([
            cn.GESTURE_PREFIX,
            cn.NICE_TO_ESCAPED_GESTURES[self.readable_gesture_name],
            self.user_name_edit.text() + (
                (cn.GESTURE_META_SEPARATOR + self.user_meta_edit.text())
                if self.user_meta_edit.text() else ''
            ),
            self.gesture_record_time or '',
        ])

    def update_shown_gesture_filename(self):
        self.gesture_filename_label.setText(self.full_gesture_filename[:-15] + '...')

    def add_displayed_canvas(self, canvas: app.canvas, name=None, record_time=None):
        self.displayed_canvases.append(canvas)
        widget = canvas.native
        widget = NamedExtension(f'{name or ""} - {record_time or ""}', widget)
        widget = BlinkExtension(widget)
        widget = ClosableExtension(widget)
        widget.setMinimumWidth(600)
        widget.setFixedHeight(200)
        self.display_column_layout.addWidget(widget)

        while len(self.displayed_canvases) > self.max_displayed_gestures:
            self.displayed_canvases[0].on_close()
            self.displayed_canvases[0].native.setParent(None)
            self.display_column_layout.takeAt(0).widget().deleteLater()
            del self.displayed_canvases[0]
