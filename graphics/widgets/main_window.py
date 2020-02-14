import warnings
from typing import Union

from graphics.widgets.session_controller import SessionController

warnings.simplefilter(action='ignore', category=FutureWarning)
# We use this to suppress a group of warnings that are a result of outdated libraries
# available on conda channels.

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget  # noqa: E402

import constants as cn  # noqa: E402
from graphics.widgets.data_viewer import DataViewer  # noqa: E402
from graphics.widgets.serial_port_controller import SerialPortController  # noqa: E402
from input.data_router import DataRouter  # noqa: E402
from input.serial_port_parser import SerialPortParser  # noqa: E402
from processing.consumers.recording_consumer import RecordingConsumer  # noqa: E402

from processing.consumers.signal_grid_consumer import SignalGridCanvasConsumer, CellContentTriple  # noqa: E402

_instance: Union['MainWindow', None] = None


class MainWindow(QTabWidget):
    @staticmethod
    def get_instance():
        global _instance
        if not _instance:
            _instance = MainWindow()
        return _instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(1200, 650)

        # Serial port Tab
        spp = SerialPortParser(cn.SERIAL_PORT_DEFAULT_NAME)
        spc = SerialPortController(spp)
        self.addTab(spc, 'Serial port control')

        # Recording Tab
        recording_tab = QWidget()
        layout = QVBoxLayout()
        recording_tab.setLayout(layout)
        self.addTab(recording_tab, 'Recording')

        canvas_consumer = SignalGridCanvasConsumer(cell_contents=(
            CellContentTriple(0, 0, 0), CellContentTriple(0, 1, 1), CellContentTriple(0, 2, 2),
            CellContentTriple(0, 3, 3), CellContentTriple(0, 4, 4),
        ), rows=1, cols=5, length=100)
        layout.addWidget(canvas_consumer.native)

        recording_consumer = RecordingConsumer()
        layout.addWidget(recording_consumer)

        # Recording session tab
        session_controller = SessionController()
        self.addTab(session_controller, 'Session')

        # Data viewer tab
        dv = DataViewer()
        self.addTab(dv, 'Data viewer')

        dr = DataRouter(serial_port_parser_instance=spp, enable_count_logs=True)
        dr.start(threaded=True)
        dr.add_consumer(canvas_consumer)
        dr.add_consumer(recording_consumer)

    def set_tab_switching(self, state: bool):
        for i in range(self.count()):
            if i == self.currentIndex():
                continue
            self.setTabEnabled(i, state)
