from PyQt5 import QtGui
from PyQt5.QtCore import QPropertyAnimation, pyqtProperty, QEasingCurve
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication, QLabel


class BlinkExtension(QWidget):
    def __init__(self,
                 child_widget: QWidget,
                 play_on_show=True,
                 duration_ms=1000,
                 start_color=QColor(50, 190, 25, 255),
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(child_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._animation = QPropertyAnimation(self, b'color')
        self._animation.setDuration(duration_ms)
        self._animation.setStartValue(start_color)
        self._animation.setEndValue(self.palette().color(self.backgroundRole()))
        self._animation.setEasingCurve(QEasingCurve.OutInBack)
        self.play_on_show = play_on_show
        # TODO implement cleanup after itself, eg. remove itself from the component tree
        # use self._animation.finished.connect()

    def set_color(self, color: QColor):
        self.setStyleSheet(f'background-color: rgb({color.red()},{color.green()},{color.blue()});')

    color = pyqtProperty(QColor, fset=set_color)

    def play(self):
        self._animation.start()

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        super(BlinkExtension, self).showEvent(a0)
        if self.play_on_show:
            self._animation.start()


if __name__ == '__main__':
    app = QApplication([])
    main_widget = BlinkExtension(QLabel('Hai'))
    main_widget.setFixedSize(600, 200)
    main_widget.show()
    app.exec_()
