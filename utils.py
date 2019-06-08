import collections
import os
import re
import time

LABEL_PATTERN = re.compile(r'\s*(\d+)(.+)')

def load_labels(path):
    with open(path, 'r', encoding='utf-8') as f:
       lines = (LABEL_PATTERN.match(line).groups() for line in f.readlines())
       return {int(num): text.strip() for num, text in lines}


def input_image_size():
    w = 224
    h = 224
    return w, h


def avg_fps_counter(window_size):
    window = collections.deque(maxlen=window_size)
    prev = time.monotonic()
    yield 0.0  # First fps value.

    while True:
        curr = time.monotonic()
        window.append(curr - prev)
        prev = curr
        yield len(window) / sum(window)


