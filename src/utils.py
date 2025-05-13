from __future__ import annotations
from .pixel import Pixel
from functools import cache
from itertools import islice
from math import floor, sqrt, cos, sin, atan2, pi
from scipy.special import comb
from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt

class AngelSequence:
    def __init__(self, angles) -> None:
        self.head = angles[0]
        self.check = angles[1]
        self.tail = angles[2]
        if self.head > self.check and self.check < self.tail:
            if self.head > self.tail:
                self.head -= 2 * pi
            else:
                self.tail -= 2 * pi
        elif self.head < self.check and self.check > self.tail:
            if self.head < self.tail:
                self.head += 2 * pi
            else:
                self.tail += 2 * pi
        
        a2b, b2c = abs(self.head - self.check), abs(self.check - self.tail)
        self.length = a2b + b2c
        self.steps = a2b / self.length, b2c / self.length
        
    def get_t(self, t):
        if t > self.steps[0]:
            return self.get_by_range((t - self.steps[0]) / self.steps[1], self.check, self.tail)
        else:
            return self.get_by_range(t / self.steps[0], self.head, self.check)
            
    def get_by_range(self, t, start, end):
        return start * (1 - t) + end * t

def until(action, iterable, cond):
    for item in iterable:
        if not cond(item):
            return
        
        yield action(item)
        
def window(seq, n=2):
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
        
    for elem in it:
        result = result[1:] + (elem,)
        yield result
        
def unique(iterable):
    prev = None
    for item in iterable:
        if item == prev:
            continue
        
        prev = item
        yield item
        
def split_same(indexable):
    prev = None
    prev_start = 0
    for i in range(len(indexable)):
        if indexable[i] == prev:
            yield indexable[prev_start:i]
            prev_start = i
            
        prev = indexable[i]
        
    if prev_start != i:
        yield indexable[prev_start:]
        
def b_curve(points: list[Pixel]):
    times = len(points)
    @cache
    def C(n, k):
        if n == k or k == 0: return 1
        
        return C(n - 1, k - 1) + C(n - 1, k)
        
    def wrapper(t):
        ans = Pixel(0, 0)
        for point, k, n in zip(points, range(times), range(times-1, -1, -1)):
            ans += C(times - 1, k) * (1 - t) ** n * (t ** k) * point
            
        # print(t, ans)
        return ans
    
    wrapper.length = times * 2
    return wrapper

def b_curve(points: list[Pixel], time):
    num_points = int(time * 60 // 1000) + 1
    points = iter(bezier_curve_evenly_spaced(points, num_points))
    def wrapper(_):
        point = next(points)
        return Pixel(point[0], point[1])

    wrapper.length = num_points
    return wrapper

def p_curve(points: tuple[Pixel, Pixel, Pixel]):
    [(x1, y1), (x2, y2), (x3, y3)] = points
    a = x1 - x2
    b = y1 - y2
    c = x1 - x3
    d = y1 - y3
    e = ((x1 ** 2 - x2 ** 2) - (y2 ** 2 - y1 ** 2)) / 2
    f = ((x1 ** 2 - x3 ** 2) - (y3 ** 2 - y1 ** 2)) / 2
    x = -((d * e - b * f) / (b * c - a * d))
    y = -((a * f - c * e) / (b * c - a * d))
    r = sqrt((points[0].x - x) ** 2 + (points[0].y - y) ** 2)
    
    # angles = tuple(atan2(point.y - y, point.x - x) for point in points)
    angles = tuple(atan2(point.y - y, point.x - x) for point in points)
    angles = tuple(angle if angle >= 0 else angle + 2 * pi for angle in angles)
    seq = AngelSequence(angles)
    
    # print(x, y, r)
    # print("Point Coordinates:", [(point.x, point.y) for point in points])
    # print("Calculated Angles:", angles)
    # print(angles)
    # print(points)
    def wrapper(t):
        t = seq.get_t(t)
        return Pixel(x + r * cos(t), y + r * sin(t))
    
    # pprint([wrapper(t) for t in np.linspace(0, 1, 30)])
    
    wrapper.length = r // 2
    return wrapper

def l_curve(points: tuple[Pixel, Pixel]):
    [(x1, y1), (x2, y2)] = points
    x, y = x2 - x1, y2 - y1
    
    def wrapper(t):
        return Pixel(x * t + x1, y * t + y1)
    
    wrapper.length = 2
    return wrapper

def split_time(control_points_list, total_duration):
    lengths = [estimate_length(cps) for cps in control_points_list]
    total_length = sum(lengths)
    weights = [length / total_length for length in lengths]
    durations = [total_duration * weight for weight in weights]
    return durations

def estimate_length(control_points, num_points=500):
    points = bezier_curve(control_points, num_points=num_points)
    length = sum(np.linalg.norm(np.array(points[i+1]) - np.array(points[i])) for i in range(num_points-1))
    return length

def bezier_curve(control_points, num_points=100):
    n = len(control_points) - 1
    t_values = np.linspace(0, 1, num_points)
    curve_points = []
    for t in t_values:
        point = np.zeros(2)
        for i, control_point in enumerate(control_points):
            bernstein_poly = comb(n, i) * (t**i) * ((1-t)**(n-i))
            point += bernstein_poly * np.array(list(control_point))
        curve_points.append(tuple(point))

    return curve_points

def bezier_curve_evenly_spaced(control_points, num_points=100):
    curve_points = bezier_curve(control_points, num_points=num_points*10)
    arc_length = np.zeros(len(curve_points))
    for i in range(1, len(curve_points)):
        arc_length[i] = arc_length[i-1] + np.linalg.norm(np.array(curve_points[i]) - np.array(curve_points[i-1]))

    interp_func = interp1d(arc_length, curve_points, axis=0)
    even_arc_length_values = np.linspace(arc_length[0], arc_length[-1], num_points)
    even_points = interp_func(even_arc_length_values)

    return [tuple(point) for point in even_points]

def calculate_length(wrappers):
    def single_length(wrapper):
        prev = None
        length: int = 0
        for t in np.linspace(0, 1, wrapper.length):
            point = wrapper(t)
            if prev is not None:
                length += np.sqrt(sum((point - prev) ** 2))
                
            prev = point
            
        return length
    
    return (*map(lambda w: single_length(w), wrappers),)

def calculate_points(wrappers, steps: tuple[float, ...]):
    points = []
    for wrapper, step in zip(wrappers, steps):
        if len(points): points.pop()
        points += [wrapper(t) for t in np.linspace(0, 1, floor(step))]
            
    return points

def draw_points(points: list[Pixel]):
    points = np.array([list(point) for point in points])
    
    plt.plot(points[:, 0], points[:, 1])
    plt.show()