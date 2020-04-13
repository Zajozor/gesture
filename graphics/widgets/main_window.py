import warnings

from graphics.widgets.recording_controller import RecordingController
from graphics.widgets.session_controller import SessionController
from graphics.widgets.session_viewer import SessionViewer
from utils import application_state

warnings.simplefilter(action='ignore', category=FutureWarning)
# We use this to suppress a group of warnings that are a result of outdated libraries
# available on conda channels.

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget  # noqa: E402

import constants as cn  # noqa: E402
from graphics.widgets.data_viewer import DataViewer  # noqa: E402
from graphics.widgets.serial_port_controller import SerialPortController  # noqa: E402
from input.data_router import DataRouter  # noqa: E402
from input.serial_port_parser import SerialPortParser  # noqa: E402

from processing.consumers.dynamic_signal_widget import DynamicSignalWidgetConsumer  # noqa: E402


class MainWindow(QTabWidget):
    @staticmethod
    def get_instance():
        if not application_state.setup_complete:
            application_state.set_up(MainWindow())
        return application_state.main_window

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial_port_parser = SerialPortParser(cn.SERIAL_PORT_DEFAULT_NAME)
        self.data_router = DataRouter(serial_port_parser_instance=self.serial_port_parser, enable_count_logs=True)

        self.init_ui()
        self.data_router.start(threaded=True)

    def init_ui(self):
        self.setMinimumSize(1200, 750)

        spc = SerialPortController(self.serial_port_parser)
        self.addTab(spc, 'Serial port control')

        # Recording Tab
        layout = QVBoxLayout()
        canvas_consumer = DynamicSignalWidgetConsumer()
        self.data_router.add_consumer(canvas_consumer)
        layout.addWidget(canvas_consumer.native)
        recording_controller = RecordingController()
        self.data_router.add_consumer(recording_controller.consumer)
        layout.addWidget(recording_controller)

        recording_tab = QWidget()
        recording_tab.setLayout(layout)
        self.addTab(recording_tab, 'Recording')

        session_controller = SessionController()
        self.addTab(session_controller, 'Session')

        dv = DataViewer()
        self.addTab(dv, 'Data viewer')

        sv = SessionViewer()
        self.addTab(sv, 'Session viewer')

    def set_tab_switching_enabled(self, state: bool):
        for i in range(self.count()):
            if i == self.currentIndex():
                continue
            self.setTabEnabled(i, state)
