import numpy as np
from vispy import app, gloo
from threading import Thread
from time import sleep
from vispy_flavor.input_parser import InputParser
from vispy_flavor.int_2d_gesture_display import entry_2d_gesture_display
from vispy_flavor.int_fourier_display import entry_fourier_display
from vispy_flavor.int_multi_fourier.wrapper import entry_multi_fourier_display
from multiprocessing import Process
import multiprocessing


class Canvas(app.Canvas):
    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        gloo.set_clear_color((1, 1, 1, 1))
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

    def on_draw(self, event):
        gloo.clear(color=True)
        for p in programs:
            p.draw('line_strip')

    def on_timer(self, event):
        update_program_data()
        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.size)


if __name__ == '__main__':
    app.use_app('PyQt5')

    vertex = """
    attribute vec2 positions;
    attribute vec3 colors;
    
    varying vec4 vColor;
    
    void main ()
    {
        gl_Position = vec4(positions, 0.0, 1);
        vColor = vec4(colors, 1.);
    }
    """

    fragment = """
    varying vec4 vColor;
    void main()
    {
        gl_FragColor = vColor;
    }
    """

    programs = [gloo.Program(vertex, fragment) for i in range(3)]  # Programs for three coordinates
    current_data = np.zeros((3, 1000)).astype(np.float32)
    current_colors = np.array([[[1, 0, 0]]*1000, [[0, 1, 0]]*1000, [[0, 0, 1]]*1000]).astype(np.float32)
    mapping = np.linspace(-0.95, 0.95, 1000)

    def update_program_data():
        for i in range(len(programs)):
            programs[i]['positions'] = np.c_[
                mapping,
                current_data[i]].astype(np.float32)
            programs[i]['colors'] = current_colors[i]

    update_program_data()

    # Options:
    #   entry_2d_gesture_display,
    #   entry_fourier_display,
    #   entry_multi_fourier_display
    targets = [entry_multi_fourier_display, ]
    queues = []

    # We start a separate process for each interpreter, creating a queue for each
    for target in targets:
        queues.append(multiprocessing.Queue())  # TODO can be a Pipe which is faster
        p = Process(target=target, args=(queues[-1], ))
        p.daemon = True
        p.start()

    input_parser = InputParser()

    def data_reader():
        global current_data  # TODO pass as parameter without using global keyword
        while True:
            data = input_parser.get_next()
            if data is not None:
                current_data = np.roll(current_data, -1, 1)
                c = 10000.0
                try:
                    current_data[0][-1] = data[0]/c
                    current_data[1][-1] = data[1]/c
                    current_data[2][-1] = data[2]/c
                    for q in queues:
                        q.put(data)  # We pass non-normalized data to the queues
                except:  # TODO exception too broad on purpose for now
                    print('format error {}'.format(data))
            sleep(.005)

    th = Thread(target=input_parser.init_serial, daemon=True)
    th.start()

    th2 = Thread(target=data_reader, daemon=True)
    th2.start()

    canvas = Canvas(keys='interactive', always_on_top=False, position=(850, 100))
    canvas.show()
    app.run()

    input_parser.stop_serial()

