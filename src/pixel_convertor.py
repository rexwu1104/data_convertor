from math import floor
import pyautogui

from .pixel import Pixel

size = pyautogui.size()
class PixelConvertor:
    height = size.height * 0.8
    width = height // 0.75
    start = (size.width - width) // 2, (size.height - height) // 2 + int(height * 0.02)
    scale = height / 384
    
    @classmethod
    def set_size(cls, size: tuple[int, int]):
        cls.height = size[1] * 0.8
        cls.width = cls.height // 0.75
        cls.start = (size[0] - cls.width) // 2, (size[1] - cls.height) // 2 + int(cls.height * 0.02)
        cls.scale = cls.height / 384
    
    @classmethod
    def convert(cls, pixel):
        return floor((pixel.x * cls.scale) + cls.start[0]), floor((pixel.y * cls.scale) + cls.start[1])
    
# print(PixelConvertor.convert(Pixel(261, 300)))