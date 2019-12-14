from typing import List, Tuple

import numpy as np
from vispy import app

import constants as cn
from graphics.widgets.signal_grid_canvas import SignalGridCanvas
from processing.consumers.consumer_mixin import ConsumerMixin


class CellContent:
    def __init__(self, row, col, count):
        self.row = row
        self.col = col
        self.count = count


class CellContentTriple(CellContent):
    def __init__(self, row, col, input_id):
        super().__init__(row, col, 3)
        self.input_id = input_id
        self.signal_ids = None


class SignalGridCanvasConsumer(SignalGridCanvas, ConsumerMixin):
    def __init__(self, cell_contents: Tuple[CellContent, ...], *args, **kwargs):
        """

        """
        super().__init__(*args, **kwargs)

        self.cell_contents = cell_contents
        for cell in self.cell_contents:
            cell.signal_ids = self.add_new_signals(cell.row, cell.col, cell.count)
            self.set_signal_single_color(cell.signal_ids[0], cn.COLORS.RED)
            self.set_signal_single_color(cell.signal_ids[1], cn.COLORS.GREEN)
            self.set_signal_single_color(cell.signal_ids[2], cn.COLORS.BLUE)

    def receive_data(self, data: np.ndarray, data_changed: List[bool]):
        for cell in self.cell_contents:
            if isinstance(cell, CellContentTriple):
                if data_changed[cell.input_id]:
                    self.roll_signal_values_multi(
                        list(zip(cell.signal_ids, np.reshape(data[cell.input_id], (3, 1))))
                    )
            else:
                raise NotImplementedError("Other data formats than triples not supported yet")


if __name__ == '__main__':
    c = SignalGridCanvasConsumer(cell_contents=(
        CellContentTriple(0, 0, 0), CellContentTriple(0, 1, 1), CellContentTriple(0, 2, 2),
        CellContentTriple(0, 3, 3), CellContentTriple(0, 4, 4),
        CellContentTriple(1, 1, 1),

    ), rows=2, cols=5, length=100, show=True)
    app.run()
