from typing import List, Tuple

import numpy as np

import constants as cn
from graphics.widgets.signal_grid_canvas import SignalGridCanvas
from processing.consumers.cell import CellContent
from processing.consumers.consumer_mixin import ConsumerMixin


class SignalGridCanvasConsumer(SignalGridCanvas, ConsumerMixin):
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
            cell.signal_ids = self.add_new_signals(cell.row, cell.col, cell.count)
            for i in range(3):
                self.set_signal_single_color(cell.signal_ids[i], cn.COLORS.DEFAULT_SIGNAL_COLORS[i])

    def receive_data(self, data: np.ndarray, data_changed: List[bool]):
        for cell in self.cell_contents:
            if data_changed[cell.input_sensor_id]:
                self.roll_signal_values_multi(
                    zip(cell.signal_ids, np.reshape(data[cell.input_sensor_id], (3, 1)))
                )
