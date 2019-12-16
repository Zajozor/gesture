from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCheckBox, QListWidget

import constants as cn


class RecordingController(QWidget):
    def __init__(self, start_callback, stop_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO make into widget
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.setLayout(layout)

        start_button = QPushButton('⏺️')
        start_button.setFont(cn.EMOJI_FONT)
        start_button.setFixedSize(50, 50)
        layout.addWidget(start_button)

        def start_recording():
            start_button.setEnabled(False)
            stop_button.setEnabled(True)
            start_callback()
        start_button.clicked.connect(start_recording)

        stop_button = QPushButton('⏹️')
        stop_button.setFont(cn.EMOJI_FONT)
        stop_button.setFixedSize(50, 50)
        layout.addWidget(stop_button)

        def stop_recording():
            start_button.setEnabled(True)
            stop_button.setEnabled(False)
            stop_callback()
        stop_button.clicked.connect(stop_recording)
        stop_button.setEnabled(False)

        self.show_checkbox = QCheckBox('Show gesture')
        layout.addWidget(self.show_checkbox)
        self.show_checkbox.setChecked(True)

        self.save_checkbox = QCheckBox('Save gesture')
        layout.addWidget(self.save_checkbox)
        self.save_checkbox.setChecked(True)

        self.gesture_choice = QListWidget()
        self.gesture_choice.addItems(cn.GESTURES)
        layout.addWidget(self.gesture_choice)
        self.gesture_choice.setCurrentRow(0)

    @property
    def save(self):
        return self.save_checkbox.isChecked()

    @property
    def show(self):
        return self.show_checkbox.isChecked()

    def gesture_name(self):
        return self.gesture_choice.selectedItems()[0].text()
