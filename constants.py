from pathlib import Path

import numpy as np
from PyQt5.QtGui import QFont

from processing.consumers.cell import CellContent
from utils import Gesture

# The input from the sensor is a 2 byte signed integer, which then normalized to a float between -1 and 1
DATA_NORMALIZATION_COEFFICIENT = 32768

SERIAL_PORT_BAUD_RATE = 460800
SERIAL_PORT_DEFAULT_NAME = '/dev/cu.SLAB_USBtoUART'

SIMULATED_SERIAL_PORT_BAUD_RATE = 115200
SIMULATED_SERIAL_PORT_PREFIX = '/dev/ttys'

SENSOR_COUNT = 5
SENSOR_ID_OFFSET = 2  # This is the i2c multiplexer id offset
SENSOR_READING_DELIMITER = b'\xff\x00\xff\x2a'
SENSOR_CORRECT_READING_LENGTH = 60
SENSOR_CHANNEL_COUNT = 6
SENSOR_DATA_DTYPE = np.dtype(np.int16).newbyteorder('>')

# When drawing the values from the sensor inside the application, to enhance readability, we draw the
# accelerometer data on top 65% of the image, and the gyroscope data below.
# drawn_data = data * coefficient + offset
SENSOR_DRAW_COEFFICIENT = np.array([0.65, 0.65, 0.65, 0.35, 0.35, 0.35])
SENSOR_DRAW_OFFSET = np.array([0.35, 0.35, 0.35, -0.65, -0.65, -0.65])

SENSOR_UPDATE_LOG_FREQUENCY = 1  # Seconds


class COLORS:
    RED = (1., 0., 0.)
    GREEN = (0., 1., 0.)
    BLUE = (0., 0., 1.)
    PURPLE = (0.2, 0., 0.6)
    MAGENTA = (1., 0., 1.)
    CYAN = (0, 1., 1.)

    # Dynamic canvas
    DEFAULT_SIGNAL_COLORS = [RED, GREEN, BLUE, CYAN, MAGENTA, PURPLE]
    # Static canvas
    PEN_COLORS = ['r', 'g', 'b', 'c', 'm', PURPLE]


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
TRASH_GESTURE_INDEX = 0
NULL_CLASS_INDEX = 28

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
    Gesture(20, 'diag', ''),
    Gesture(21, 'square', ''),
    Gesture(22, 'right', ''),
    Gesture(23, 'left', ''),
    Gesture(24, 'up', ''),
    Gesture(25, 'down', ''),
    Gesture(26, 'cwise', ''),
    Gesture(27, 'ccwise', ''),
    Gesture(28, 'null', ''),
]

EMOJI_FONT = QFont('Menlo', 24)

SIMULATOR_FREQUENCY = 28
SIMULATOR_TICK_CHANGE = 1000

RECORDING_POLL_FREQUENCY = 60
RECORDING_MAX_LENGTH = 1000

CONSOLE_LOGGER_BUFFER_INTERVAL = 3

DEFAULT_CELL_CONTENTS = tuple(
    CellContent(input_id=i, col=i, row=0, count=SENSOR_CHANNEL_COUNT) for i in range(SENSOR_COUNT)
)
