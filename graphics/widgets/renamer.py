from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QLineEdit, \
    QComboBox, QApplication, QMessageBox, QDialog

import constants as cn


class Renamer(QDialog):
    def __init__(self, old_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Rename gesture')
        layout = QVBoxLayout()
        self.setLayout(layout)

        old_name_layout = QHBoxLayout()
        old_name_layout.addWidget(QLabel('Old name:'))
        old_name_layout.addWidget(QLabel(old_name))
        layout.addLayout(old_name_layout)

        new_type_layout = QHBoxLayout()

        edit_name_layout = QHBoxLayout()
        layout.addLayout(edit_name_layout)

        new_name_layout = QHBoxLayout()
        layout.addLayout(new_name_layout)

        new_name_layout.addWidget(QLabel('New name:'))
        self.new_name_label = QLabel(old_name)
        new_name_layout.addWidget(self.new_name_label)

        self.new_name_parts = [
            QLineEdit(part) for part in old_name.split(cn.GESTURE_NAME_SEPARATOR)
        ]

        new_type_layout.addWidget(QLabel('Change gesture type:'))

        new_type_combo_box = QComboBox()
        new_type_combo_box.addItems(cn.GESTURES)

        # This may cause weird behaviour if you name files maliciously, but we ignore that for now
        if len(old_name.split(cn.GESTURE_NAME_SEPARATOR)) > cn.GESTURE_NAME_TYPE_INDEX:
            layout.addLayout(new_type_layout)
            escaped_name = self.new_name_parts[cn.GESTURE_NAME_TYPE_INDEX].text()
            if escaped_name in cn.ESCAPED_TO_NICE_GESTURES:
                nice_name = cn.ESCAPED_TO_NICE_GESTURES[escaped_name]
                new_type_combo_box.setCurrentIndex(new_type_combo_box.findText(nice_name))

        new_type_combo_box.currentTextChanged.connect(self.change_gesture_type)
        new_type_layout.addWidget(new_type_combo_box)

        for i, part_line_edit in enumerate(self.new_name_parts):
            part_line_edit.textEdited.connect(self.refresh_new_name)
            edit_name_layout.addWidget(part_line_edit, stretch=([1, 5, 3, 3][i:i + 1] + [2])[0])

        confirm_button = QPushButton('Confirm')
        confirm_button.clicked.connect(self.confirm_rename)
        layout.addWidget(confirm_button)

        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.old_name = old_name

    def change_gesture_type(self, gesture_name):
        escaped_name = cn.NICE_TO_ESCAPED_GESTURES[gesture_name]
        self.new_name_parts[cn.GESTURE_NAME_TYPE_INDEX].setText(escaped_name)
        self.refresh_new_name()

    def refresh_new_name(self):
        self.new_name_label.setText(
            cn.GESTURE_NAME_SEPARATOR.join(map(lambda line_edit: line_edit.text(), self.new_name_parts))
        )

    def confirm_rename(self):
        if Renamer.rename_gesture(self.old_name, self.new_name_label.text()):
            self.close()

    @staticmethod
    def trash_gesture(old_name):
        parts = old_name.split(cn.GESTURE_NAME_SEPARATOR)
        parts[cn.GESTURE_NAME_TYPE_INDEX] = cn.NICE_TO_ESCAPED_GESTURES[cn.GESTURES[cn.TRASH_GESTURE_INDEX]]
        return Renamer.rename_gesture(old_name, cn.GESTURE_NAME_SEPARATOR.join(parts))

    @staticmethod
    def rename_gesture(old_name, new_name):
        old_path = cn.DATA_FOLDER / old_name
        new_path = cn.DATA_FOLDER / new_name
        if not old_path.exists():
            message_box = QMessageBox()
            message_box.setText('The source file not longer exists!')
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec()
            return False

        if old_path == new_path:
            return True

        if new_path.exists():
            message_box = QMessageBox()
            message_box.setText('Target file name already exists!')
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec()
            return False

        old_path.rename(new_path)
        return True


if __name__ == '__main__':
    app = QApplication([])
    main_widget = Renamer('old-hai')
    main_widget.show()
    app.exec_()
