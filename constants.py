DATA_NORMALIZATION_COEFFICIENT = 5

SENSOR_DATA_PREFIXES = ('aworld', 'ypr', 'areal')

SERIAL_PORT_BAUD_RATE = 115200
SERIAL_PORT_NAME = '/dev/ttys010'

SENSOR_COUNT = 5
SENSOR_ID_OFFSET = 2  # This is the i2c multiplexer id offset


class COLORS:
    RED = (1., 0., 0.)
    GREEN = (0., 1., 0.)
    BLUE = (0., 0., 1.)


DEFAULT_WINDOW_SIZE = (800, 150)

DATA_FOLDER = 'data/gestures'
