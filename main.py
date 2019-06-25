from vispy import app

from graphics.status_canvas import StatusCanvas
from input.data_reader import DataReader
from input.input_parser import InputParser
from processing.int_multi_fourier.wrapper import entry_multi_fourier_display
from multiprocessing import Process
import multiprocessing


if __name__ == '__main__':
    app.use_app('PyQt5')

    # Options:
    #   entry_2d_gesture_display,
    #   entry_fourier_display,
    #   entry_multi_fourier_display
    # targets = [entry_multi_fourier_display, ]
    # queues = []

    # We start a separate process for each interpreter, creating a queue for each
    # for target in targets:
    #     queues.append(multiprocessing.Queue())  # TODO can be a Pipe which is faster
    #     p = Process(target=target, args=(queues[-1], ))
    #     p.daemon = True
    #     p.start()

    input_parser = InputParser()
    input_parser.start(threaded=True)

    data_reader = DataReader(input_parser)
    data_reader.start(threaded=True)

    status_canvas = StatusCanvas(data_reader)
    status_canvas.show()
    app.run()

    input_parser.stop_serial()
