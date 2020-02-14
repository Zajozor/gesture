from PyQt5.QtWidgets import QApplication

from graphics.event_filter import GlobalEventFilter
from graphics.widgets.main_window import MainWindow
from utils import logger

if __name__ == '__main__':
    logger.debug('Starting up application')
    q_app = QApplication([])

    win = MainWindow.get_instance()
    win.show()

    q_app.installEventFilter(GlobalEventFilter.get_instance())
    q_app.exec()
