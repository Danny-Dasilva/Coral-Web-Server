"""A demo which runs object classification on camera frames."""

# export TEST_DATA=/usr/lib/python3/dist-packages/edgetpu/test_data
#
# python3 -m edgetpuvision.classify \
#   --model ${TEST_DATA}/mobilenet_v2_1.0_224_inat_bird_quant.tflite \
#   --labels ${TEST_DATA}/inat_bird_labels.txt

import argparse
import collections
import itertools
import time
import logging

from edgetpu.classification.engine import ClassificationEngine

import svg
import utils
#from apps import run_app

logger = logging.getLogger(__name__)


    
        

def render_gen(args):
    

    fps_counter = utils.avg_fps_counter(30)

    engines, titles = utils.make_engines(args.model, ClassificationEngine)
    print(ClassificationEngine)
    print('engines1', engines)
    #assert utils.same_input_image_sizes(engines)
    engines = itertools.cycle(engines)
    engine = next(engines)

    
    draw_overlay = True
    
    
    yield utils.input_image_size(engine)
    
    
    while True:
        #tensor, layout, command = (yield output)
        
        inference_rate = next(fps_counter)
        if draw_overlay:
            start = time.monotonic()
       
        else:
            output = None

    

def add_render_gen_args(parser):
    parser.add_argument('--model', required=True,
                        help='.tflite model path')
    
    parser.add_argument('--window', type=int, default=10,
                        help='number of frames to accumulate inference results')
    parser.add_argument('--print', default=False, action='store_true',
                        help='Print inference results')

