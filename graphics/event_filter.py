from typing import Callable, List, Dict, Union

from PyQt5.QtCore import QObject, Qt, QEvent
from PyQt5.QtGui import QKeyEvent

from utils import logger

_instance: Union['GlobalEventFilter', None] = None


class GlobalEventFilter(QObject):
    @staticmethod
    def get_instance():
        global _instance
        if not _instance:
            _instance = GlobalEventFilter()
        return _instance

    def __init__(self, *args, log_events=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_events = log_events
        self.key_hooks: Dict[Qt.Key, List[Callable[[QObject, QKeyEvent], bool]]] = {}

    def install_key_hook(self, key: Qt.Key, callback: Callable[[QObject, QKeyEvent], bool]):
        logger.debug(f'Installing key hook on {key} to call {callback}')
        if key not in self.key_hooks:
            self.key_hooks[key] = []
        self.key_hooks[key].append(callback)

    def remove_key_hook(self, key: Qt.Key, callback: Callable[[QObject, QKeyEvent], bool]):
        logger.debug(f'Removing key hook on {key} to call {callback}')
        self.key_hooks[key].remove(callback)

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if type(event) == QKeyEvent:
            key_event = QKeyEvent(event)
            key = key_event.key()
            if self.log_events:
                logger.debug(f'Event: Key {key} Type {key_event.type()} Source {type(source).__name__}')
            if key in self.key_hooks:
                for hook in self.key_hooks[key]:
                    if hook(source, event):
                        return True
        return super().eventFilter(source, event)
