from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication, QLabel

import constants as cn


class ClosableExtension(QWidget):
    def __init__(self, child_widget: QWidget, stretch=4, *args, **kwargs):
        super().__init__(*args, **kwargs)
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        close_button = QPushButton('❌')
        close_button.setFont(cn.EMOJI_FONT)
        close_button.setFixedSize(50, 50)

        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button, stretch=1)
        main_layout.addWidget(child_widget, stretch=stretch)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)


if __name__ == '__main__':
    app = QApplication([])
    main_widget = ClosableExtension(QLabel('Hai'))
    main_widget.show()
    app.exec_()
