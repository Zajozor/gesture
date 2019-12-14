import os

import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QApplication

import constants as cn
from graphics.widgets.signal_grid_canvas import create_simple_canvas


class DataViewer(QWidget):
    def __init__(self, show=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout()

        refresh_button = QPushButton('Refresh')
        refresh_button.clicked.connect(self.refresh_list)
        layout.addWidget(refresh_button)

        self.show_button = QPushButton('Show')
        layout.addWidget(self.show_button)
        self.show_button.clicked.connect(self.show_selected)

        self.gesture_list = QListWidget()
        layout.addWidget(self.gesture_list)

        self.refresh_list()
        self.gesture_list.setCurrentRow(0)

        self.setLayout(layout)
        if show:
            self.window().show()

        self.shown_canvases = []

    def refresh_list(self):
        gestures = sorted(os.listdir(os.path.join('..', cn.DATA_FOLDER)))
        self.gesture_list.clear()
        self.gesture_list.addItems(gestures)

    def show_selected(self):
        filename = self.gesture_list.selectedItems()[0].text()
        selected_file = os.path.join('..', cn.DATA_FOLDER, filename)
        data = np.load(selected_file)
        self.shown_canvases.append(create_simple_canvas(data, data.shape[0], filename))


if __name__ == '__main__':
    app = QApplication([])
    d = DataViewer(show=True)
    app.exec_()
