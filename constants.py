from pathlib import Path

from PyQt5.QtGui import QFont

from processing.consumers.cell import CellContent
from utils import Gesture

DATA_NORMALIZATION_COEFFICIENT = 5

SENSOR_DATA_PREFIXES = ('aworld', 'ypr', 'areal')

SERIAL_PORT_BAUD_RATE = 115200
SERIAL_PORT_DEFAULT_NAME = '/dev/cu.SLAB_USBtoUART'

SENSOR_COUNT = 5
SENSOR_ID_OFFSET = 2  # This is the i2c multiplexer id offset
SENSOR_UPDATE_LOG_FREQUENCY = 1  # Seconds


class COLORS:
    RED = (1., 0., 0.)
    GREEN = (0., 1., 0.)
    BLUE = (0., 0., 1.)

    DEFAULT_SIGNAL_COLORS = [RED, GREEN, BLUE]
    PEN_COLORS = ['r', 'g', 'b']


DEFAULT_WINDOW_SIZE = (800, 150)
GIF_RECORDING_SIZE = (960, 540)
GIF_DISPLAY_SIZE = 0.5

BASE_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = BASE_DIR / 'data' / 'gestures'
MODELS_FOLDER = BASE_DIR / 'resources' / 'render'
SESSIONS_FOLDER = BASE_DIR / 'resources' / 'sessions'
GESTURE_PREFIX = 'g'
SESSION_PREFIX = 's'
FILE_NAME_SEPARATOR = '-'
GESTURE_META_SEPARATOR = ','
FILE_NAME_DATETIME_FORMAT = '%Y%m%d-%H%M%S'
GESTURE_NAME_TYPE_INDEX = 1
TRASH_GESTURE_INDEX = -1

GESTURES = [
    Gesture(0, 'trash', 'Trash (mistake)'),
    Gesture(1, 'index_swipe_left', 'Index swipe left'),
    Gesture(2, 'index_swipe_right', 'Index swipe right'),
    Gesture(3, 'two_finger_swipe_left', 'Two finger swipe left'),
    Gesture(4, 'two_finger_swipe_right', 'Two finger swipe right'),
    Gesture(5, 'hand_swipe_left', 'Hand swipe left'),
    Gesture(6, 'hand_swipe_right', 'Hand swipe right'),
    Gesture(7, 'pinch_closer', 'Pinch closer'),
    Gesture(8, 'pinch_away', 'Pinch away'),
    Gesture(9, 'thumb_double_tap', 'Thumb double tap'),
    Gesture(10, 'grab', 'Grab'),
    Gesture(11, 'ungrab', 'Ungrab'),
    Gesture(12, 'push', 'Push'),
    Gesture(13, 'raise_up', 'Raise up'),
    Gesture(14, 'page_flip', 'Page flip'),
    Gesture(15, 'peace', 'Peace'),
    Gesture(16, 'phone', 'Phone'),
    Gesture(17, 'metal', 'Metal'),
    Gesture(18, 'shoot', 'Shoot'),
    Gesture(19, 'passive', 'Passive'),
]

EMOJI_FONT = QFont('Menlo', 24)

SIMULATOR_FREQUENCY = 28
SIMULATOR_TICK_CHANGE = 0.5
SIMULATOR_VALUES_RANGE = 10

RECORDING_POLL_FREQUENCY = 60
RECORDING_MAX_LENGTH = 1000

CONSOLE_LOGGER_BUFFER_INTERVAL = 3

DEFAULT_CELL_CONTENTS = tuple(CellContent(input_id=i, col=i) for i in range(SENSOR_COUNT))
