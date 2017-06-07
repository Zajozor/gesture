from threading import Thread
from vispy import app
from .display import MultiFourierCanvas
from .data import MultiFourierDataStore, FourierGesture
from .computation import MultiFourierComputation, PredictionState
import pickle

#  Config
gesture_set_config = [
    {
        'name': '1',
        'hotkey': '1'
    }, {
        'name': '2',
        'hotkey': '2'
    }, {
        'name': '3',
        'hotkey': '3'
    }, {
        'name': '4',
        'hotkey': '4'
    }, {
        'name': '5',
        'hotkey': '5'
    }
]

gesture_size = 500


def entry_multi_fourier_display(q, _=None):
    data_store = MultiFourierDataStore(gesture_set_config)

    try:
        fh = open('D:\gestures.dat', 'rb')
        data_store = pickle.load(fh)
        fh.close()
    except Exception as e:
        print(e)
        print('Did not load saved data')

    current_gesture = FourierGesture()

    prediction_state = PredictionState(current_gesture, data_store)
    computation = MultiFourierComputation(prediction_state)

    th = Thread(target=computation.predict_from_queue, args=(q, ), daemon=True)
    th.start()

    c = MultiFourierCanvas(gesture_size,
                           q,
                           computation,
                           gesture_set_config,

                           keys='interactive',
                           always_on_top=False,
                           title='Multi Fourier',
                           position=(50, 150))

    c.show()
    app.run()
    try:
        fh = open('D:\gestures.dat', 'wb')
        pickle.dump(data_store, fh)
        fh.close()
    except Exception as e:
        print(e)
        print('did not save')

