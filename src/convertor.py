import cv2
import json
import tqdm
import zipfile
import numpy as np
from .file import File
from .pixel import Pixel
from .pixel_convertor import PixelConvertor

class Convertor:
    def __init__(self, osu, osr, delay=0, size=(1280, 720)) -> None:
        self.file = File(osu)
        self.capture = cv2.VideoCapture(osr)
        self.size = size
        self.delay = delay
        
    def __iter__(self):
        PixelConvertor.set_size(self.size)
        n = 1 / 60 * 1000
        start = -self.delay
        prev_time = 0
        frames = 0
        def next():
            return self.capture.read()
        
        for position, time in self.file:
            if not self.capture.isOpened(): return
            while start + n * frames < time:
                _, frame = next()
                frames += 1
                pos = None
                if (time - prev_time) / n < 1.3 or (start + n * frames - time) / n > -0.3:
                    pos = position

                yield frame, pos

            prev_time = time

    def write(self, file):
        convert = PixelConvertor.convert
        writer = cv2.VideoWriter(file, cv2.VideoWriter_fourcc(*'mp4v'), 60, self.size)
        for frame, position in tqdm.tqdm(self):
            if position is not None:
                cv2.rectangle(frame, tuple(convert(position - 15)), tuple(convert(position + 15)), (127, 127, 127), 7)
                
            writer.write(frame)

        writer.release()

    def to_data(self, file):
        convert = PixelConvertor.convert
        positions = []
        clicks = []
        with zipfile.ZipFile(file, 'w') as zfile:
            prev = Pixel(256, 192)
            length = 0
            for i, (frame, curr) in tqdm.tqdm(enumerate(self)):
                _, png = cv2.imencode('.png', frame)
                zfile.writestr(f'images/{i}.png', png.tostring())
                if curr is None:
                    clicks.append(0)
                else:
                    clicks.append(1)

                if curr is None and prev is not None:
                    length += 1
                elif length != 0:
                    positions.extend([convert((prev + (curr - prev) * s).round()) for s in np.linspace(1 / length, 1, length)])
                    length = 0
                
                if curr is not None:
                    positions.append(convert(curr))
                    prev = curr

            if length != 0:
                positions.extend([convert((prev + (curr - prev) * s).round()) for s in np.linspace(1 / length, 1, length)])

            zfile.writestr('position.json', json.dumps(positions))
            zfile.writestr('click.json', json.dumps(clicks))

    @classmethod
    def from_file(cls, path):
        with open(f'convertors/{path}', 'r', encoding='utf-8') as cfile:
            rows = cfile.read().split('\n')

        params = {}
        for row in rows:
            key, *value = row.split('=')
            value = '='.join(value)

            match key:
                case 'size':
                    params[key] = tuple(map(int, value.split(',')))
                case 'delay':
                    params[key] = int(value)
                case _:
                    params[key] = value

        return cls(**params)
