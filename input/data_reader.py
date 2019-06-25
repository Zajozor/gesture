from threading import Thread
from time import sleep
import numpy as np

from constants import DATA_NORMALIZATION_COEFFICIENT


class DataReader:
    def __init__(self, input_parser_instance):
        self.input_parser_instance = input_parser_instance

        self.current_data = np.zeros((3, 1000)).astype(np.float32)
        self.running = False
        self.run_thread = None

    def start(self, threaded):
        self.running = True
        if threaded:
            self.run_thread = Thread(target=self.copy_cycle, daemon=True)
            self.run_thread.start()
        else:
            self.copy_cycle()

    def copy_cycle(self):
        while self.running:
            data = self.input_parser_instance.get_data()
            if data is not None:
                self.current_data = np.roll(self.current_data, -1, 1)
                try:
                    self.current_data[0][-1] = data[0] / DATA_NORMALIZATION_COEFFICIENT
                    self.current_data[1][-1] = data[1] / DATA_NORMALIZATION_COEFFICIENT
                    self.current_data[2][-1] = data[2] / DATA_NORMALIZATION_COEFFICIENT
                    # for q in queues:
                    #     q.put(data)  # We pass non-normalized data to the queues
                except Exception as e:  # TODO exception too broad on purpose for now
                    print(f'format error {data}, {e}')
            sleep(.005)
