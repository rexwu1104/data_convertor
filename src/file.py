from functools import partial, reduce
from pprint import pprint
import re

from .time import TimePoint
from .object import Circle, Slide, Spin, HitObject
from .difficulty import Difficulty

def reduce_map(cb, iterable, init):
    for item in iterable:
        result = cb(init, item)
        if init is None:
            init = result
            
        yield result

class File:
    content: str
    slots: ...
    need_keys = (
        'TimingPoints',
        'HitObjects',
        'Difficulty')
    diffculty_keys = (
        'SliderMultiplier',
        'SliderTickRate')
    
    def __init__(self, file_name: str) -> None:
        with open(file_name, 'r', encoding='utf-8') as ofile:
            self.content = ofile.readlines()
        
        self.__init()
        
    def __iter__(self):
        for object in self.objects:
            yield from object
            
    def __init(self):
        need_content = {}
        slot_re = re.compile('\[(.*)\]')
        curr_slot = ""
        need = False
        for line in self.content:
            if ms := slot_re.match(line):
                curr_slot = ms.group(1)
                if curr_slot in self.need_keys:
                    need_content[curr_slot] = []
                    need = True
                    continue
                else:
                    need = False

            if need and len(line.strip()):
                need_content[curr_slot].append(line.strip())
                
        need_content['Difficulty'] = filter(lambda i: len(i) and i.split(':')[0] in self.diffculty_keys, need_content['Difficulty'])
        time_points = tuple(reduce_map(lambda p, c: TimePoint(c.split(','), p), need_content['TimingPoints'], None))
        time_points = (*self.__create_time_point(time_points[0]), *time_points[1:])
        difficulty = Difficulty(dict(map(lambda i: i.split(':'), need_content['Difficulty'])))
        self.objects = [HitObject.from_source(line, time_points, difficulty) for line in need_content['HitObjects']]
        # Slide("287,287,18912,6,0,B|164:227|275:185|172:116|172:116|113:178,1,300".split(','), time_points, difficulty)
        # Slide("257,321,51020,2,0,P|297:266|266:129,2,200".split(','), time_points, difficulty)
        # print('-' * 80)
        # Slide("141,134,4641,2,0,P|102:181|99:237,2,100".split(','), time_points, difficulty)
        # Spin("256,192,9831,12,0,11128,0:0:0:0:".split(','))
        # return need_content

    def __create_time_point(self, point: TimePoint) -> tuple[TimePoint, TimePoint]:
        start, step, speed, ninherit = point
        first = [''] * 7
        second = first.copy()

        first[0] = '0'
        first[1] = str(step)
        first[2] = str(speed)
        first[6] = '1'
        second[0] = str(start)
        second[1] = '-100'
        second[2] = str(speed)
        second[6] = '0'

        first = TimePoint(first)
        return (first, TimePoint(second, first))

