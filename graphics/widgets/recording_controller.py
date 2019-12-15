from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCheckBox, QListWidget

import constants as cn


class RecordingController:
    def __init__(self, start_callback, stop_callback):
        # TODO make into widget
        self.window = QWidget()
        layout = QVBoxLayout()

        self.start_button = QPushButton('Start')
        layout.addWidget(self.start_button)
        self.start_button.clicked.connect(start_callback)

        self.stop_button = QPushButton('Stop')
        layout.addWidget(self.stop_button)
        self.stop_button.clicked.connect(stop_callback)
        self.stop_button.setEnabled(False)

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

        self.window.setLayout(layout)
        self.window.show()

    @property
    def save(self):
        return self.save_checkbox.isChecked()

    @property
    def show(self):
        return self.show_checkbox.isChecked()

    def gesture_name(self):
        return self.gesture_choice.selectedItems()[0].text()
