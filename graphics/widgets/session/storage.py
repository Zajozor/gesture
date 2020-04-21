import time

import numpy as np

import constants as cn
from utils import logger


class SessionStorage:
    def __init__(self):
        self.data = {'user': '', 'meta': '', 'datetime': time.strftime(cn.FILE_NAME_DATETIME_FORMAT)}

    def __str__(self):
        return str(self.data)

    def store_signal_data(self, name, instances: np.ndarray):
        if name in self.data and type(self.data[name]) != np.ndarray:
            logger.error(f'Incompatible key already present in storage: `{name}`!')
            raise ValueError(f'Key {name} is incompatible and already present in session storage.')
        self.data.setdefault(name, np.array([]))

        if instances.size:
            try:
                self.data[name] = np.concatenate((
                    self.data[name],
                    instances
                ))
            except ValueError as e:
                logger.error(f'Failed to save to storage: {e}')
