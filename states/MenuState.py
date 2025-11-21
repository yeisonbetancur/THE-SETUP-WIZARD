from State import State
from ui.menu_classes import Button
import pygame

class MenuState(State):
    def enter(self):
        print("Entrando al menú")
        cx = self.game.pantalla.get_width() // 2
        self.btn_jugar = Button(cx - 100, 280, 200, 50, "JUGAR", self.game.fuente_chica)
        self.btn_opciones = Button(cx - 100, 350, 200, 50, "OPCIONES", self.game.fuente_chica)
        self.btn_salir = Button(cx - 100, 420, 200, 50, "SALIR", self.game.fuente_chica, (120, 50, 50), (180, 70, 70))
        self.botones = [self.btn_jugar, self.btn_opciones, self.btn_salir]
        
    def exit(self):
        print("Saliendo del menú")
        
    def handle_events(self, eventos):
        for e in eventos:
            if self.btn_jugar.clicked(e):
                self.game.change_state("jugando")
            elif self.btn_opciones.clicked(e):
                self.game.change_state("opciones")
            elif self.btn_salir.clicked(e):
                self.game.corriendo = False
                
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.botones:
            btn.update(mouse_pos)
            
    def draw(self, pantalla):
        pantalla.fill((30, 30, 30))
        titulo = self.game.fuente_grande.render("MI JUEGO", True, (255, 255, 255))
        pantalla.blit(titulo, (pantalla.get_width()//2 - titulo.get_width()//2, 150))
        for btn in self.botones:
            btn.draw(pantalla)