from abc import ABC, abstractmethod

class State(ABC):
    def __init__(self, game):
        self.game = game
        
    @abstractmethod
    def enter(self):
        pass
        
    @abstractmethod
    def exit(self):
        pass
        
    @abstractmethod
    def handle_events(self, eventos):
        pass
        
    @abstractmethod
    def update(self, dt):
        pass
        
    @abstractmethod
    def draw(self, pantalla):
        pass