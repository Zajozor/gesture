import logging

logger = logging.getLogger('gesture')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(levelname)7s] %(asctime)-15s %(message)s')

file_handler = logging.FileHandler('data/op.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class ApplicationState:
    def __init__(self):
        self.setup_complete = False
        self.main_window = None

    def set_up(self, main_window):
        self.setup_complete = True
        self.main_window = main_window

    def get_main_window(self):
        return self.main_window


application_state = ApplicationState()


class Gesture:
    def __init__(self, index, slug, verbose_name):
        self.index = index
        self._slug = slug
        self.verbose_name = verbose_name

    def __str__(self):
        return f'{self.index:2d} {self.verbose_name}'

    @property
    def slug(self):
        return f'{self.index:02}_{self._slug}'
