import sys
import __main__
import logging

from logging.handlers import RotatingFileHandler

formatter = logging.Formatter(f'[%(asctime)s][%(levelname)s] %(message)s')

log = logging.getLogger('AutoSneknet')
log.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setFormatter(formatter)
console.setLevel(logging.ERROR)
log.addHandler(console)

file = RotatingFileHandler(__main__.__file__ + '.log', mode='a', maxBytes=5*1024*1024, backupCount=0, encoding=None, delay=0)
file.setFormatter(formatter)
file.setLevel(logging.DEBUG)
log.addHandler(file)
