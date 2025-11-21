from states.State import State
from ui.menu_classes import Button
import pygame

class PauseState(State):
    def enter(self):
        print("Juego pausado")
        cx = self.game.pantalla.get_width() // 2
        self.btn_continuar = Button(cx - 100, 280, 200, 50, "CONTINUAR", self.game.fuente_chica)
        self.btn_menu = Button(cx - 100, 350, 200, 50, "MENÚ", self.game.fuente_chica, (120, 50, 50), (180, 70, 70))
        self.botones = [self.btn_continuar, self.btn_menu]
        
        # Pausar detección de gestos
        self.game.gesture_detector.detener_camara()
        
    def exit(self):
        print("Reanudando juego")
        # Reanudar gestos si estaban activos
        if self.game.gestos_activos:
            self.game.gesture_detector.iniciar_camara()
            
    def handle_events(self, eventos):
        for e in eventos:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.game.change_state("jugando")
            if self.btn_continuar.clicked(e):
                self.game.change_state("jugando")
            elif self.btn_menu.clicked(e):
                self.game.change_state("menu")
                
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.botones:
            btn.update(mouse_pos)
            
    def draw(self, pantalla):
        overlay = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        pantalla.blit(overlay, (0, 0))
        
        texto = self.game.fuente_grande.render("PAUSA", True, (255, 255, 255))
        pantalla.blit(texto, (pantalla.get_width()//2 - texto.get_width()//2, 180))
        
        for btn in self.botones:
            btn.draw(pantalla)
