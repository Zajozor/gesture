from typing import Union

from PyQt5.QtWidgets import QWidget

from graphics.widgets.session.item_base import BaseItem


class StateItem(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = self.item_spec.copy()
        data.pop('type')
        self.storage.data.update(data)

    def get_widget(self) -> Union[QWidget, None]:
        return None

    def finish(self):
        pass
