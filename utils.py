import logging

logger = logging.getLogger('gesture')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(levelname)7s] %(asctime)-15s %(message)s')

file_handler = logging.FileHandler('data/op.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
