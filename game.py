import pygame
import cv2
from systems.gesture_detector import GestureDetector
from states import OptionsState, MenuState, PlayingState, PauseState



class Game:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("State Pattern con Gestos")
        self.clock = pygame.time.Clock()
        self.corriendo = True
        
        self.fuente_grande = pygame.font.Font(None, 74)
        self.fuente_chica = pygame.font.Font(None, 36)
        self.fuente_mini = pygame.font.Font(None, 24)
        
        # Configuraciones
        self.volumen = 0.5
        self.gestos_activos = True
        
        # Sistema de detección de gestos
        self.gesture_detector = GestureDetector()
        
        # Registro de estados
        self.states = {
            "menu": MenuState(self),
            "jugando": PlayingState(self),
            "pausa": PauseState(self),
            "opciones": OptionsState(self),
        }
        self.current_state = None
        self.change_state("menu")
        
    def set_resolution(self, ancho, alto):
        self.pantalla = pygame.display.set_mode((ancho, alto))
        
    def change_state(self, nombre):
        if self.current_state:
            self.current_state.exit()
        self.current_state = self.states[nombre]
        self.current_state.enter()
        
    def run(self):
        while self.corriendo:
            dt = self.clock.tick(60) / 1000
            eventos = pygame.event.get()
            
            for e in eventos:
                if e.type == pygame.QUIT:
                    self.corriendo = False
                    
            self.current_state.handle_events(eventos)
            self.current_state.update(dt)
            self.current_state.draw(self.pantalla)
            
            pygame.display.flip()
            
        # Limpiar recursos
        self.gesture_detector.detener_camara()
        cv2.destroyAllWindows()
        pygame.quit()

if __name__ == "__main__":
    juego = Game()
    juego.run()