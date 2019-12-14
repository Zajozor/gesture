from abc import ABC
from typing import List

import numpy as np


class ConsumerMixin(ABC):
    def receive_data(self, data: np.ndarray, data_changed: List[bool]):
        """
        This method should be swift, eg. only save the stuff, as it is called
        synchronously in a DataRouter. The core processing done by the consumer
        should happen at least in a different thread.

        :param data: numpy array of size (cn.SENSOR_COUNT, 3) containing floats
        :param data_changed: list of booleans containing which data is actually new
        """
        raise NotImplementedError
