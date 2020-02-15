
class CellContent:
    def __init__(self, input_id, row=0, col=0, count=3):
        self.input_sensor_id = input_id
        self.row = row
        self.col = col
        self.count = count
        self.signal_ids = None
