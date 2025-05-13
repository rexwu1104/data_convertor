from __future__ import annotations
from typing import Optional

class TimePoint:
    ninherit: bool
    start: int
    step: float
    multiple: float
    bpm: int
    base_step: float
    speed: float
    
    def __init__(self, params: tuple[str, ...], prev: Optional[TimePoint] = None):
        self.ninherit = bool(int(params[6]))
        self.start = int(params[0])
        self.step = float(params[1])
        self.multiple = 1. if self.step > 0 else 1 / -self.step * 100
        self.bpm = int(1 / float(params[1]) * 1000 * 60 if self.ninherit else prev.bpm)
        self.base_step = self.step if self.ninherit else prev.base_step
        self.speed = int(params[2])
        
    def __repr__(self):
        return f'<TimePoint start: {self.start}, bpm: {self.bpm}, slide_speed: {self.multiple}>'
    
    def __iter__(self):
        yield from [self.start, self.step, self.speed, self.ninherit]