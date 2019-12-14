from vispy import app

from input.data_router import DataRouter
from input.serial_port_parser import SerialPortParser
from processing.consumers.recording_consumer import RecordingConsumer
from processing.consumers.signal_grid_consumer import SignalGridCanvasConsumer, CellContentTriple

if __name__ == '__main__':
    canvas_consumer = SignalGridCanvasConsumer(cell_contents=(
        CellContentTriple(0, 0, 0), CellContentTriple(0, 1, 1), CellContentTriple(0, 2, 2),
        CellContentTriple(0, 3, 3), CellContentTriple(0, 4, 4),
    ), rows=1, cols=5, length=100, show=True)

    recording_consumer = RecordingConsumer()

    spp = SerialPortParser('/dev/cu.SLAB_USBtoUART')
    # spp = SerialPortParser('/dev/ttys002')
    spp.start(threaded=True)

    dr = DataRouter(serial_port_parser_instance=spp, enable_count_logs=True)
    dr.start(threaded=True)
    dr.add_consumer(canvas_consumer)
    dr.add_consumer(recording_consumer)
    app.run()
