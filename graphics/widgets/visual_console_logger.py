from logging import StreamHandler
from typing import Union

from vispy import app
from vispy.scene import Console, SceneCanvas

import constants as cn
from input.serial_port_parser import SerialPortParser
from utils import logger


class VisualConsoleLogger(SceneCanvas):
    def __init__(self,
                 add_logger_handler=True,
                 spp_instance: Union[None, SerialPortParser] = None,
                 spp_buffer_interval=cn.CONSOLE_LOGGER_BUFFER_INTERVAL,
                 *args, **kwargs):
        """
        Creates a vispy console widget, which it shows logs from the global logger.
        If serial port parser instance is provided, shows its buffer periodically.
        """
        super().__init__(*args, **kwargs)
        self.unfreeze()
        self.console = Console()

        self.console.font_size = 8
        self.central_widget.add_widget(self.console)
        self.central_widget.bgcolor = '#ffffff'

        if spp_instance is not None:
            # Bound to self, otherwise would be GCed
            def write_log(_):
                if spp_instance.current_active_state:
                    formatted_buffer = ' | '.join(','.join(f'{x:6.3f}' for x in y) for y in spp_instance.buffer)
                    self.console.write(f'Buffer: {formatted_buffer}')

            self.console_timer = app.Timer(
                interval=spp_buffer_interval,
                connect=write_log,
                start=True
            )

        if add_logger_handler:
            logger.addHandler(VispyConsoleHandler(self.console))

    def on_mouse_wheel(self, event):
        self.console.font_size += event.delta[1]


class VispyConsoleHandler(StreamHandler):
    def __init__(self, console: Console):
        super().__init__(self)
        self.console = console

    def emit(self, record):
        self.console.write(self.format(record))

    def flush(self):
        pass
