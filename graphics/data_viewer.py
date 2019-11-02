import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QApplication
import os
import constants as cn
from graphics.simple_canvas import create_simple_canvas


class DataViewer:
    def __init__(self):
        self.window = QWidget()
        layout = QVBoxLayout()

        self.refresh_button = QPushButton('Refresh')
        layout.addWidget(self.refresh_button)
        self.refresh_button.clicked.connect(self.refresh_list)

        self.show_button = QPushButton('Show')
        layout.addWidget(self.show_button)
        self.show_button.clicked.connect(self.show_selected)

        self.gesture_list = QListWidget()
        layout.addWidget(self.gesture_list)

        self.refresh_list()
        self.gesture_list.setCurrentRow(0)

        self.window.setLayout(layout)
        self.window.show()

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
    d = DataViewer()
    app.exec_()
