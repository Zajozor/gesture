import logging

FORMAT = '%(levelname)7s %(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

logger = logging.getLogger('gesture')
