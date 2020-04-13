import time

import constants as cn


class SessionStorage:
    def __init__(self):
        self.data = {'user': '', 'meta': '', 'datetime': time.strftime(cn.FILE_NAME_DATETIME_FORMAT)}

    def __str__(self):
        return str(self.data)
