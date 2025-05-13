import cv2
import time
import argparse

from src import Convertor, PixelConvertor

convert = PixelConvertor.convert
parser = argparse.ArgumentParser(
    prog='Osu Convertor',
    description='convert the video and ".osu" file to combine video or AI data')

parser.add_argument('cvt_file', metavar='convertor')
parser.add_argument('-w', '--write', metavar='output')
parser.add_argument('-c', '--convert', metavar='output')
parser.add_argument('-p', '--preview', action='store_const', const=True, default=False)

args = parser.parse_args()
convertor = Convertor.from_file(args.cvt_file)
if args.write is not None:
    print('writing mp4 to {}'.format(args.write))
    convertor.write(args.write)

if args.convert is not None:
    print('writing zip to {}'.format(args.convert))
    convertor.to_data(args.convert)

if args.preview:
    for frame, position in convertor:
        if position is not None:
            cv2.rectangle(frame, tuple(convert(position - 15)), tuple(convert(position + 15)), (127, 127, 127), 7)

        cv2.imshow('frame', frame)
        key = cv2.waitKey(0) & 0xff
        if key == 27:
            break
