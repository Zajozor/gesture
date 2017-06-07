import numpy as np
from scipy.spatial import distance
import pickle


class Gesture:
    def __init__(self, gesture_size=500):
        self.gesture_size = gesture_size
        self.data = np.zeros((3, self.gesture_size)).astype(np.float32)
        self.colors = np.array([[[1, 0, 0]] * self.gesture_size,
                               [[0, 1, 0]] * self.gesture_size,
                               [[0, 0, 1]] * self.gesture_size]).astype(np.float32)
        self.mapping = np.linspace(0.05, 0.95, self.gesture_size)

    """ Parameter data is an one-dimensional array of size 3 and data is already normalised """
    def push_data(self, data):
        self.data = np.roll(self.data, -1, 1)
        for i in range(3):
            self.data[i][-1] = data[i]

    """ Just a simple norm distance, not advised to be used """
    def get_distances(self, other_gesture):
        res = np.zeros(3)
        for i in range(3):
            res[i] = np.linalg.norm(self.data[i], other_gesture.data[i])
        return res

    def get_total_distance(self, other_gesture):
        return sum(self.get_distances(other_gesture))

    """ For recalculating certain values in child Classes """
    def update_computed(self):
        pass


class FourierGesture(Gesture):
    def __init__(self, gesture_size=500, fourier_part=32, norm_constant=10000.0):
        Gesture.__init__(self, gesture_size)
        self.fourier_part = fourier_part
        self.norm_constant = norm_constant
        self.fourier = np.zeros((3, self.gesture_size)).astype(np.complex128)

    def update_computed(self):
        for i in range(3):
            self.fourier[i] = np.fft.fft(self.data[i])

    def get_distances(self, other_gesture):
        res = np.zeros(3)
        for i in range(3):
            res[i] = distance.cosine(
                abs(self.fourier[i][:self.gesture_size//self.fourier_part]),
                abs(other_gesture.fourier[i][:self.gesture_size//self.fourier_part]))
        return res


class GestureSet:
    def __init__(self):
        self.gestures = []
        # TODO add options from config like color, ok limit, name, hotkey etc. (it should be saved)

    def add_gesture(self, gesture):
        self.gestures.append(gesture)

    def update_gestures(self):
        for gesture in self.gestures:
            gesture.update_computed()

    def get_distance(self, challenge_gesture):
        return sum(map(lambda x: x.get_total_distance(challenge_gesture), self.gestures))


class MultiFourierDataStore:

    def __init__(self, gesture_set_config):
        self.gesture_sets = []
        for g in gesture_set_config:
            self.gesture_sets.append(GestureSet())
