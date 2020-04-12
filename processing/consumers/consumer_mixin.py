import numpy as np


class ConsumerMixin:
    def __init__(self):
        # We do not use ABC here, because it causes metaclass conflict when used as mixin with Qt classes.
        if self.__class__ == ConsumerMixin:
            raise NotImplementedError('This is an abstract class!')

    def receive_data(self, data: np.ndarray, data_changed: bool):
        """
        This method should be swift, eg. only save the stuff, as it is called
        synchronously in a DataRouter. The core processing done by the consumer
        should happen at least in a different thread.

        :param data: numpy array of size (cn.SENSOR_COUNT, cn.SENSOR_CHANNEL_COUNT) containing floats
        :param data_changed: boolean indicating whether new reading happened
        """
        raise NotImplementedError
