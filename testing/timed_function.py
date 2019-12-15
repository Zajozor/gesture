import time


def time_function(f):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        f(*args, **kwargs)
        t2 = time.time()
        print(f'Time elapsed in {f.__name__}: {(t2 - t1)*1000:.2f}ms')
    return wrapper
