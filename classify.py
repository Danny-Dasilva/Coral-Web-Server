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

logger = logging.getLogger(__name__)








def print_results(inference_rate, results):
    print('\nInference (rate=%.2f fps):' % inference_rate)
    for label, score in results:
        print('  %s, score=%.2f' % (label, score))
    
        

def render_gen(args):
    acc = accumulator(size=args.window, top_k=args.top_k)
    acc.send(None)  # Initialize.

    fps_counter = utils.avg_fps_counter(30)

    engines, titles = utils.make_engines(args.model, ClassificationEngine)
    assert utils.same_input_image_sizes(engines)
    engines = itertools.cycle(engines)
    engine = next(engines)

    labels = utils.load_labels(args.labels)
    draw_overlay = True
    

    yield utils.input_image_size(engine)

    output = None
    while True:
        tensor, layout, command = (yield output)
        
        inference_rate = next(fps_counter)
        if draw_overlay:
            start = time.monotonic()
            results = engine.ClassifyWithInputTensor(tensor, threshold=args.threshold, top_k=args.top_k)
            
            inference_time = time.monotonic() - start
            
            results = [(labels[i], score) for i, score in results]
            # b =  [(score) for i, score in results]
            for i, score in results:
                score = score
            b = score * 100
            a = results
            
            results = acc.send(results)
            
            if args.print:
                print_results(inference_rate, results)

            title = titles[engine]
            output = overlay(title, results, inference_time, inference_rate, layout)


            # Confidence Values
            # print(a)
            # if b > 22:
            #     print(a, "Correct guess")
            # else:
            #     print(b,"threshold not met")
            
        else:
            output = None

        if command == 'o':
            draw_overlay = not draw_overlay
        elif command == 'n':
            engine = next(engines)

def add_render_gen_args(parser):
    parser.add_argument('--model', required=True,
                        help='.tflite model path')
    parser.add_argument('--labels', required=True,
                        help='label file path')
    parser.add_argument('--window', type=int, default=10,
                        help='number of frames to accumulate inference results')
    parser.add_argument('--top_k', type=int, default=1,
                        help='number of classes with highest score to display')
    parser.add_argument('--threshold', type=float, default=0.1,
                        help='class score threshold')
    parser.add_argument('--print', default=False, action='store_true',
                        help='Print inference results')

def main():
    run_app(add_render_gen_args, render_gen)

if __name__ == '__main__':
    main()
