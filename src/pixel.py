from math import sqrt

class Pixel:
    x: int
    y: int
    
    def __init__(self, x, y) -> None:
        self.x, self.y = x, y
        
    def __eq__(self, value: object) -> bool:
        return repr(self) == repr(value)
    
    def __mul__(self, value) -> "Pixel":
        return Pixel(self.x * value, self.y * value)
    
    def __rmul__(self, value) -> "Pixel":
        return self * value
    
    def __div__(self, value) -> "Pixel":
        return Pixel(self.x / value, self.y / value)
    
    def __add__(self, value) -> "Pixel":
        if isinstance(value, int):
            return Pixel(self.x + value, self.y + value)
        return Pixel(self.x + value.x, self.y + value.y)
    
    def __sub__(self, value) -> "Pixel":
        if isinstance(value, int):
            return Pixel(self.x - value, self.y - value)
        return Pixel(self.x - value.x, self.y - value.y)
    
    def __pow__(self, value) -> "Pixel":
        return Pixel(self.x ** value, self.y ** value)
        
    def __repr__(self) -> str:
        return f'({self.x}, {self.y})'
    
    def __iter__(self):
        yield self.x
        yield self.y
        
    def round(self):
        return Pixel(round(self.x), round(self.y))