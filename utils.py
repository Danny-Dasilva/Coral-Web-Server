import collections
import os
import re
import time

LABEL_PATTERN = re.compile(r'\s*(\d+)(.+)')


def input_image_size(engine):
    _, h, w, _ = engine.get_input_tensor_shape()
    return w, h

# def same_input_image_sizes(engines):
#     return len({input_image_size(engine) for engine in engines}) == 1

def avg_fps_counter(window_size):
    window = collections.deque(maxlen=window_size)
    prev = time.monotonic()
    yield 0.0  # First fps value.

    while True:
        curr = time.monotonic()
        window.append(curr - prev)
        prev = curr
        yield len(window) / sum(window)

