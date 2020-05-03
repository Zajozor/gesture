import os
import pickle
import time

import h5py
import numpy as np


# Local config
class CN:
    DATA_FOLDER = '../data/gestures'
    SEPARATOR = '-'
    SKIP_SUFFIX = '.quit'
    DATA_PREFIX = 's-'
    SINGLE_LOAD_SESSIONS = {'single_gestures'}
    MULTI_LOAD_SESSIONS = {'multi_gestures', 'tutorial'}
    GESTURE_CUTOFF_LENGTH = 130
    GESTURE_CHANNEL_COUNT = 5 * 6
    CLASS_TO_INT = {
        '28_null': 0,
        5: 1, 6: 2, 7: 3, 8: 4, 9: 5,
        10: 6, 11: 7, 14: 8, 15: 9, 17: 10,

        '20_diag': 1, '21_square': 2, '22_right': 3, '23_left': 4,
        '24_up': 5, '25_down': 6, '26_cwise': 7, '27_ccwise': 8,
    }
    DATETIME_FILENAME_FORMAT = 's-%Y%m%d-%H%M%S'
    DEFAULT_USER_NAME = 'zajo'


def get_sessions_data(sessions):
    files = os.listdir(CN.DATA_FOLDER)
    all_data = {}
    instance_count = 0

    for file in files:
        if file.startswith(CN.DATA_PREFIX) and \
                len(file.split(CN.SEPARATOR)) == 3 and \
                not file.endswith(CN.SKIP_SUFFIX):

            path = f'{CN.DATA_FOLDER}/{file}'

            with open(path, 'rb') as data_file:
                data = pickle.load(data_file)

            if 'session' not in data or data['session'] not in sessions:
                continue

            all_data[file] = data
            for key in data:
                if type(data[key]) == np.ndarray and key in CN.CLASS_TO_INT:
                    instance_count += len(data[key])
    return all_data, instance_count


def preprocess_session_data(h5_name, sessions):
    with h5py.File(f'{h5_name}.h5', 'w') as h5f:
        all_data, instance_count = get_sessions_data(sessions)

        xs = h5f.create_dataset('x', (instance_count, CN.GESTURE_CUTOFF_LENGTH, CN.GESTURE_CHANNEL_COUNT),
                                dtype='float64')
        xs.attrs['channels'] = sum(
            [
                [f'acc{i}-x', f'acc{i}-y', f'acc{i}-z', f'gyro{i}-x', f'gyro{i}-y', f'gyro{i}-z']
                for i in range(1, 6)
            ], [])
        xs.attrs['d1'] = 'instance'
        xs.attrs['d2'] = 'time'
        xs.attrs['d3'] = 'channel'

        ys = h5f.create_dataset('y', (instance_count,), dtype=np.dtype([('class', np.int8)]))
        ys.attrs['d1'] = 'instance'

        metas = h5f.create_dataset('meta', (instance_count,), dtype=np.dtype(
            [('datetime', np.int32), ('length', np.int32), ('user', np.int32)]))
        metas.attrs['d1'] = 'instance'

        counter = 0
        user_counter = {}
        for session in all_data:
            session_data = all_data[session]
            session_datetime = int(time.mktime(time.strptime(session, CN.DATETIME_FILENAME_FORMAT)))

            user = session_data.get('name', None) or CN.DEFAULT_USER_NAME
            if user not in user_counter:
                user_counter[user] = len(user_counter)
            user_no = user_counter[user]

            for key in session_data:
                if type(session_data[key]) == np.ndarray:
                    if key not in CN.CLASS_TO_INT:
                        print(f'[DEBUG] Skipping instance {key} in {session}.')
                        continue

                    instances = session_data[key]
                    for instance in instances:
                        instance_data = instance[:CN.GESTURE_CUTOFF_LENGTH].reshape(-1, 30)
                        padded_data = np.pad(instance_data,
                                             ((0, CN.GESTURE_CUTOFF_LENGTH - instance_data.shape[0]), (0, 0)))
                        xs[counter] = padded_data
                        ys[counter] = CN.CLASS_TO_INT[key]
                        metas[counter] = (session_datetime, padded_data.shape[0], user_no)
                        counter += 1
        ys.attrs['classes'] = np.unique(ys).astype(np.int8)

        print('-' * 70)
        print(f'Completed {h5_name} with {counter} instances.')
        print('Class distribution:')
        print(np.histogram(ys['class'], bins=np.unique(ys['class']).shape[0])[0])
        print('User distribution:')
        print(np.histogram(metas['user'], bins=np.unique(metas['user']).shape[0])[0])
        print(user_counter)
        print('-' * 70)


if __name__ == '__main__':
    preprocess_session_data('single', CN.SINGLE_LOAD_SESSIONS)
    preprocess_session_data('multi', CN.MULTI_LOAD_SESSIONS)
