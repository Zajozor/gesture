from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QLabel


class NamedExtension(QWidget):
    def __init__(self, title: str, child_widget: QWidget, stretch=4, *args, **kwargs):
        super().__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label, stretch=1)
        main_layout.addWidget(child_widget, stretch=stretch)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)


if __name__ == '__main__':
    app = QApplication([])
    main_widget = NamedExtension('my label below', QLabel('Hai'))
    main_widget.show()
    app.exec_()
