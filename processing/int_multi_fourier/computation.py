import numpy as np
from time import sleep


class PredictionState:
    """ Simple prediction state encapsulating data store with prediction values """
    def __init__(self, current_gesture, data_store):
        self.current_gesture = current_gesture
        self.data_store = data_store
        self.predictions = np.zeros((len(self.data_store.gesture_sets),
                                     self.current_gesture.gesture_size)).astype(np.float32)
        # TODO prediction colors


class MultiFourierComputation:
    def __init__(self, prediction_state):
        self.prediction_state = prediction_state
        self.recording = False

    """
        Starts periodic predicting from queue ( paused on recording )
        Should be ran in separate thread
    """
    def predict_from_queue(self, queue):
        while True:
            if not self.recording:
                try:
                    while True:
                        a = queue.get(block=False)
                        self.prediction_state.current_gesture.push_data(a)
                except:
                    # Exception happens on queue being empty
                    #   without valid naming, maybe format error on data
                    pass
                self.prediction_state.current_gesture.update_computed()

                self.prediction_state.predictions = np.roll(self.prediction_state.predictions, -1, 1)
                for i in range(len(self.prediction_state.data_store.gesture_sets)):
                    self.prediction_state.predictions[i][-1] =\
                        self.prediction_state.data_store.gesture_sets[i].get_distance(
                            self.prediction_state.current_gesture)

            sleep(.05)

    def record_to_gesture(self, queue, target_gesture):
        self.recording = True

        recording_phase = 0

        while recording_phase < target_gesture.gesture_size:
            a = queue.get()  # should be three floats
            try:
                target_gesture.push_data(a)
            except:
                print('format error on fourier')

            recording_phase += 1
            sleep(.005)

        target_gesture.update_computed()

        self.recording = False

