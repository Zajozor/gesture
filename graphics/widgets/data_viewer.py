import os

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QTreeView, \
    QAbstractItemView, QMenu

import constants as cn
from graphics.widgets.extensions.blink import BlinkExtension
from graphics.widgets.extensions.closable import ClosableExtension
from graphics.widgets.extensions.named import NamedExtension
from graphics.widgets.extensions.vertical_scrollable import VerticalScrollableExtension
from graphics.widgets.renamer import Renamer
from graphics.widgets.signal_static import StaticSignalWidget
from utils import logger


class DataViewer(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(500, 400)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        control_column = QVBoxLayout()
        main_layout.addLayout(control_column, stretch=1)

        refresh_button = QPushButton('🔄 Refresh')
        refresh_button.setFont(cn.EMOJI_FONT)
        refresh_button.clicked.connect(self.refresh_list)
        control_column.addWidget(refresh_button)

        self.gesture_tree_view = QTreeView()
        self.gesture_tree_view.setMinimumWidth(250)
        self.gesture_tree_view.header().hide()
        self.gesture_tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.gesture_tree_view.clicked.connect(self.show_selected)
        self.gesture_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.gesture_tree_view.customContextMenuRequested.connect(self.gesture_context_menu)

        self.gesture_model = QStandardItemModel()
        self.gesture_tree_view.setModel(self.gesture_model)
        self.gesture_tree_view.setAnimated(True)
        control_column.addWidget(self.gesture_tree_view)

        self.displayed_gestures_layout = QVBoxLayout()

        display_column = QVBoxLayout()

        close_all_button = QPushButton('❌ Close all opened')
        close_all_button.setFont(cn.EMOJI_FONT)

        def close_all_displayed_gestures():
            for i in range(self.displayed_gestures_layout.count()):
                self.displayed_gestures_layout.itemAt(i).widget().close()

        close_all_button.clicked.connect(close_all_displayed_gestures)

        control_column.addWidget(close_all_button)
        display_column.addLayout(VerticalScrollableExtension(self.displayed_gestures_layout))
        main_layout.addLayout(display_column, stretch=2)

        self.refresh_list()

    def refresh_list(self):
        gestures = sorted(os.listdir(cn.DATA_FOLDER))

        gesture_tree = {}
        for gesture in gestures:
            parts = gesture.split(cn.FILE_NAME_SEPARATOR)
            if len(parts) < 3 or (parts[0] != cn.GESTURE_PREFIX and parts[0] != cn.SESSION_PREFIX):
                logger.debug(f'Skipping file {gesture}, unknown naming.')
                continue

            index = int(parts[1])
            if index < 0 or index >= len(cn.GESTURES):
                logger.debug(f'Invalid index on {gesture}, skipping.')
                continue

            gesture = cn.GESTURES[index]
            parts[1] = str(gesture)

            current_node = gesture_tree
            for part in parts[1:]:
                current_node = current_node.setdefault(part, {})

        self.gesture_model.clear()
        root = self.gesture_model.invisibleRootItem()

        def add_tree(tree: dict, node: QStandardItem):
            for item in tree:
                child_node = QStandardItem(item)
                node.appendRow(child_node)
                add_tree(tree[item], child_node)

        add_tree(gesture_tree, root)

    @staticmethod
    def get_filename(model_index):
        name = []
        node = model_index
        while node.isValid():
            name.append(node.data())
            node = node.parent()
        name.append(cn.GESTURE_PREFIX)

        # TODO this could be nicer
        for i, gesture_spec in enumerate(cn.GESTURES):
            if str(gesture_spec) == name[-2]:
                name[-2] = str(i)
        return cn.FILE_NAME_SEPARATOR.join(name[::-1])

    def show_selected(self, model_index):
        is_leaf = not model_index.child(0, 0).isValid()
        if not is_leaf:
            self.gesture_tree_view.setExpanded(model_index, not self.gesture_tree_view.isExpanded(model_index))
            return

        filename = DataViewer.get_filename(model_index)
        selected_file = cn.DATA_FOLDER / filename
        data = np.load(selected_file)

        signal_widget = StaticSignalWidget()
        signal_widget.plot_data(data)
        widget = NamedExtension(filename, signal_widget)
        widget = BlinkExtension(widget)
        widget = ClosableExtension(widget)
        widget.setMinimumWidth(600)
        widget.setFixedHeight(200)

        self.displayed_gestures_layout.addWidget(widget)

    def gesture_context_menu(self, point):
        model_index = self.gesture_tree_view.indexAt(point)
        is_leaf = not model_index.child(0, 0).isValid()
        if not is_leaf:
            self.gesture_tree_view.setExpanded(model_index, not self.gesture_tree_view.isExpanded(model_index))
            return

        menu = QMenu()

        def move_dialog():
            Renamer(DataViewer.get_filename(model_index)).exec()

        menu.addAction('Move', move_dialog)

        def trash_and_remove_from_tree():
            if Renamer.trash_gesture(DataViewer.get_filename(model_index)):
                self.gesture_model.removeRow(model_index.row(), model_index.parent())

        menu.addAction('Trash', trash_and_remove_from_tree)
        menu.exec(QCursor.pos())


if __name__ == '__main__':
    app = QApplication([])
    main_widget = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    main_widget.setLayout(layout)

    layout.addWidget(DataViewer())
    layout.addWidget(DataViewer())

    main_widget.show()

    app.exec_()
