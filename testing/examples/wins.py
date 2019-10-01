# from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
#
# if __name__ == '__main__':
#     app = QApplication([])
#     window = QWidget()
#     layout = QVBoxLayout()
#     layout.addWidget(QPushButton('Top'))
#     layout.addWidget(QPushButton('Bottom'))
#     window.setLayout(layout)
#     window.show()
#     app.exec_()
#

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QApplication


class Example(QWidget):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):
        self.text = u'\u041b\u0435\u0432 \u041d\u0438\u043a\u043e\u043b\u0430\
\u0435\u0432\u0438\u0447 \u0422\u043e\u043b\u0441\u0442\u043e\u0439: \n\
\u0410\u043d\u043d\u0430 \u041a\u0430\u0440\u0435\u043d\u0438\u043d\u0430'

        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Draw text')
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)


app = QApplication([])


def main():
    global app
    e = Example()
    e.show()
    app.exec()


if __name__ == '__main__':
    main()
