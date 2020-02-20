import time
from os import path
from threading import Thread
from typing import Union

import numpy as np
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QKeyEvent, QMovie
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCheckBox, QListWidget, QHBoxLayout, QLabel, QLineEdit, \
    QFrame

import constants as cn
from graphics.event_filter import GlobalEventFilter
from graphics.styles import Q_PUSH_BUTTON_TOGGLE_STYLE
from graphics.widgets.extensions.blink import BlinkExtension
from graphics.widgets.extensions.closable import ClosableExtension
from graphics.widgets.extensions.named import NamedExtension
from graphics.widgets.extensions.vertical_scrollable import VerticalScrollableExtension
from graphics.widgets.signal_static import StaticSignalWidget
from processing.consumers.recording import RecordingConsumer
from utils import logger, application_state


class RecordingController(QWidget):
    def __init__(self, max_displayed_static_signals=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Here we instantiate some members that need to be bound to `self`
        # all the rest of the ui initialization happens in `_setup_..` functions
        self.start_button = QPushButton('⏺️')
        self.stop_button = QPushButton('⏹️')

        self.show_checkbox = QCheckBox('Show gesture')
        self.save_checkbox = QCheckBox('Save gesture')
        self.launchpad_control_checkbox = QCheckBox('Use launchpad control')
        self.space_control_checkbox = QCheckBox('Use space control')

        self.gesture_choice = QListWidget()
        self.user_name_edit = QLineEdit('user')
        self.user_meta_edit = QLineEdit('')
        self.gesture_filename_label = QLabel('')
        self.instruction_gif_label = QLabel()

        # Used in the final gesture filename, set when recording starts
        self.gesture_record_time: Union[str, None] = None

        self.display_column_layout = QVBoxLayout()
        self.instruction_column_layout = QVBoxLayout()

        self.setLayout(self._setup_main_layout())
        self.update_shown_gesture_filename()

        self.max_displayed_static_signals = max_displayed_static_signals
        self.displayed_static_signals = []
        self.consumer = RecordingConsumer()

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
        self.start_button.setStyleSheet(Q_PUSH_BUTTON_TOGGLE_STYLE)
        main_button_layout.addWidget(self.start_button)

        self.stop_button.setFont(cn.EMOJI_FONT)
        self.stop_button.setFixedSize(50, 50)
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet(Q_PUSH_BUTTON_TOGGLE_STYLE)
        main_button_layout.addWidget(self.stop_button)

        control_column_layout.addLayout(self._setup_session_layout())
        return control_column_layout

    def _setup_session_layout(self):
        session_layout = QVBoxLayout()

        self.show_checkbox.setChecked(True)
        session_layout.addWidget(self.show_checkbox)

        self.save_checkbox.setChecked(True)
        session_layout.addWidget(self.save_checkbox)

        self.launchpad_control_checkbox.setChecked(False)

        def launchpad_control_checkbox_changed(state):
            self.launchpad_control_enabled = state == Qt.Checked
            # TODO call handler etc

        self.launchpad_control_checkbox.stateChanged.connect(launchpad_control_checkbox_changed)
        session_layout.addWidget(self.launchpad_control_checkbox)

        self.space_control_checkbox.setChecked(False)

        def space_control_checkbox_changed(state):
            self.space_control_enabled = state == Qt.Checked
            application_state.main_window.set_tab_switching_enabled(not self.space_control_enabled)
            global_event_filter = GlobalEventFilter.get_instance()

            if self.space_control_enabled:
                global_event_filter.install_key_hook(Qt.Key_Space, self.space_callback)
            else:
                global_event_filter.remove_key_hook(Qt.Key_Space, self.space_callback)

        self.space_control_checkbox.stateChanged.connect(space_control_checkbox_changed)
        session_layout.addWidget(self.space_control_checkbox)

        self.gesture_choice.addItems(map(str, cn.GESTURES))
        self.gesture_choice.setCurrentRow(0)
        self.gesture_choice.setMinimumSize(250, 250)
        # noinspection PyUnresolvedReferences
        self.gesture_choice.currentRowChanged.connect(self.update_shown_gesture_filename)
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

        def update_shown_gif(index):
            gesture = cn.GESTURES[index]
            gif_path = cn.MODELS_FOLDER / f'{gesture.slug}.gif'
            if gif_path.exists():
                movie = QMovie(gif_path.as_posix())
                movie.start()
                self.instruction_gif_label.setMovie(movie)
                self.instruction_gif_label.setText('')
            else:
                self.instruction_gif_label.setMovie(None)
                self.instruction_gif_label.setText(f'Missing gif for "{gesture.verbose_name}" - {gesture.slug}.gif')

        # noinspection PyUnresolvedReferences
        self.gesture_choice.currentRowChanged.connect(update_shown_gif)
        update_shown_gif(self.selected_gesture_index)
        self.instruction_gif_label.setScaledContents(True)
        self.instruction_gif_label.setFixedSize(cn.GIF_RECORDING_SIZE[0] * cn.GIF_DISPLAY_SIZE,
                                                cn.GIF_RECORDING_SIZE[1] * cn.GIF_DISPLAY_SIZE)
        self.instruction_gif_label.setAlignment(Qt.AlignCenter)
        self.instruction_gif_label.setFrameStyle(QFrame.Panel)
        return self.instruction_column_layout

    def _setup_display_layout(self):
        return VerticalScrollableExtension(self.display_column_layout)

    def space_callback(self, _: QObject, event: QKeyEvent) -> bool:
        event_type = event.type()
        if event_type == QKeyEvent.KeyPress and not event.isAutoRepeat():
            self.start_recording()
            return True
        if event_type == QKeyEvent.KeyRelease:
            self.stop_recording()
            return True
        return False

    def start_recording(self):
        self.consumer.start_recording()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.gesture_record_time = time.strftime(cn.FILE_NAME_DATETIME_FORMAT)

    def stop_recording(self):
        self.consumer.stop_recording()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        if self.save_checkbox.isChecked():
            self.save_gesture_async()
        if self.show_checkbox.isChecked():
            signal_widget = StaticSignalWidget()
            signal_widget.plot_data(self.consumer.gesture_data)
            self.add_displayed_signal(
                signal_widget,
                cn.GESTURES[self.selected_gesture_index].verbose_name,
                self.gesture_record_time,
            )

    def save_gesture_async(self):
        if self.consumer.recording_active.is_set():
            logger.warning('Saving in the middle of recording.')

        def save_gesture(filename, gesture_name, gesture_data):
            logger.warning(f'Saving gesture {gesture_name} to {filename}.')
            np.save(path.join(cn.DATA_FOLDER, filename), gesture_data)

        Thread(target=save_gesture, args=(
            self.full_gesture_filename,
            cn.GESTURES[self.selected_gesture_index].verbose_name,
            self.consumer.gesture_data
        )).start()

    @property
    def selected_gesture_index(self):
        return self.gesture_choice.selectedIndexes()[0].row()

    @property
    def full_gesture_filename(self):
        return cn.FILE_NAME_SEPARATOR.join([
            cn.GESTURE_PREFIX,
            str(self.selected_gesture_index),
            self.user_name_edit.text() + (
                (cn.GESTURE_META_SEPARATOR + self.user_meta_edit.text())
                if self.user_meta_edit.text() else ''
            ),
            self.gesture_record_time or '',
        ])

    def update_shown_gesture_filename(self):
        self.gesture_filename_label.setText(self.full_gesture_filename[:25] + '...')

    def add_displayed_signal(self, static_signal: StaticSignalWidget, name=None, record_time=None):
        widget = NamedExtension(f'{name or ""} - {record_time or ""}', static_signal)
        widget = BlinkExtension(widget)
        widget = ClosableExtension(widget)
        widget.setMinimumWidth(600)
        widget.setFixedHeight(200)
        self.displayed_static_signals.append(widget)
        self.display_column_layout.addWidget(widget)

        while len(self.displayed_static_signals) > self.max_displayed_static_signals:
            self.displayed_static_signals[0].close()
            del self.displayed_static_signals[0]
