import os

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QTreeView, \
    QAbstractItemView, QMenu

import constants as cn
from graphics.widgets.extensions.closable import ClosableExtension
from graphics.widgets.extensions.named import NamedExtension
from graphics.widgets.renamer import Renamer
from graphics.widgets.signal_grid_canvas import SignalGridCanvas
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

        refresh_button = QPushButton('Refresh')
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

        self.display_column = QVBoxLayout()
        main_layout.addLayout(self.display_column, stretch=2)

        self.refresh_list()

    def refresh_list(self):
        gestures = sorted(os.listdir(cn.DATA_FOLDER))

        gesture_tree = {}
        for gesture in gestures:
            parts = gesture.split(cn.GESTURE_NAME_SEPARATOR)
            if len(parts) < 3 or parts[0] != cn.GESTURE_PREFIX:
                logger.debug(f'Leaving out file {gesture}, unknown naming.')
                continue

            if parts[1] in cn.ESCAPED_TO_NICE_GESTURES:
                parts[1] = cn.ESCAPED_TO_NICE_GESTURES[parts[1]]

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

        if name[-2] in cn.NICE_TO_ESCAPED_GESTURES:
            name[-2] = cn.NICE_TO_ESCAPED_GESTURES[name[-2]]

        return cn.GESTURE_NAME_SEPARATOR.join(name[::-1])

    def show_selected(self, model_index):
        is_leaf = not model_index.child(0, 0).isValid()
        if not is_leaf:
            self.gesture_tree_view.setExpanded(model_index, not self.gesture_tree_view.isExpanded(model_index))
            return

        filename = DataViewer.get_filename(model_index)
        selected_file = cn.DATA_FOLDER / filename
        data = np.load(selected_file)
        self.display_column.addWidget(
            ClosableExtension(
                NamedExtension(filename,
                               SignalGridCanvas.from_data(data, title=filename).native
        )))

    def gesture_context_menu(self, point):
        model_index = self.gesture_tree_view.indexAt(point)
        is_leaf = not model_index.child(0, 0).isValid()
        if not is_leaf:
            self.gesture_tree_view.setExpanded(model_index, not self.gesture_tree_view.isExpanded(model_index))
            return

        menu = QMenu()

        menu.addAction('Move', lambda: Renamer(DataViewer.get_filename(model_index)).exec())

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
