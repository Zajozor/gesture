from typing import List, Tuple

import numpy as np

import constants as cn
from graphics.widgets.signal_dynamic import DynamicSignalWidget
from processing.consumers.cell import CellContent
from processing.consumers.consumer_mixin import ConsumerMixin


class DynamicSignalWidgetConsumer(DynamicSignalWidget, ConsumerMixin):
    def __init__(self, cell_contents: Tuple[CellContent, ...] = cn.DEFAULT_CELL_CONTENTS, *args, **kwargs):
        """
        Creates a SignalGridCanvas, which can also receive data.
        Upon calling `receive_data`, the signals displayed are rolled.
        The cell_contents specify what signals are shown:
        - their position on the grid
        - the sensor_id from which the cell receives input
        """
        super().__init__(*args, **kwargs)

        self.cell_contents = cell_contents
        for cell in self.cell_contents:
            cell.signal_ids = tuple(self.add_new_signal(cell.row, cell.col) for _ in range(cell.count))

            for i in range(cell.count):
                self.set_signal_color(cell.signal_ids[i], cn.COLORS.DEFAULT_SIGNAL_COLORS[i])

    def receive_data(self, data: np.ndarray, data_changed: List[bool]):
        for cell in self.cell_contents:
            if data_changed[cell.input_sensor_id]:
                for i, signal_id in enumerate(cell.signal_ids):
                    self.roll_signal_values(signal_id, np.array([data[cell.input_sensor_id][i]]))
