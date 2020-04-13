import os
import pickle

import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QListWidget, QLabel, \
    QBoxLayout, QTableWidget, QTableWidgetItem

import constants as cn
from graphics.widgets.extensions.vertical_scrollable import VerticalScrollableExtension
from graphics.widgets.signal_static import StaticSignalWidget


class SessionViewer(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(1100, 400)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        list_column = QVBoxLayout()
        main_layout.addLayout(list_column, stretch=1)

        refresh_button = QPushButton('🔄 Refresh')
        refresh_button.setFont(cn.EMOJI_FONT)
        refresh_button.clicked.connect(self.refresh_list)
        list_column.addWidget(refresh_button)

        self.session_list = QListWidget()
        self.session_list.currentItemChanged.connect(self.show_session)
        list_column.addWidget(self.session_list)
        self.refresh_list()

        self.info_column = QVBoxLayout()
        main_layout.addLayout(self.info_column, stretch=1)

        self.info_column.addWidget(QLabel('Selected session info:'))

        self.session_info_table = QTableWidget()
        self.session_info_table.setColumnCount(2)
        self.session_info_table.horizontalHeader().setStretchLastSection(True)
        self.info_column.addWidget(self.session_info_table)

        self.info_column.addWidget(QLabel('Contained gestures:'))
        self.gesture_list = QListWidget()
        self.gesture_list.currentItemChanged.connect(self.show_gesture)
        self.info_column.addWidget(self.gesture_list)

        self.data_column = QVBoxLayout()
        self.data_column.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(
            VerticalScrollableExtension(self.data_column, direction=QBoxLayout.TopToBottom, scrolled_spacing=10),
            stretch=3)

        self.current_session_data = None
        self.current_gesture_names = None

    @staticmethod
    def load_session_data(session_name):
        file = f'data/gestures/{session_name}'
        with open(file, 'rb') as f:
            data = pickle.load(f)
            gesture_keys = [item for item in data if type(data[item]) == np.ndarray]
        return data, gesture_keys

    @staticmethod
    def load_session_list():
        return sorted(
            filter(
                lambda x: x.startswith('s-') and x.count(cn.FILE_NAME_SEPARATOR) == 2,
                os.listdir(cn.DATA_FOLDER)
            )
        )

    def refresh_list(self):
        self.session_list.clear()
        self.session_list.addItems(SessionViewer.load_session_list())

    def cleanup_shown_session(self):
        self.session_info_table.clear()

    def cleanup_shown_gestures(self):
        for i in range(self.data_column.count()):
            self.data_column.itemAt(i).widget().close()

    def show_session(self, current_item):
        if not current_item:
            return
        self.cleanup_shown_session()
        session_name = current_item.text()
        self.current_session_data, self.current_gesture_names = SessionViewer.load_session_data(session_name)

        self.session_info_table.setRowCount(2 + len(self.current_session_data) - len(self.current_gesture_names))
        row = 0
        for info in self.current_session_data:
            if info in self.current_gesture_names:
                continue
            self.session_info_table.setItem(row, 0, QTableWidgetItem(info))
            self.session_info_table.setItem(row, 1, QTableWidgetItem(str(self.current_session_data[info])))
            row += 1
        self.session_info_table.setItem(row, 0, QTableWidgetItem('Gestures'))
        self.session_info_table.setItem(row, 1, QTableWidgetItem(str(len(self.current_gesture_names))))
        self.session_info_table.setItem(row + 1, 0, QTableWidgetItem('Instances'))
        self.session_info_table.setItem(row + 1, 1, QTableWidgetItem(str(
            sum(map(
                lambda name: len(self.current_session_data[name]),
                self.current_gesture_names
            ))
        )))

        self.gesture_list.clear()
        self.gesture_list.addItems(
            map(
                lambda name: f'{name} ({len(self.current_session_data[name])} inst.)',
                self.current_gesture_names
            )
        )

    def show_gesture(self):
        current_gesture_data = self.current_session_data[
            self.current_gesture_names[self.gesture_list.currentIndex().row()]
        ]
        self.cleanup_shown_gestures()

        def add_widgets():
            for instance in current_gesture_data:
                signal_widget = StaticSignalWidget()
                self.data_column.addWidget(signal_widget)
                signal_widget.plot_data(instance)

        QTimer.singleShot(0, add_widgets)


if __name__ == '__main__':
    # print(SessionViewer.load_session_list())
    # print(SessionViewer.load_session_data(SessionViewer.load_session_list()[0]))
    app = QApplication([])
    main_widget = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    main_widget.setLayout(layout)

    layout.addWidget(SessionViewer())
    layout.addWidget(SessionViewer())

    main_widget.show()

    app.exec_()
