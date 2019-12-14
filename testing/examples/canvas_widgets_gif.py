import sys

import numpy as np
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from vispy import app, gloo

from graphics.widgets.signal_grid_canvas import SignalGridCanvas

if __name__ == '__main__':
    # Running the code below shows examples of using the SignalCanvas, we spawn two canvases and show them
    # in a single Qt window.

    qt_app = QApplication(sys.argv)
    main_window = QMainWindow()
    base_widget = QWidget()
    main_window.setCentralWidget(base_widget)

    base_widget.setLayout(QVBoxLayout())

    # Now we construct the canvases

    canvas_1 = SignalGridCanvas(3, 3, length=1000)

    o1 = canvas_1.add_new_signal(2, 2)
    o2 = canvas_1.add_new_signal(1, 1)
    o3 = canvas_1.add_new_signal(1, 1)

    o4 = canvas_1.add_new_signals(2, 0)
    canvas_1.set_signal_single_color(o4[0], (1., 0., 0.))
    canvas_1.set_signal_single_color(o4[1], (0., 1., 0.))
    canvas_1.set_signal_single_color(o4[2], (0., 0., 1.))

    o5 = canvas_1.add_new_signals(0, 2)
    canvas_1.set_signal_single_color(o5[0], (1., 0., 0.5))
    canvas_1.set_signal_single_color(o5[1], (0.5, 1., 0.))
    canvas_1.set_signal_single_color(o5[2], (0., 0.5, 1.))

    canvas_1.set_signal_single_color(o3, (1., 0., 0.))


    def update(_):
        canvas_1.set_signal_values(o1, np.random.rand(1000))
        canvas_1.set_signal_values(o2, np.concatenate([np.random.rand(500), np.repeat(1, 500)]))
        canvas_1.set_signal_values(o3, np.concatenate([np.random.rand(500), np.repeat(1, 500)]))


    timer = app.Timer()
    timer.connect(update)
    timer.start()

    canvas_2 = SignalGridCanvas(3, 3, length=1000)
    c2_0 = canvas_2.add_new_signal(1, 1)
    canvas_2.set_signal_values(c2_0, np.concatenate([np.random.rand(500), np.repeat(1, 500)]))

    base_widget.layout().addWidget(canvas_1.native)
    base_widget.layout().addWidget(canvas_2.native)
    from vispy.scene.widgets.console import Console
    from vispy.scene import SceneCanvas

    sc = SceneCanvas(keys='interactive')
    horiz = QHBoxLayout()
    base_widget.layout().addLayout(horiz)
    horiz.addWidget(sc.native)

    c = Console()
    sc.central_widget.add_widget(c)
    sc.central_widget.bgcolor = '#ffffff'
    import random


    def write(_):
        c.write(f'hai {random.randint(0, 10)}')
        c3.visuals[1].set_data(np.random.rand(4, 2) * 100)
        c3.update()


    t = app.Timer(interval=0.5, connect=write, start=True)
    from vispy import visuals


    class TextCanvas(app.Canvas):
        def __init__(self):
            app.Canvas.__init__(self, title='Bezier lines example',
                                keys='interactive', size=(400, 750))
            self.visuals = [
                visuals.TextVisual('Third order curve', bold=True, color='w',
                                   font_size=14, pos=(200, 75)),
                visuals.LineVisual(np.array([[10, 10], [30, 10], [40, 40], [90, 40]]),
                                   color=(1, 0, 0, 1))
            ]
            # self.visuals[0].transform = NullTransform()
            # self.visuals[1].transform = STTransform(translate=[20, 20])

        def on_draw(self, event):
            gloo.clear('black')
            gloo.set_viewport(0, 0, *self.physical_size)
            for visual in self.visuals:
                visual.draw()

        def on_resize(self, event):
            vp = (0, 0, self.physical_size[0], self.physical_size[1])
            self.context.set_viewport(*vp)
            for visual in self.visuals:
                visual.transforms.configure(canvas=self, viewport=vp)


    c3 = TextCanvas()
    horiz.addWidget(c3.native)

    mv = QMovie('../../models/render/15.peace.gif')
    label = QLabel()
    label.setMovie(mv)
    label.setScaledContents(True)
    label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
    # mv.loopCount()
    mv.start()

    horiz.addWidget(label)

    main_window.show()
    app.run()
