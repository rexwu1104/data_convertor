class Difficulty:
    slider_mutiplier: float
    slider_tick_rate: float
    
    def __init__(self, data):
        self.slider_mutiplier = float(data['SliderMultiplier'])
        self.slider_tick_rate = float(data['SliderTickRate'])