import argparse
import logging
import signal

from camera import make_camera
from gstreamer import Display, run_gen
from streaming.server import StreamingServer

import svg

EMPTY_SVG = str(svg.Svg())

def run_server(add_render_gen_args, render_gen):
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--source',
                        help='/dev/videoN:FMT:WxH:N/D or .mp4 file or image file',
                        default='/dev/video0:YUY2:640x480:30/1')
    parser.add_argument('--bitrate', type=int, default=1000000,
                        help='Video streaming bitrate (bit/s)')
    parser.add_argument('--loop', default=False, action='store_true',
                        help='Loop input video file')

    add_render_gen_args(parser)
    args = parser.parse_args()

    gen = render_gen(args)
    
    camera = make_camera(args.source, next(gen), args.loop)
    assert camera is not None

    with StreamingServer(camera, args.bitrate) as server:
        def render_overlay(tensor, layout, command):
            # server.send_overlay(EMPTY_SVG)
            print('meme')

        camera.render_overlay = render_overlay
        signal.pause()

