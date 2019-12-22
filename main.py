from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget

from graphics.widgets.data_viewer import DataViewer
from graphics.widgets.serial_port_controller import SerialPortController
from input.data_router import DataRouter
from input.serial_port_parser import SerialPortParser
from processing.consumers.recording_consumer import RecordingConsumer
from processing.consumers.signal_grid_consumer import SignalGridCanvasConsumer, CellContentTriple

# TODO log handler logging to file for historical purposes. also add debug log messages to various places
# TODO show raw serial output?

if __name__ == '__main__':
    q_app = QApplication([])

    win = QTabWidget()
    win.setMinimumSize(1600, 850)
    layout = QVBoxLayout()
    main_tab = QWidget()
    main_tab.setLayout(layout)
    win.addTab(main_tab, 'Recording')

    canvas_consumer = SignalGridCanvasConsumer(cell_contents=(
        CellContentTriple(0, 0, 0), CellContentTriple(0, 1, 1), CellContentTriple(0, 2, 2),
        CellContentTriple(0, 3, 3), CellContentTriple(0, 4, 4),
    ), rows=1, cols=5, length=100)
    layout.addWidget(canvas_consumer.native)

    recording_consumer = RecordingConsumer()
    layout.addWidget(recording_consumer)

    spp = SerialPortParser('/dev/cu.SLAB_USBtoUART')

    spc = SerialPortController(spp)
    win.addTab(spc, 'Serial port control')

    dv = DataViewer()
    win.addTab(dv, 'Data viewer')

    dr = DataRouter(serial_port_parser_instance=spp, enable_count_logs=True)
    dr.start(threaded=True)
    dr.add_consumer(canvas_consumer)
    dr.add_consumer(recording_consumer)
    win.show()
    q_app.exec()
