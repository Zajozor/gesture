from vispy import app, gloo


class SimpleCanvas(app.Canvas):
    def __init__(self, draw_callback=None, update_callback=None, *args, **kwargs):
        self.draw_callback = draw_callback if draw_callback else lambda: None
        self.update_callback = update_callback if update_callback else lambda: None

        app.Canvas.__init__(self, *args, **kwargs)
        gloo.set_clear_color((1, 1, 1, 1))
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

    def on_draw(self, event):
        gloo.clear(color=True)
        self.draw_callback()

    def on_timer(self, event):
        self.update_callback()
        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.size)
