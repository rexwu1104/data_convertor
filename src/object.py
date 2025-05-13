from __future__ import annotations
from enum import IntEnum
from math import ceil, pi, cos, sin
from functools import partial
from .pixel import Pixel
from .difficulty import Difficulty
from .time import TimePoint
from .utils import until, split_same, b_curve, p_curve, l_curve, calculate_length, calculate_points, draw_points, window, split_time, estimate_length

import numpy as np

class ObjectType(IntEnum):
    Circle = 0
    Slide = 1
    Spin = 2

class HitObject:
    ty: ObjectType
    times: list[int]
    points: list[Pixel]
    
    def __init__(self, type: ObjectType):
        self.ty = type
        
    def __repr__(self):
        return f'<{self.__class__.__name__} point="{self.points[0]} to {self.points[-1]}">'
    
    def __iter__(self):
        # print(self.points)
        yield from zip(self.points, self.times)
        
    @staticmethod
    def from_source(raw: str, time_points: list[TimePoint], difficulty: Difficulty) -> "HitObject":
        data = raw.split(',')
        ty = int(data[3])
        if ty & 1:
            return Circle(data)
        elif ty & 2:
            return Slide(data, time_points, difficulty)
        elif ty & 8:
            return Spin(data)
        
class Circle(HitObject):
    def __init__(self, data: list[str]):
        super().__init__(ObjectType.Circle)
        self.times = [int(data[2])]
        self.points = [Pixel(int(data[0]), int(data[1]))]
        
class Slide(HitObject):
    n: float = 1 / 60 * 1000
    "x, y, start_time, xxx, xxx, line_points, times, length"
    "0, 1, 2         , 3  , 4  , 5          , 6    , 7     "
    def __init__(self, data: list[str], time_points: list[TimePoint], difficulty: Difficulty):
        super().__init__(ObjectType.Slide)
        current: TimePoint = list(until(lambda i: i, time_points, lambda i: i.start <= int(data[2])))[-1]
        points_data = data[5].split('|')
        flag = points_data[0]
        points = [Pixel(int(data[0]), int(data[1]))] + list(map(lambda i: Pixel(*map(int, i.split(':'))), points_data[1:]))
        time = float(data[7]) / (100 * difficulty.slider_mutiplier * current.multiple) * current.base_step
        start_time = int(data[2])
        self.length = float(data[7])
        
        match flag:
            case 'B':
                self.init_B(points, start_time, time)
            case 'P':
                self.init_P(points, start_time, time)
            case 'L':
                self.init_L(points, start_time, time)
        
        temp_points = self.points.copy()
        temp_times = np.array(self.times, dtype=np.float64)
        reverse = True
        for _ in range(int(data[6]) - 1):
            if reverse:
                self.points.extend(list(reversed(temp_points))[1:])
            else:
                self.points.extend(temp_points[1:])
                
            temp_times += time
            self.times.extend(temp_times[1:])
            
            reverse = not reverse
            
        self.times = list(map(round, self.times))
        
    def init_B(self, points: list[Pixel], current: int, time_length: float):
        chunks = tuple(split_same(points))
        times = split_time(chunks, time_length)
        steps = [time / self.n for time in times] # need change
        wrappers = list(map(lambda params: b_curve(*params), zip(chunks, times)))
        full_points = list(point.round() for point in calculate_points(wrappers, steps))
        full_points_length = len(full_points)
        full_times = list(current + time_length * (i / full_points_length) for i in range(full_points_length + 1))
        
        self.points = full_points
        self.times = full_times
        
    def init_P(self, points: tuple[Pixel, Pixel, Pixel], current: int, time_length: float):
        if points[0] == points[2]:
            return self.init_L(points, current, time_length)
        elif points[0] == points[1]:
            return self.init_L(points[1:], current, time_length)
        elif points[1] == points[2]:
            return self.init_L(points[:-1], current, time_length)
        
        wrappers = [p_curve(points)]
        steps = (time_length / self.n,)
        full_points = list(point.round() for point in calculate_points(wrappers, steps))
        full_points_length = len(full_points)
        full_times = list(current + time_length * (i / full_points_length) for i in range(full_points_length + 1))
        
        self.points = full_points
        self.times = full_times
        
    def init_L(self, points: list[Pixel], current: int, time_length: float):
        chunks = [win for win in window(points, 2)]
        wrappers = list(map(l_curve, chunks))
        lengths = calculate_length(wrappers)
        full_length = sum(lengths)
        steps = tuple(length / full_length * time_length / self.n for length in lengths)
        full_points = list(point.round() for point in calculate_points(wrappers, steps))
        full_points_length = len(full_points)
        full_times = list(current + time_length * (i / full_points_length) for i in range(full_points_length + 1))
        
        self.points = full_points
        self.times = full_times
        
class Spin(HitObject):
    r: int = 44
    centor: Pixel = Pixel(256, 192)
    n: float = 1 / 60 * 1000
    cps: float = 477.26 / 120
    def __init__(self, data: list[str]):
        super().__init__(ObjectType.Spin)
        
        start = int(data[2])
        end = int(data[5])
        time = end - start
        
        trange = self.cps * time / 1000 * 2 * pi
        step = ceil(time / self.n)
        self.points = [Pixel(round(self.centor.x + self.r * cos(t)), round(self.centor.y + self.r * sin(t))) for t in reversed(np.linspace(0, trange, step))]
        self.times = [ceil(t) for t in np.linspace(start, end, step)]