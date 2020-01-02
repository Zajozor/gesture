from pathlib import Path

from PyQt5.QtGui import QFont

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


DEFAULT_WINDOW_SIZE = (800, 150)

BASE_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = BASE_DIR / 'data/gestures'
MODELS_FOLDER = BASE_DIR / 'resources/render'
GESTURE_PREFIX = 'g'
GESTURE_NAME_SEPARATOR = '-'
GESTURE_META_SEPARATOR = ','
GESTURE_NAME_TYPE_INDEX = 1
TRASH_GESTURE_INDEX = -1

GESTURES = [
    '01 Index swipe left',
    '02 Index swipe right',
    '03 Two finger swipe left',
    '04 Two finger swipe right',
    '05 Hand swipe left',
    '06 Hand swipe right',
    '07 Pinch closer',
    '08 Pinch away',
    '09 Thumb double tap',
    '10 Grab',
    '11 Ungrab',
    '12 Push',
    '13 Raise up',
    '14 Cover down',
    '15 Peace',
    '16 Phone',
    '17 Metal',
    '18 Shoot',
    '19 Passive',
    '20 Trash',
]

ESCAPED_TO_NICE_GESTURES = {name.lower().replace(' ', '_').replace(GESTURE_NAME_SEPARATOR, '_'): name
                            for name in GESTURES}
NICE_TO_ESCAPED_GESTURES = {name: name.lower().replace(' ', '_').replace(GESTURE_NAME_SEPARATOR, '_')
                            for name in GESTURES}

EMOJI_FONT = QFont('Menlo', 24)

SIMULATOR_FREQUENCY = 28
SIMULATOR_TICK_CHANGE = 0.5
SIMULATOR_VALUES_RANGE = 10

CONSOLE_LOGGER_BUFFER_INTERVAL = 0.5
